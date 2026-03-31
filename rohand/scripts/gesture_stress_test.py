import datetime
import logging
import os
import sys
import time
import concurrent.futures
from rohand.api.OHandSerialAPI import MAX_MOTOR_CNT
from rohand.rohand_manager import RohanManager
from rohand.rohand_common import OperateSharedData

# ==================== 日志配置 ====================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_folder = "./log"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

timestamp = str(int(time.time()))
current_date = time.strftime("%Y-%m-%d", time.localtime())
log_file_name = f'./log/GestureStressTest_log_{current_date}_{timestamp}.txt'

file_handler = logging.FileHandler(log_file_name, encoding='utf-8')
file_handler.setLevel(logging.INFO)

log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


# ==================== 手势压测类 ====================
class GestureStressTest:
    MODBUS_PROTOCOL = 0
    PEAK_CAN_PROTOCOL = 1
    FINGER_POS_TARGET_MAX_LOSS = 200
    action_interval = 1

    def __init__(self, protocol_type, port, device_id):
        self.protocol_type = protocol_type
        self.port = port
        self.device_id = device_id
        self.rohan_manager = RohanManager(protocol_type)
        self.rohan_manager.create_client(port=port)

        self.POS_MAX_LOSS = 200
        self.DEFAULT_SPEED = 255
        self.SIXTH_FINGER_MIN_POS = 728
        self.initial_gesture = [0, 0, 0, 0, 0, 728]

        # 28种手势定义
        self.fist_gesture = [[0, 62258, 62258, 62258, 62258, 728], [36044, 62258, 62258, 62258, 62258, 728]]
        self.mouse_gesture = [[32768, 0, 0, 0, 45875, 728], [32768, 7864, 0, 7864, 45875, 728]]
        self.key_gesture = [[0, 36044, 62258, 62258, 62258, 728], [42598, 36044, 62258, 62258, 62258, 728]]
        self.point_gesture = [[0, 0, 62258, 62258, 62258, 728], [52428, 0, 62258, 62258, 62258, 728]]
        self.column_gesture = [[52428, 0, 64880, 64880, 64880, 728], [52428, 36044, 64880, 64880, 64880, 728]]
        self.palm_gesture = [[26214, 16384, 16384, 16384, 19661, 728], [26214, 16384, 16384, 16384, 16384, 728]]
        self.salute_gesture = [[29491, 0, 0, 0, 0, 728], [29491, 0, 0, 0, 0, 728]]
        self.chopstick_gesture = [[16384, 19661, 62258, 62258, 62258, 728], [16384, 45875, 62258, 62258, 62258, 728]]
        self.power_gesture = [[0, 62258, 62258, 62258, 62258, 62258], [40000, 62258, 62258, 62258, 62258, 62258]]
        self.grasp_gesture = [[27525, 29491, 32768, 27525, 24903, 62258], [27525, 29491, 32768, 27525, 24903, 62258]]
        self.lift_gesture = [[0, 22937, 22937, 22937, 22937, 62258], [39321, 62258, 62258, 62258, 62258, 62258]]
        self.plate_gesture = [[0, 9830, 11141, 9830, 11141, 62258], [62258, 9830, 11141, 9830, 11141, 62258]]
        self.buckle_gesture = [[36044, 0, 55705, 55705, 55705, 728], [36044, 29491, 55705, 55705, 55705, 62258]]
        self.pinch_ic_gesture = [[29491, 0, 62258, 62258, 62258, 728], [29491, 32768, 62258, 62258, 62258, 728]]
        self.pinch_io_gesture = [[29491, 0, 0, 0, 0, 62258], [29491, 32768, 0, 0, 0, 62258]]
        self.pinch_tc_gesture = [[0, 29491, 62258, 62258, 62258, 62258], [32768, 29491, 62258, 62258, 62258, 62258]]
        self.pinch_to_gesture = [[0, 29491, 0, 0, 0, 62258], [32768, 29491, 0, 0, 0, 62258]]
        self.pinch_itc_gesture = [[0, 0, 62258, 62258, 62258, 728], [29491, 29491, 62258, 62258, 62258, 728]]
        self.tripod_ic_gesture = [[30801, 0, 0, 62258, 62258, 62258], [30801, 30146, 32768, 62258, 62258, 62258]]
        self.tripod_io_gesture = [[30801, 0, 0, 0, 0, 62258], [30801, 30146, 32768, 0, 0, 62258]]
        self.tripod_tc_gesture = [[0, 30146, 32768, 62258, 62258, 62258], [30801, 30146, 32768, 62258, 62258, 62258]]
        self.tripod_to_gesture = [[0, 30146, 32768, 0, 0, 62258], [30801, 30146, 32768, 0, 0, 62258]]
        self.tripod_itc_gesture = [[0, 0, 0, 62258, 62258, 62258], [30801, 30146, 32768, 62258, 62258, 62258]]
        self.gun_gesture = [[0, 0, 62258, 62258, 62258, 728], [0, 0, 62258, 62258, 62258, 728]]
        self.love_gesture = [[0, 0, 0, 62258, 62258, 728], [0, 0, 0, 62258, 62258, 728]]
        self.swear_gesture = [[0, 62258, 0, 0, 62258, 728], [0, 62258, 0, 0, 62258, 728]]
        self.victory_gesture = [[62258, 0, 0, 62258, 62258, 728], [62258, 0, 0, 62258, 62258, 728]]
        self.six_gesture = [[0, 62258, 62258, 62258, 0, 728], [0, 62258, 62258, 62258, 0, 728]]

        self.gestures = self._create_gesture_dict()

    def _create_gesture_dict(self):
        return {
            'fist': self.fist_gesture,
            'mouse': self.mouse_gesture,
            'key': self.key_gesture,
            'point': self.point_gesture,
            'column': self.column_gesture,
            'palm': self.palm_gesture,
            'salute': self.salute_gesture,
            'chopstick': self.chopstick_gesture,
            'power': self.power_gesture,
            'grasp': self.grasp_gesture,
            'lift': self.lift_gesture,
            'plate': self.plate_gesture,
            'buckle': self.buckle_gesture,
            'pinch_ic': self.pinch_ic_gesture,
            'pinch_io': self.pinch_io_gesture,
            'pinch_tc': self.pinch_tc_gesture,
            'pinch_to': self.pinch_to_gesture,
            'pinch_itc': self.pinch_itc_gesture,
            'tripod_ic': self.tripod_ic_gesture,
            'tripod_io': self.tripod_io_gesture,
            'tripod_tc': self.tripod_tc_gesture,
            'tripod_to': self.tripod_to_gesture,
            'tripod_itc': self.tripod_itc_gesture,
            'gun': self.gun_gesture,
            'love': self.love_gesture,
            'swear': self.swear_gesture,
            'victory': self.victory_gesture,
            'six': self.six_gesture
        }

    def do_gesture(self, gesture):
        time.sleep(self.action_interval)
        return self.rohan_manager.setFingerPos(gesture=gesture, device_id=self.device_id)

    def judge_if_hand_broken(self, gesture):
        current_pos = self.rohan_manager.getFingerPos(self.device_id)
        for i in range(MAX_MOTOR_CNT):
            if abs(current_pos[i] - gesture[i]) > self.FINGER_POS_TARGET_MAX_LOSS:
                return True
        return False

    def close(self):
        try:
            if self.rohan_manager:
                self.rohan_manager.client.disconnect()
        except Exception as e:
            logger.error(f"[{self.port}] 关闭异常: {e}")


