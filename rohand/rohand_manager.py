#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import can
import configparser
import logging
import sys

# 修复 pymodbus 串口导入路径
from pymodbus.client import ModbusSerialClient
from pymodbus import exceptions as modbus_exceptions
# 正确的串口列表读取模块
import serial.tools.list_ports

from rohand.can_client import CanClient
from rohand.modbus_client import ModbusClient

# ==============================
# 日志配置
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("rohan_manager.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


# ==============================
# 通用 CAN/Modbus 端口管理类
# ==============================
class RohanManager:
    # 协议类型常量
    MODBUS_PROTOCOL = 0  # 串口 Modbus
    PEAK_CAN_PROTOCOL = 1  # PEAK CAN 总线
    client = None

    def __init__(self, protocol_type):
        """
        初始化端口管理器
        :param protocol_type: 协议类型（0=Modbus，1=PEAK CAN）
        """
        self.protocol_type = protocol_type
        self.port = None  # 当前端口（初始化时为空）
        self.node_id = 2  # 默认从站地址
        self.client = None  # 客户端延迟初始化（避免传入None端口）
        logger.info(f"初始化管理器，协议类型：{self._get_protocol_name()}")

    def _get_protocol_name(self):
        """辅助函数：返回协议名称"""
        return "Modbus" if self.protocol_type == self.MODBUS_PROTOCOL else "PEAK CAN"

    def create_client(self, port):
        """
        延迟创建客户端（关键修正：避免初始化时传入None端口）
        :param port: 具体端口号（如 COM1 / PCAN_USBBUS1）
        """
        if port == "无可用端口":
            logger.error(f"无法创建客户端：端口无效 {port}")
            return False

        self.port = port
        try:
            if self.protocol_type == self.MODBUS_PROTOCOL:
                self.client = ModbusClient(port)  # 创建Modbus客户端
                self.client.connect()  # 建立连接
            else:
                self.client = CanClient(port)  # 创建CAN客户端
                self.client.connect()  # 建立连接
            logger.info(f"成功创建 {self._get_protocol_name()} 客户端：{port}")
            return True
        except Exception as e:
            logger.error(f"创建 {self._get_protocol_name()} 客户端失败：{str(e)}")
            self.client = None
            self.port = None
            return False

    def read_port_info(self):
        """
        读取可用端口列表
        :return: 端口列表（如 ["COM1", "COM2"] 或 ["PCAN_USBBUS1"]）
        """
        ports = []
        logger.info(f"开始读取 {self._get_protocol_name()} 端口...")

        try:
            if self.protocol_type == self.MODBUS_PROTOCOL:
                # Modbus 串口读取
                port_infos = serial.tools.list_ports.comports()
                ports = [
                    port_info.device
                    for port_info in port_infos
                    if port_info.device and "BLUETOOTH" not in port_info.description.upper()
                ]

            else:
                # CAN 端口读取
                try:
                    available_configs = can.interface.detect_available_configs()
                except AttributeError:
                    available_configs = can.Bus._detect_available_configs()

                peak_configs = [
                    cfg for cfg in available_configs
                    if cfg.get("channel", "").startswith("PCAN_USBBUS")
                ]
                ports = [cfg["channel"] for cfg in peak_configs] if peak_configs else []

            if not ports:
                logger.warning(f"未检测到 {self._get_protocol_name()} 端口")
                ports = ["无可用端口"]
            else:
                logger.info(f"检测到 {len(ports)} 个 {self._get_protocol_name()} 端口：{ports}")

        except Exception as e:
            # 同时写入日志文件，并让上层 UI 能拿到具体错误信息
            logger.error(f"读取 {self._get_protocol_name()} 端口失败：{str(e)}", exc_info=True)
            # 统一返回“无可用端口”，并把异常抛给调用方（例如 PortRefreshThread），
            # 这样主窗口可以在“动态日志输出区”显示详细错误。
            ports = ["无可用端口"]
            raise

        return ports

    # ==============================
    # 补充 Modbus 写寄存器函数（修正调用逻辑）
    # ==============================
    def mb_send_cmd_to_device(self, address, value, slave=None):
        """
        向指定的寄存器地址写入数据。
        :param address: 要写入的寄存器地址。
        :param value: 要写入的值。
        :param slave: 从站地址（默认使用self.node_id）
        :return: 如果写入成功则返回True，否则返回False。
        """
        # 前置校验
        if self.protocol_type != self.MODBUS_PROTOCOL or not self.client:
            logger.error("Modbus客户端未初始化，无法写寄存器")
            return False

        slave_id = slave if slave is not None else self.node_id

        try:
            # 适配当前 ModbusSerialClient 接口：
            # 本工程统一使用 device_id 作为从站地址参数（与 OHandSerialAPI / ModbusClient 保持一致）
            response = self.client.serialClient.write_registers(
                address=address,
                values=value,
                device_id=slave_id
            )
            if not response.isError():
                logger.info(f'[port = {self.port}]写寄存器成功: 地址={address}, 值={value}')
                return True
            else:
                # 调用ModbusClient自带的异常解析函数
                error_type = self.client.get_exception(response, slave_id)
                logger.error(f'[port = {self.port}]写寄存器失败: {error_type}\n')
                return False
        except Exception as e:
            logger.error(f'[port = {self.port}]写寄存器异常: {str(e)}')
            return False

    # ==============================
    # 补充 Modbus 读寄存器函数（修正调用逻辑）
    # ==============================
    def mb_receive_data_from_device(self, address, count, slave=None):
        """
        从指定的寄存器地址读取数据。
        :param address: 要读取的寄存器地址。
        :param count: 要读取的寄存器数量。
        :param slave: 从站地址（默认使用self.node_id）
        :return: 成功返回寄存器值列表，失败返回None。
        """
        # 前置校验
        if self.protocol_type != self.MODBUS_PROTOCOL or not self.client:
            logger.error("Modbus客户端未初始化，无法读寄存器")
            return None

        slave_id = slave if slave is not None else self.node_id
        response = None

        try:
            # 适配当前 ModbusSerialClient 接口：
            # 本工程统一使用 device_id 作为从站地址参数（与 OHandSerialAPI / ModbusClient 保持一致）
            response = self.client.serialClient.read_holding_registers(
                address=address,
                count=count,
                device_id=slave_id
            )
            if response.isError():
                error_type = self.client.get_exception(response, slave_id)
                logger.error(f'[port = {self.port}]读寄存器失败: {error_type}\n')
                return None
            logger.info(f'[port = {self.port}]读寄存器成功: 地址={address}, 数量={count}, 数据={response.registers}')
            return response.registers
        except Exception as e:
            logger.error(f'[port = {self.port}]读寄存器异常: {str(e)}')
            return None

    # ==============================
    # 获取软件版本号
    # ==============================

    def get_firmware_version(self, id):
        ROH_FW_VERSION = 1001  # 固件版本寄存器地址
        SUCCESS = 0x00
        sw_version = '无法获取软件版本'
        if self.protocol_type == self.MODBUS_PROTOCOL:
            response = self.mb_receive_data_from_device(address=ROH_FW_VERSION, count=2, slave=id)
            if response is not None:
                sw_version = self.convert_version_format(response)

        else:
            major, minor, revision = [0], [0], [0]
            err, major_get, minor_get, revision_get = self.client.serialClient.HAND_GetFirmwareVersion(id, major, minor,
                                                                                                      revision, [])
            if err == SUCCESS:
                sw_version = f'v{major_get}.{minor_get}.{revision_get}'
        return sw_version


    def convert_version_format(self, registers):
        if len(registers) >= 2:
            value1 = registers[0]
            value2 = registers[1]
            major_version = (value1 >> 8) & 0xFF
            minor_version = value1 & 0xFF
            patch_version = value2 & 0xFF
            return f"V{major_version}.{minor_version}.{patch_version}"
        else:
            return "无法获取"

    def get_device_info(self, port):
        ROH_FW_VERSION = 1001  # 固件版本寄存器地址
        MAX_ID = 247
        SUCCESS = 0x00
        STR_PORT = '端口号'
        STR_SOFTWARE_VERSION = '软件版本'
        STR_DEVICE_ID = '设备ID'
        STR_CONNECT_STATUS = '连接状态'
        STR_TEST_RESULT = '测试结果'
        for id in range(2, MAX_ID):
            if self.protocol_type == self.MODBUS_PROTOCOL:
                response = self.mb_receive_data_from_device(ROH_FW_VERSION, 2, id)
                if response is not None:
                    sw_version = self.convert_version_format(response)
                    node_id = id
                    connect_status = '已连接'
                    return {
                        STR_PORT: port,
                        STR_SOFTWARE_VERSION: sw_version,
                        STR_DEVICE_ID: node_id,
                        STR_CONNECT_STATUS: connect_status,
                        STR_TEST_RESULT: '--'
                    }
            else:
                major, minor, revision = [0], [0], [0]
                err, major_get, minor_get, revision_get = self.client.serialClient.HAND_GetFirmwareVersion(id, major, minor,
                                                                                                      revision, [])
                if err == SUCCESS:
                    sw_version = f'V{major_get}.{minor_get}.{revision_get}'
                    node_id = id
                    connect_status = '已连接'
                    return {
                        STR_PORT: port,
                        STR_SOFTWARE_VERSION: sw_version,
                        STR_DEVICE_ID: node_id,
                        STR_CONNECT_STATUS: connect_status,
                        STR_TEST_RESULT: '--'
                    }
        return None

    # ==============================
    # 配置文件读取内部类（保留原代码）
    # ==============================
    class ConfigReader:
        """读取 config.ini 配置文件的工具类"""

        def __init__(self, config_file_path="config.ini"):
            self.config_file_path = config_file_path
            self.config = configparser.ConfigParser()
            try:
                self.config.read(self.config_file_path, encoding='UTF-8')
                logger.info(f"成功加载配置文件：{self.config_file_path}")
            except FileNotFoundError:
                logger.error(f"配置文件不存在：{self.config_file_path}")
            except Exception as e:
                logger.error(f"读取配置文件失败：{str(e)}", exc_info=True)

        def get_value(self, section, key, default=None):
            try:
                return self.config.get(section, key, fallback=default)
            except Exception as e:
                logger.warning(f"获取配置 [{section}][{key}] 失败：{str(e)}")
                return default

        def get_section(self, section):
            try:
                if section in self.config.sections():
                    return dict(self.config.items(section))
                else:
                    logger.warning(f"配置段 [{section}] 不存在")
                    return None
            except Exception as e:
                logger.error(f"读取配置段 [{section}] 失败：{str(e)}", exc_info=True)
                return None


# ==============================
# 测试代码
# ==============================
if __name__ == "__main__":
    # 测试 Modbus 端口读取
    modbus_manager = RohanManager(RohanManager.MODBUS_PROTOCOL)
    modbus_ports = modbus_manager.read_port_info()
    print(f"\nModbus 可用端口：{modbus_ports}")

    # 测试 PEAK CAN 端口读取
    can_manager = RohanManager(RohanManager.PEAK_CAN_PROTOCOL)
    can_ports = can_manager.read_port_info()
    print(f"PEAK CAN 可用端口：{can_ports}")

    # 测试配置文件读取
    config_reader = RohanManager.ConfigReader()
    baudrate = config_reader.get_value("CAN", "baudrate", default="500000")
    print(f"CAN 波特率配置：{baudrate}")

    # 测试 Modbus 客户端创建和读写（可选）
    if modbus_ports and modbus_ports[0] != "无可用端口":
        modbus_manager.create_client(modbus_ports[0])
        # 测试写寄存器
        write_ok = modbus_manager.mb_send_cmd_to_device(address=1115, value=[123])
        print(f"写寄存器结果：{write_ok}")
        # 测试读寄存器
        read_data = modbus_manager.mb_receive_data_from_device(address=1115, count=2)
        print(f"读寄存器结果：{read_data}")


    #测试can客户端创建和读写
    if can_ports and can_ports[0]!= "无可用端口":
        can_manager.create_client(can_ports[0])
        if can_manager.client:
            # 测试读寄存器
            self_test_level = [0]
            err, self_test_level_get = can_manager.client.serialClient.HAND_GetSelfTestLevel(2, self_test_level, [])
            print(f"读寄存器结果：{self_test_level_get}")
            # 测试写寄存器
            remote_err = []
            err2 = can_manager.client.serialClient.HAND_SetSelfTestLevel(2, 2, remote_err)
            print(f"写寄存器结果：{err2}")