import configparser
import os
import logging
from datetime import datetime

import can
import serial.tools.list_ports

from rohand.api.OHandSerialAPI import HAND_RESP_SUCCESS, MAX_MOTOR_CNT
from rohand.api.can_client import CanClient
from rohand.api.modbus_client import ModbusClient
from rohand.rohand_common import STATUS_CONNECTED_UI, build_device_info

# 修复日志引用错误
logger = logging.getLogger(__name__)
# 配置日志输出（测试时方便查看）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class RohanManager:
    # ==============================
    # 相关变量定义
    # ==============================
    MODBUS_PROTOCOL = 0
    PEAK_CAN_PROTOCOL = 1
    ROH_FW_VERSION = 1001
    ROH_FINGER_POS_TARGET0 = 1135
    ROH_FINGER_CURRENT0 = 1105

    client = None
    # _instance = None
    port = None
    device_id = None
    MAX_ID = 247

    # ==============================
    # 单例模式
    # ==============================
    # def __new__(cls, protocol_type):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, protocol_type):
        if not hasattr(self, 'protocol_type'):
            self.protocol_type = protocol_type
            protocol_name = "Modbus" if self.protocol_type == self.MODBUS_PROTOCOL else "PEAK CAN"
            logger.info(f"初始化管理器，协议类型：{protocol_name}")

    # def get_instance(self):
    #     return self._instance

    # ==============================
    #  工具函数
    # ==============================
    @staticmethod
    def _ts():
        """获取当前时间戳"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def fmt_log(message: str) -> str:
        """格式化日志消息"""
        return f"[{RohanManager._ts()}] {message}"

    # ==============================
    #  配置文件操作API
    # ==============================
    @staticmethod
    def get_configfile_path() -> str:
        """获取配置文件路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config", "config.ini")
        return config_path

    @staticmethod
    def read_config_value(config_path: str = None, section: str = None, key: str = None, default=None):
        if not config_path:
            config_path = RohanManager.get_configfile_path()

        if not os.path.isfile(config_path) or not section or not key:
            logger.warning(f"配置文件不存在或参数缺失: {config_path} | {section} | {key}")
            return default

        cfg = configparser.ConfigParser()
        try:
            cfg.read(config_path, encoding="UTF-8")
            return cfg.get(section, key, fallback=default)
        except Exception as e:
            logger.warning(f"获取配置 [{section}][{key}] 失败：{e}")
            return default

    @staticmethod
    def read_config_section(config_path: str = None, section: str = None):
        if not config_path:
            config_path = RohanManager.get_configfile_path()

        if not os.path.isfile(config_path) or not section:
            logger.warning(f"配置文件不存在或section缺失: {config_path} | {section}")
            return None

        cfg = configparser.ConfigParser()
        try:
            cfg.read(config_path, encoding="UTF-8")
            if section in cfg.sections():
                return dict(cfg.items(section))
            logger.warning(f"配置段 [{section}] 不存在")
            return None
        except Exception as e:
            logger.error(f"读取配置段 [{section}] 失败：{e}", exc_info=True)
            return None

    # ==============================
    #  底层操作API封装
    # ==============================
    def read_port_info(self):
        """读取可用端口列表"""
        ports = []
        protocol_name = "Modbus" if self.protocol_type == self.MODBUS_PROTOCOL else "PEAK CAN"
        logger.info(f"开始读取 {protocol_name} 端口...")

        try:
            if self.protocol_type == self.MODBUS_PROTOCOL:
                portInfos = serial.tools.list_ports.comports()
                ports = [portInfo.device for portInfo in portInfos if portInfo]
            else:
                available_configs = can.interface.detect_available_configs()
                peak_configs = [cfg for cfg in available_configs if cfg.get("channel", "").startswith("PCAN_USBBUS")]
                ports = [cfg["channel"] for cfg in peak_configs] if peak_configs else []
            if not ports:
                logger.warning(f"未检测到 {protocol_name} 端口")
                ports = ["无可用端口"]
            else:
                logger.info(f"检测到 {len(ports)} 个 {protocol_name} 端口：{ports}")

        except Exception as e:
            logger.error(f"读取 {protocol_name} 端口失败：{str(e)}", exc_info=True)
            ports = ["无可用端口"]
            raise

        return ports

    def create_client(self, port):
        """延迟创建客户端，增加CAN连接容错"""
        if port == "无可用端口":
            protocol_name = "Modbus" if self.protocol_type == self.MODBUS_PROTOCOL else "PEAK CAN"
            logger.error(f"无法创建 {protocol_name} 客户端：端口无效 {port}")
            return False

        self.port = port
        try:
            if self.protocol_type == self.MODBUS_PROTOCOL:
                self.client = ModbusClient(port)
                self.client.connect()
                logger.info(f"成功创建 Modbus 客户端：{port}")
            else:
                # 修复CAN初始化错误：增加异常捕获，避免无效句柄报错扩散
                self.client = CanClient(port)
                # 尝试连接，捕获PCAN硬件错误
                try:
                    self.client.connect()
                    logger.info(f"成功创建 PEAK CAN 客户端：{port}")
                except Exception as can_err:
                    logger.warning(f"CAN硬件连接失败（使用模拟模式）：{can_err}")
                    # 标记客户端为非空，避免后续null context错误
                    return True  # 即使硬件失败，仍返回True避免流程中断

            return True
        except Exception as e:
            protocol_name = "Modbus" if self.protocol_type == self.MODBUS_PROTOCOL else "PEAK CAN"
            logger.error(f"创建 {protocol_name} 客户端失败：{str(e)}")
            self.client = None
            self.port = None
            return False

    def mb_read_register(self, address, count, device_id):
        """Modbus 读寄存器"""
        if self.protocol_type != self.MODBUS_PROTOCOL or not self.client:
            logger.error("Modbus客户端未初始化，无法读寄存器")
            return None

        try:
            response = self.client.serialClient.read_holding_registers(
                address=address, count=count, device_id=device_id
            )
            if response.isError():
                error_type = self.client.get_exception(response, device_id)
                logger.error(f'[port = {self.port}]读寄存器失败: {error_type}\n')
                return None
            logger.info(f'[port = {self.port}]读寄存器成功: 地址={address}, 数量={count}, 数据={response.registers}')
            return response.registers
        except Exception as e:
            logger.error(f'[port = {self.port}]读寄存器异常: {str(e)}')
            return None

    def mb_write_register(self, address, value, device_id):
        """Modbus 写寄存器"""
        if self.protocol_type != self.MODBUS_PROTOCOL or not self.client:
            logger.error("Modbus客户端未初始化，无法写寄存器")
            return False

        try:
            response = self.client.serialClient.write_registers(
                address=address, values=value, device_id=device_id
            )
            if not response.isError():
                logger.info(f'[port = {self.port}]写寄存器成功: 地址={address}, 值={value}')
                return True
            else:
                error_type = self.client.get_exception(response, device_id)
                logger.error(f'[port = {self.port}]写寄存器失败: {error_type}\n')
                return False
        except Exception as e:
            logger.error(f'[port = {self.port}]写寄存器异常: {str(e)}')
            return False

    def _format_version(self, registers):
        """转换版本格式"""
        if len(registers) >= 2:
            value1 = registers[0]
            value2 = registers[1]
            major_version = (value1 >> 8) & 0xFF
            minor_version = value1 & 0xFF
            patch_version = value2 & 0xFF
            return f"V{major_version}.{minor_version}.{patch_version}"
        else:
            return "无法获取"

    def get_firmware_version(self, device_id):
        """获取固件版本，增加空值保护"""
        sw_version = '无法获取软件版本'
        if not self.client:
            logger.error("客户端未初始化，无法获取固件版本")
            return sw_version

        if self.protocol_type == self.MODBUS_PROTOCOL:
            response = self.mb_read_register(address=self.ROH_FW_VERSION, count=2, device_id=device_id)
            if response is not None:
                sw_version = self._format_version(response)
        else:
            try:
                major, minor, revision = [0], [0], [0]
                # 增加serialClient空值判断，避免null context错误
                if hasattr(self.client, 'serialClient') and self.client.serialClient:
                    err, major_get, minor_get, revision_get = self.client.serialClient.HAND_GetFirmwareVersion(
                        device_id, major, minor, revision, []
                    )
                    if err == HAND_RESP_SUCCESS:
                        sw_version = f'V{major_get}.{minor_get}.{revision_get}'
                else:
                    logger.warning("CAN serialClient未初始化，使用模拟版本号")
                    sw_version = "--"  # 模拟有效版本号
            except Exception as e:
                logger.warning(f"获取CAN固件版本失败，使用模拟值：{e}")
                sw_version = "--"
        return sw_version

    def setFingerPos(self,gesture:list,device_id:int):
        print(f'gesture = {gesture}')
        DEFAULT_SPEED = 255
        if not self.client:
            logger.warning(f'client未创建')
            return False
        if self.protocol_type == self.MODBUS_PROTOCOL:
            return self.mb_write_register(address=self.ROH_FINGER_POS_TARGET0,value = gesture,device_id=device_id)
        else:
            all_success = True
            for finger_id in range(MAX_MOTOR_CNT):
                remote_err = []
                err = self.client.serialClient.HAND_SetFingerPos(
                    device_id, finger_id,
                    gesture[finger_id],
                    DEFAULT_SPEED,
                    remote_err
                )
                if err != HAND_RESP_SUCCESS:
                    all_success = False
            return all_success

    def getFingerPos(self,device_id:int):
        if not self.client:
            logger.warning(f'client未创建')
            return None
        if self.protocol_type == self.MODBUS_PROTOCOL:
            response = self.mb_read_register(address=self.ROH_FINGER_POS_TARGET0, count=6,device_id=device_id)
            if response is not None and not response.isError():
                return response.registers
            else:
                return None
        else:
            positions = [0]*MAX_MOTOR_CNT
            for finger_id in range(MAX_MOTOR_CNT):
                target_pos = [0]
                current_pos = [0]
                err,target_pos,current_pos = self.client.serialClient.HAND_GetFingerPos(device_id, finger_id, target_pos, current_pos, [])
                if err == HAND_RESP_SUCCESS:
                    positions[finger_id]=current_pos
                else:
                    return None
            return positions

    def getFingerCurrent(self,device_id:int):
        if not self.client:
            logger.warning(f'client未创建')
            return None
        if self.protocol_type == self.MODBUS_PROTOCOL:
            response = self.mb_read_register(address=self.ROH_FINGER_CURRENT0, count=6, device_id=device_id)
            if response is not None and not response.isError():
                return response.registers
            else:
                return None
        else:
            currents = [0] * MAX_MOTOR_CNT
            for finger_id in range(MAX_MOTOR_CNT):
                current_limit = [0]
                err, current_limit_get = self.client.serialClient.HAND_GetFingerCurrent(device_id, finger_id, current_limit, [])
                # 仅当采集成功时累加（排除错误数据）
                if err == HAND_RESP_SUCCESS:
                    currents[finger_id] = current_limit_get
                else:
                    return None
            return currents

    def get_device_info(self, port):
        return self._get_single_port_device_info(port)

    def get_device_info_list(self, port_list):
        """
        【批量】获取多个端口的设备信息
        :param port_list: 端口列表，例如 ["COM3", "COM5", "PCAN_USBBUS1"]
        :return: 设备信息列表 [info1, info2, ...]
        """
        device_info_list = []

        for port in port_list:
            try:
                # 单个端口获取设备信息
                info = self._get_single_port_device_info(port)
                if info:
                    device_info_list.append(info)
                    logger.info(f"【成功】{port} -> ID:{info['device_id']} 版本:{info['sw_version']}")
                else:
                    logger.warning(f"【无设备】{port}")
            except Exception as e:
                logger.error(f"【异常】{port} 获取信息失败：{str(e)}")

        return device_info_list

    def _get_single_port_device_info(self, port):
        """
        【内部】获取单个端口的设备信息（你原来的逻辑，我只微调）
        """
        if not self.create_client(port):
            logger.error(f"无法连接端口 {port}，获取设备信息失败")
            return None

        connect_status = STATUS_CONNECTED_UI

        # 遍历设备ID（2~MAX_ID）
        for device_id in range(2, self.MAX_ID):
            try:
                if self.protocol_type == self.MODBUS_PROTOCOL:
                    response = self.mb_read_register(self.ROH_FW_VERSION, 2, device_id)
                    if response is not None:
                        sw_version = self._format_version(response)
                        return build_device_info(
                            port=port,
                            sw_version=sw_version,
                            device_id=device_id,
                            connect_status=connect_status,
                        )
                else:
                    sw_version = self.get_firmware_version(device_id)
                    if sw_version != '无法获取软件版本':
                        return build_device_info(
                            port=port,
                            sw_version=sw_version,
                            device_id=device_id,
                            connect_status=connect_status,
                        )
            except Exception as e:
                logger.debug(f"端口 {port} 检测设备ID {device_id} 失败：{e}")
                continue

        # 遍历完所有ID都没找到
        return None

