import datetime
import logging
import concurrent.futures
import os
import sys
import time
from typing import List, Tuple

from rohand.api.OHandSerialAPI import MAX_MOTOR_CNT
from rohand.rohand_manager import RohanManager

# ==================== 日志配置 ====================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_folder = "./log"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

timestamp = str(int(time.time()))
current_date = time.strftime("%Y-%m-%d", time.localtime())
log_file_name = f'./log/MotorCurrentTest_log_{current_date}_{timestamp}.txt'

file_handler = logging.FileHandler(log_file_name, encoding='utf-8')
file_handler.setLevel(logging.INFO)

log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# ==================== 电机电流测试类 ====================
class MotorCurrentTest:
    MODBUS_PROTOCOL = 0
    PEAK_CAN_PROTOCOL = 1
    FINGER_POS_TARGET_MAX_LOSS = 32
    DEFAULT_SPEED = 255
    action_interval = 1

    def __init__(self, protocol_type, port, device_id):
        self.protocol_type = protocol_type
        self.port = port
        self.device_id = device_id
        self.rohan_manager = RohanManager(protocol_type=protocol_type)
        self.rohan_manager.create_client(port=port)

        self.max_average_times = 5
        self.initial_gesture = [[0,0,0,0,0,728], [0,0,0,0,0,728]]
        self.thumb_up_gesture = [[0,0,0,0,0,728], [0, 65535, 65535, 65535, 65535, 728]]
        self.thumb_bend_gesture = [[0,0,0,0,0,728], [65535, 0, 0, 0, 0, 728]]
        self.thumb_rotation_gesture = [[0,0,0,0,0,728], [0, 0, 0, 0, 0, 65535]]

        self.gestures = self.create_gesture_dict()

        self.collectMotorCurrents = {
            'thumb': [0.0, 0.0],
            'index': [0.0, 0.0],
            'middle': [0.0, 0.0],
            'third': [0.0, 0.0],
            'little': [0.0, 0.0],
            'thumb_root': [0.0, 0.0]
        }

        self.start_motor_currents = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.end_motor_currents = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def create_gesture_dict(self):
        return {
            '自然展开': self.initial_gesture,
            '四指弯曲': self.thumb_up_gesture,
            '大拇值弯曲': self.thumb_bend_gesture,
            '大拇指旋转到对掌位': self.thumb_rotation_gesture,
        }

    def checkCurrent(self, curs):
        if not curs:
            return False
        return all(0 <= c <= 100 for c in curs)

    def do_gesture(self, gesture):
        time.sleep(self.action_interval)
        return self.rohan_manager.setFingerPos(gesture=gesture, device_id=self.device_id)

    def get_motor_currents(self):
        sum_currents = [0.0] * MAX_MOTOR_CNT
        average_times = 3
        valid_count = 0

        for i in range(average_times):
            time.sleep(0.3)
            currents = self.rohan_manager.getFingerCurrent(device_id=self.device_id)

            if currents is None:
                logger.warning(f"[{self.port}] 第{i + 1}次采集电流返回None，已跳过")
                continue
            if len(currents) != MAX_MOTOR_CNT:
                logger.warning(f"[{self.port}] 电流数据长度不匹配，已跳过")
                continue

            for idx in range(MAX_MOTOR_CNT):
                sum_currents[idx] += currents[idx]
            valid_count += 1

        if valid_count == 0:
            return [0.0] * MAX_MOTOR_CNT  # 禁止返回None，防止UI解析/Excel导出崩溃

        return [round(total / valid_count, 2) for total in sum_currents]

    def collect_start_and_end_currents(self, ges='', current=[]):
        if not current:
            return

        if ges == '自然展开':
            self.start_motor_currents = current.copy()
        elif ges == '四指弯曲':
            self.end_motor_currents[1:5] = current[1:5]
        elif ges == '大拇值弯曲':
            self.end_motor_currents[0] = current[0]
        elif ges == '大拇指旋转到对掌位':
            self.end_motor_currents[5] = current[5]

    def collect_motor_currents(self):
        keys = list(self.collectMotorCurrents.keys())
        for i, key in enumerate(keys):
            self.collectMotorCurrents[key][0] = self.start_motor_currents[i]
            self.collectMotorCurrents[key][1] = self.end_motor_currents[i]

        logger.info(f'============ [{self.port}] 各电机始末电流 ============')
        for key, values in self.collectMotorCurrents.items():
            logger.info(f"[{key}] 起始: {values[0]} mA | 结束: {values[1]} mA")

    def close(self):
        try:
            if self.rohan_manager:
                self.rohan_manager.client.disconnect()
        except Exception as e:
            logger.error(f"[{self.port}] 关闭异常: {e}")

# ==================== 工具函数 ====================
def build_gesture_result(timestamp, result, motors_current, comment=""):
    return {
        "timestamp": timestamp,
        "content": str(motors_current),
        "result": result,
        "comment": comment
    }

# ==================== 单端口测试 ====================
def test_single_port(port, device_id):
    result = "通过"
    protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
    tester = MotorCurrentTest(protocol_type, port, device_id)
    port_result = {"port": port, "gestures": []}
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        for name, gesture in tester.gestures.items():
            logger.info(f"[{port}] 执行 -> {name}")
            if tester.do_gesture(gesture[0]) and tester.do_gesture(gesture[1]):
                time.sleep(tester.action_interval*3)
                currents = tester.get_motor_currents()
                logger.info(f"[{port}] 电流: {currents}")

                if not tester.checkCurrent(currents):
                    result = "不通过"
                    logger.error(f"[{port}] {name} 电流超限！")
                tester.collect_start_and_end_currents(ges=name, current=currents)
            else:
                result = "不通过"
                logger.error(f"[{port}] {name} 执行失败！")
        tester.collect_motor_currents()
        port_result["gestures"].append(build_gesture_result(ts, result, tester.collectMotorCurrents))
    except Exception as e:
        logger.exception(f"[{port}] 测试异常")
        result = "不通过"
        port_result["gestures"].append(build_gesture_result(ts, result, {}, f"异常：{e}"))
    finally:
        tester.close()
    return port_result

# ==================== 主函数 ====================
def main(ports: list = [], devices_ids: list = [], aging_duration: float = 0) -> Tuple[str, List]:
    test_title = "电机电流测试 | 标准：0~100mA"
    overall_result = []
    final_result = "通过"

    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("------------------- 电机电流测试开始 -------------------")
    logger.info(f"开始时间: {start_time}")

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(ports)) as executor:
            futures = [executor.submit(test_single_port, p, d) for p, d in zip(ports, devices_ids)]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                overall_result.append(res)
                for g in res["gestures"]:
                    if g["result"] != "通过":
                        final_result = "不通过"

    except Exception as e:
        logger.exception("测试异常")
        final_result = "不通过"

    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"------------------- 测试结束: {final_result} -------------------")
    logger.info(f"结束时间: {end_time}")

    return test_title, overall_result

# ==================== 入口 ====================
if __name__ == "__main__":
    main(ports=['PCAN_USBBUS1'], devices_ids=[2])