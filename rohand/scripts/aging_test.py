import os
import sys
import time
import datetime
import logging
import concurrent.futures
from rohand.api.OHandSerialAPI import MAX_MOTOR_CNT
from rohand.rohand_manager import RohanManager

from rohand.rohand_common import OperateSharedData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_folder = "./log"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

timestamp = str(int(time.time()))
current_date = time.strftime("%Y-%m-%d", time.localtime())
log_file_name = f'./log/AgingTest_log_{current_date}_{timestamp}.txt'

file_handler = logging.FileHandler(log_file_name, encoding='utf-8')
file_handler.setLevel(logging.INFO)

log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class Aging_test:
    MODBUS_PROTOCOL = 0
    PEAK_CAN_PROTOCOL = 1
    initial_gesture = [[26069, 31499, 36569, 32949, 28966, 62258], [0, 0, 0, 0, 0, 62258]]
    grasp_gesture = [[0, 31499, 36569, 32949, 28966, 62258], [26069, 31499, 36569, 32949, 28966, 62258]]
    FINGER_POS_TARGET_MAX_LOSS = 32
    ROH_FINGER_POS_TARGET0 = 1135
    ROH_FINGER_CURRENT0 = 1105
    DEFAULT_SPEED = 255
    action_interval  = 1

    def __init__(self, protocol_type, port, device_id):
        self.protocol_type = protocol_type
        self.port = port
        self.device_id = device_id
        self.rohan_manager = RohanManager(protocol_type=protocol_type)
        self.rohan_manager.create_client(port=port)

    def do_gesture(self, gesture):
        time.sleep(self.action_interval )
        return self.rohan_manager.setFingerPos(gesture=gesture, device_id=self.device_id)

    def judge_if_hand_broken(self, gesture):
        current_pos = self.rohan_manager.getFingerPos(self.device_id)
        for i in range(MAX_MOTOR_CNT):
            if abs(current_pos[i] - gesture[i]) > self.FINGER_POS_TARGET_MAX_LOSS:
                return True
        return False

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

    def close(self):
        try:
            if self.rohan_manager:
                self.rohan_manager.client.disconnect()
        except Exception as e:
            logger.error(f'异常关闭端口{e}')


def main(ports: list = [], devices_ids: list = [], aging_duration: float = 1.5):
    test_title = '老化测试报告'
    overall_result = []
    final_result = '通过'
    SECONDS_PER_HOUR = 3600
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f'------------------- 开始老化测试 <{start_time}> -------------------')
    logger.info('测试标准：无异常、不脱线、电流正常')

    try:
        end_time = time.time() + aging_duration * SECONDS_PER_HOUR
        round_num = 0
        delay = 0.0

        while time.time() < end_time + delay:
            # ====================== 优化点 1：轮询前先检查停止/暂停 ======================
            stop_test, pause_test = OperateSharedData.read()
            if stop_test:
                logger.info('测试已停止')
                break

            # ====================== 优化点 2：真正阻塞式暂停（直到恢复/停止） ======================
            while pause_test:
                time.sleep(0.2)
                delay += 0.2
                stop_test, pause_test = OperateSharedData.read()
                if stop_test:  # 暂停期间也能响应停止
                    logger.info('测试已停止')
                    break
            if stop_test:
                break

            round_num += 1
            logger.info(f'################ 第 {round_num} 轮测试开始 ################')
            result = '通过'
            round_results = []

            # stop_test,pause_test = OperateSharedData.read()
            # if stop_test:
            #     logger.info('测试已停止')
            #     break
            #
            # if pause_test:
            #     logger.info('测试已暂停')
            #     time.sleep(0.1)
            #     delay += 0.1
            #     continue


            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
                futures = [executor.submit(run_single_port, p, d) for p, d in zip(ports, devices_ids)]
                for future in concurrent.futures.as_completed(futures):
                    port_result = future.result()
                    round_results.append(port_result)
                    for g in port_result["gestures"]:
                        if g["result"] != "通过":
                            result = final_result = "不通过"

            overall_result.extend(round_results)
            logger.info(f'################ 第 {round_num} 轮结果：{result} ################\n')

    except Exception as e:
        final_result = '不通过'
        logger.error(f'错误：{e}')

    end_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'------------------- 测试结束：{final_result} <{end_time_str}> -------------------\n')
    print_overall_result(overall_result)
    return test_title, overall_result


def print_overall_result(overall_result):
    port_data = {}
    for item in overall_result:
        if item['port'] not in port_data:
            port_data[item['port']] = []
        port_data[item['port']].extend(item['gestures'])

    for port, gestures in port_data.items():
        logger.info(f'Port: {port}')
        for g in gestures:
            logger.info(
                f'[测试时间：{g["timestamp"]}] | 电流：{g["content"]} | 测试结果：{g["result"]} | 备注：{g["comment"]}')


def run_single_port(port, device_id):
    protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
    aging = Aging_test(protocol_type, port, device_id)
    port_result = {"port": port, "gestures": []}
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    currents = []

    try:
        # 抓握
        if aging.do_gesture(aging.grasp_gesture[0]) and aging.do_gesture(aging.grasp_gesture[1]):
            currents = aging.get_motor_currents()
            logger.info(f'[{port}] 抓握完成，电流：{currents}')
        else:
            port_result["gestures"].append(build_gesture_result(ts, "", "不通过", "执行失败"))
            return port_result

        # 展开,并判断手指有没有异常(如无法回到初始位置)
        if aging.do_gesture(aging.initial_gesture[0]) and aging.do_gesture(aging.initial_gesture[1]):
            time.sleep(Aging_test.action_interval)
            if not aging.judge_if_hand_broken(aging.initial_gesture[1]):
                res = build_gesture_result(ts, currents, "通过", "无")
            else:
                res = build_gesture_result(ts, "", "不通过", "手指异常，无法归位(或脱线）")
        else:
            res = build_gesture_result(ts, "", "不通过", "命令执行失败，请查看手是否连接异常")

        port_result["gestures"].append(res)

    except Exception as e:
        port_result["gestures"].append(build_gesture_result(ts, "", "不通过", f"异常：{e}"))
    finally:
        aging.close()
    # logger.info(f'[{port}] 测试完成')
    return port_result


def build_gesture_result(timestamp, content, result, comment):
    return {
        "timestamp": timestamp,
        "content": str(content),
        "result": result,
        "comment": comment
    }


if __name__ == "__main__":
    main(ports=['PCAN_USBBUS1'], devices_ids=[2], aging_duration=0.01)