# ==================== 工具函数 ====================
def build_gesture_result(timestamp, content, result, comment="无"):
    return {
        "timestamp": timestamp,
        "content": str(content),
        "result": result,
        "comment": comment
    }


def print_overall_result(overall_result):
    port_data = {}
    for item in overall_result:
        port = item.get("port")
        if not port:
            continue
        if port not in port_data:
            port_data[port] = []
        port_data[port].extend(item.get("gestures", []))

    for port, gestures in port_data.items():
        logger.info(f"Port: {port}")
        for g in gestures:
            logger.info(f"[测试时间:{g['timestamp']}] 手势:{g['content']} | 测试结果:{g['result']} | 备注:{g['comment']}")


# ==================== 单端口测试 ====================
def test_single_port(port, device_id):
    protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
    tester = GestureStressTest(protocol_type, port, device_id)
    port_result = {"port": port, "gestures": []}

    try:
        for name, gesture in tester.gestures.items():
            logger.info(f"[{port}] 执行 -> {name}")
            ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            stop_test, pause_test = OperateSharedData.read()
            # 每个手势前检查暂停/停止
            stop_test, pause_test = OperateSharedData.read()
            if stop_test:
                logger.info('测试已停止')
                break

            # 阻塞式暂停
            while pause_test:
                time.sleep(0.2)
                stop_test, pause_test = OperateSharedData.read()
                if stop_test:
                    break
            if stop_test:
                break
            # 执行手势
            for ges in gesture:
                tester.do_gesture(ges)

            # 回归初始位并判断
            tester.do_gesture(tester.initial_gesture)
            time.sleep(tester.action_interval)
            ok = not tester.judge_if_hand_broken(tester.initial_gesture)
            port_result["gestures"].append(build_gesture_result(ts, name, "通过" if ok else "不通过"))

    except Exception as e:
        logger.error(f"[{port}] 执行异常: {e}")
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        port_result["gestures"].append(build_gesture_result(ts, "异常", "不通过", str(e)))
    finally:
        tester.close()

    return port_result