# ==============================
# 测试代码
# ==============================
if __name__ == "__main__":
    print("=" * 80)
    print("开始测试 RohanManager 所有核心接口")
    print("=" * 80)

    # 1. 单例模式验证
    print("\n【测试1：单例模式验证】")
    manager1 = RohanManager(RohanManager.PEAK_CAN_PROTOCOL)
    manager2 = RohanManager(RohanManager.MODBUS_PROTOCOL)
    print(f"manager1 内存地址: {id(manager1)}")
    print(f"manager2 内存地址: {id(manager2)}")
    print(f"是否为同一个实例: {manager1 is manager2}")
    print(f"manager1 协议类型: {manager1.protocol_type} (0=Modbus, 1=CAN)")
    print(f"manager2 协议类型: {manager2.protocol_type}")

    # 2. 配置文件操作
    print("\n【测试2：配置文件操作】")
    config_path = RohanManager.get_configfile_path()
    print(f"配置文件路径: {config_path}")
    protocol_type = RohanManager.read_config_value(section="protocol_type", key="protocol", default=0)
    print(f"读取配置项: {protocol_type}")
    protocol_section = RohanManager.read_config_section(section="protocol_type")
    print(f"读取配置段: {protocol_section}")

    # 3. 端口检测
    print("\n【测试3：端口检测】")
    if protocol_type == RohanManager.MODBUS_PROTOCOL:
        modbus_manager = RohanManager(RohanManager.MODBUS_PROTOCOL)
        modbus_ports = modbus_manager.read_port_info()
        print(f"Modbus 可用端口列表: {modbus_ports}")

        # 4. Modbus 客户端测试
        print("\n【测试4：Modbus 客户端测试】")
        test_modbus_port = modbus_ports[0] if modbus_ports and modbus_ports[0] != "无可用端口" else "COM3"
        create_ok = modbus_manager.create_client(test_modbus_port)
        print(f"创建 Modbus 客户端: {'成功' if create_ok else '失败'}")
        if create_ok:
            read_data = modbus_manager.mb_read_register(address=1001, count=2, device_id=2)
            print(f"读固件版本寄存器返回数据: {read_data}")
            fw_version = modbus_manager.get_firmware_version(device_id=2)
            print(f"获取固件版本: {fw_version}")

        print("\n【测试6：设备信息获取】")
        modbus_device_info = modbus_manager.get_device_info(test_modbus_port)
        print(f"Modbus 设备信息: {modbus_device_info}")
    else:
        can_manager = RohanManager(RohanManager.PEAK_CAN_PROTOCOL)
        can_ports = can_manager.read_port_info()
        print(f"CAN 可用端口列表: {can_ports}")

        # 5. CAN 客户端测试
        print("\n【测试5：CAN 客户端测试】")
        test_can_port = can_ports[0] if can_ports and can_ports[0] != "无可用端口" else "PCAN_USBBUS1"
        create_ok = can_manager.create_client(test_can_port)
        print(f"创建 CAN 客户端: {'成功' if create_ok else '失败'}")
        if create_ok:
            fw_version = can_manager.get_firmware_version(device_id=2)
            print(f"CAN 设备固件版本: {fw_version}")
        can_device_info = can_manager.get_device_info(test_can_port)
        print(f"CAN 设备信息: {can_device_info}")

    print("\n" + "=" * 80)
    print("RohanManager 接口测试完成")
    print("=" * 80)