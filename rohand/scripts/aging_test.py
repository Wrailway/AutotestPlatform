from rohand.api.OHandSerialAPI import MAX_MOTOR_CNT, HAND_RESP_SUCCESS
from rohand.rohand_manager import RohanManager


class Aging_test:
    MODBUS_PROTOCOL = 0  # 串口 Modbus
    PEAK_CAN_PROTOCOL = 1  # PEAK CAN 总线

    # 类属性初始化
    initial_gesture = [[26069, 31499, 36569, 32949, 28966, 62258], [0, 0, 0, 0, 0, 62258]]  # 自然展开手势
    grasp_gesture = [[0, 31499, 36569, 32949, 28966, 62258], [26069, 31499, 36569, 32949, 28966, 62258]]
    FINGER_POS_TARGET_MAX_LOSS = 32
    DEFAULT_SPEED = 255

    def __init__(self, protocol_type, port, device_id):
        """初始化方法 - 修复核心错误"""
        self.protocol_type = protocol_type
        self.port = port
        self.device_id = device_id

        # 1. 修复：创建管理器实例
        self.rohan_manager = RohanManager(protocol_type=self.protocol_type)

        # 2. 修复：增加异常捕获，避免连接失败导致崩溃
        self.client = None
        try:
            self.rohan_manager.create_client(port=self.port)
            self.client = self.rohan_manager.client.serialClient
            if not self.client:
                raise Exception("客户端创建失败")
        except Exception as e:
            print(f"设备连接失败 {port}：{str(e)}")

    def do_gesture(self, gesture):
        """执行手势 - 修复返回值和逻辑错误"""
        # 3. 修复：默认设置执行成功
        all_success = True

        if not self.client:
            print(f"错误：设备未连接，无法执行手势")
            return False

        for finger_id in range(MAX_MOTOR_CNT):
            remote_err = []
            err = self.client.HAND_SetFingerPos(
                self.device_id, finger_id,
                gesture[finger_id],  # 测试变量位置值
                self.DEFAULT_SPEED,  # 速度固定为默认值
                remote_err
            )

            # 4. 修复：检查每个手指的执行结果
            if err != HAND_RESP_SUCCESS:
                print(f"手指 {finger_id} 执行失败，错误码：{err}")
                all_success = False

        # 5. 修复：返回整体执行结果
        return all_success


def main():
    """主函数 - 修复调用逻辑"""
    try:
        # 创建老化测试实例（PEAK CAN 总线，端口PCAN_USBBUS1，设备ID2）
        aging = Aging_test(
            protocol_type=Aging_test.PEAK_CAN_PROTOCOL,
            port='PCAN_USBBUS1',
            device_id=2
        )

        # 检查设备是否连接成功
        if not aging.client:
            print("设备连接失败，退出测试")
            return

        # 6. 修复：分步执行手势并检查结果
        print("开始执行抓握手势第一阶段...")
        result1 = aging.do_gesture(gesture=aging.grasp_gesture[0])
        print(f"抓握手势第一阶段执行结果：{'成功' if result1 else '失败'}")

        print("开始执行抓握手势第二阶段...")
        result2 = aging.do_gesture(gesture=aging.grasp_gesture[1])
        print(f"抓握手势第二阶段执行结果：{'成功' if result2 else '失败'}")

        if result1 and result2:
            print("抓握手势执行完成！")
        else:
            print("抓握手势执行失败！")

    except Exception as e:
        print(f"程序执行异常：{str(e)}")
        # 打印详细错误堆栈
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()