# ==================== 主函数 ====================
def main(ports=None, devices_ids=None, aging_duration=1.5):
    if ports is None:
        ports = []
    if devices_ids is None:
        devices_ids = []

    test_title = "循环28个手势压测 | 标准：无异常、不脱线"
    final_result = "通过"
    overall_result = []
    SECONDS_PER_HOUR = 3600

    start_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info("------------------- 手势压测开始 -------------------")
    logger.info(f"开始时间: {start_time_str}")

    try:
        end_time = time.time() + aging_duration * SECONDS_PER_HOUR
        round_num = 0
        delay = 0.0
        while time.time() < end_time + delay:
            # 阻塞式检查暂停/停止
            stop_test, pause_test = OperateSharedData.read()
            if stop_test:
                logger.info('测试已停止')
                break

            # 真正的暂停：卡在这里，直到恢复或停止
            while pause_test:
                time.sleep(0.2)
                delay += 0.2
                stop_test, pause_test = OperateSharedData.read()
                if stop_test:
                    logger.info('测试已停止')
                    break
            if stop_test:
                break

            round_num += 1
            logger.info(f"\n========== 第 {round_num} 轮测试 ==========")
            round_result = "通过"

            # stop_test, pause_test = OperateSharedData.read()
            # if stop_test:
            #     logger.info('测试已停止')
            #     break
            #
            # if pause_test:
            #     logger.info('测试已暂停')
            #     time.sleep(0.1)
            #     delay += 0.1
            #     continue

            with concurrent.futures.ThreadPoolExecutor(max_workers=len(ports)) as executor:
                futures = [executor.submit(test_single_port, p, d) for p, d in zip(ports, devices_ids)]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    overall_result.append(res)
                    for g in res.get("gestures", []):
                        if g.get("result") != "通过":
                            round_result = final_result = "不通过"

            logger.info(f"第 {round_num} 轮结果: {round_result}")

    except Exception as e:
        logger.exception(f"测试异常: {e}")
        final_result = "不通过"

    end_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"\n------------------- 测试结束: {final_result} -------------------")
    logger.info(f"结束时间: {end_time_str}")

    print_overall_result(overall_result)
    return test_title, overall_result


# ==================== 入口 ====================
if __name__ == "__main__":
    main(ports=['PCAN_USBBUS1'], devices_ids=[2], aging_duration=0.01)