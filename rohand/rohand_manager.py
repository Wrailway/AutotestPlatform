#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import can
import configparser
import logging
import sys

from pymodbus.client import ModbusSerialClient
from pymodbus import exceptions as modbus_exceptions
import serial.tools.list_ports

from api.can_client import CanClient
from api.modbus_client import ModbusClient
from rohand_common import (
    COL_PORT, COL_SOFTWARE_VERSION, COL_DEVICE_ID, COL_CONNECT_STATUS, COL_TEST_RESULT,
    STATUS_CONNECTED_UI, STATUS_NOT_CONNECTED, STATUS_UNKNOWN_DEVICE, STATUS_READ_FAIL,
    build_device_info,
)

logger = logging.getLogger(__name__)


def _detect_can_available_configs():
    """
    枚举本机 CAN 接口（依赖 PyPI 包 python-can，import 名仍为 can）。
    兼容不同版本的 API，避免 can 无 interface / 无 Bus 时盲目 fallback 报错。
    """
    # 1) 部分版本在包顶层提供
    fn = getattr(can, "detect_available_configs", None)
    if callable(fn):
        return fn()

    # 2) 常见：can.interface.detect_available_configs()
    interface = getattr(can, "interface", None)
    if interface is not None:
        fn = getattr(interface, "detect_available_configs", None)
        if callable(fn):
            return fn()

    # 3) 旧版内部接口
    bus_cls = getattr(can, "Bus", None)
    if bus_cls is not None:
        fn = getattr(bus_cls, "_detect_available_configs", None)
        if callable(fn):
            return fn()

    mod_file = getattr(can, "__file__", "?")
    raise RuntimeError(
        "未找到 python-can 的端口枚举 API（can 模块缺少 Bus/interface）。"
        f"当前加载的 can 来自: {mod_file}。"
        "请安装官方库: pip install -U python-can"
    )


# 全局单例：在界面根据配置确定 protocol 后创建，窗口销毁时释放
_global_manager = None
_config_cache_path = None
_cached_protocol_type = None

# 设备信息相关常量
ROH_FW_VERSION = 1001  # 固件版本寄存器地址
MAX_ID = 247
SUCCESS = 0x00


# ==============================
# 通用 CAN/Modbus 端口管理类
# ==============================
class RohanManager:
    # 协议类型常量
    MODBUS_PROTOCOL = 0  # 串口 Modbus
    PEAK_CAN_PROTOCOL = 1  # PEAK CAN 总线
    client = None

    # ---------- 配置读取方法 ----------
    @staticmethod
    def get_config_path() -> str:
        """获取配置文件路径"""
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建 config/config.ini 的路径
        config_path = os.path.join(current_dir, "config", "config.ini")
        return config_path

    @staticmethod
    def read_protocol_type_from_config(config_path: str = None) -> int:
        """从 config.ini 读取 [protocol_type] protocol，失败返回 0（Modbus）。"""
        # 如果没有提供路径，使用默认路径
        if not config_path:
            config_path = RohanManager.get_config_path()
        
        if not os.path.isfile(config_path):
            logger.warning(f"配置文件不存在：{config_path}，使用 Modbus 协议")
            return RohanManager.MODBUS_PROTOCOL
        
        cfg = configparser.ConfigParser()
        try:
            cfg.read(config_path, encoding="UTF-8")
            return int(cfg.get("protocol_type", "protocol", fallback="0").strip())
        except Exception as e:
            logger.warning(f"读取协议配置失败，使用 Modbus：{e}")
            return RohanManager.MODBUS_PROTOCOL

    @staticmethod
    def read_config_value(config_path: str = None, section: str = None, key: str = None, default=None):
        """读取任意配置项"""
        # 如果没有提供路径，使用默认路径
        if not config_path:
            config_path = RohanManager.get_config_path()
        
        if not os.path.isfile(config_path):
            logger.warning(f"配置文件不存在：{config_path}")
            return default
        
        if not section or not key:
            logger.warning("section 或 key 未提供")
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
        """读取整个 section 为 dict"""
        # 如果没有提供路径，使用默认路径
        if not config_path:
            config_path = RohanManager.get_config_path()
        
        if not os.path.isfile(config_path):
            logger.warning(f"配置文件不存在：{config_path}")
            return None
        
        if not section:
            logger.warning("section 未提供")
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

    @classmethod
    def get_global(cls):
        """返回当前全局 RohanManager，可能为 None。"""
        return _global_manager

    @classmethod
    def ensure_global(cls, protocol_type: int):
        """
        根据协议类型保证存在唯一全局实例；协议变化时先释放旧实例再新建。
        """
        global _global_manager
        if _global_manager is not None and _global_manager.protocol_type == int(protocol_type):
            return _global_manager
        cls.release_global()
        _global_manager = cls(int(protocol_type))
        logger.info("已创建全局 RohanManager（protocol=%s）", protocol_type)
        return _global_manager

    @classmethod
    def release_global(cls):
        """断开连接并销毁全局管理器（界面关闭时调用）。"""
        global _global_manager
        if _global_manager is None:
            return
        try:
            if getattr(_global_manager, "client", None):
                _global_manager.client.disconnect()
        except Exception as e:
            logger.warning(f"释放全局管理器时断开连接异常：{e}")
        _global_manager = None
        logger.info("已释放全局 RohanManager")

    # ---------------------------------------------------------------------------
    # 工具函数
    # ---------------------------------------------------------------------------
    @staticmethod
    def _ts():
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def fmt_log(message: str) -> str:
        """格式化日志消息"""
        return f"[{RohanManager._ts()}] {message}"

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
                # CAN 端口读取（须正确安装 python-can）
                available_configs = _detect_can_available_configs()

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

    def convert_version_format(self, registers):
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

    def get_firmware_version(self, id):
        """获取固件版本"""
        sw_version = '无法获取软件版本'
        if self.protocol_type == self.MODBUS_PROTOCOL:
            response = self.mb_receive_data_from_device(address=ROH_FW_VERSION, count=2, slave=id)
            if response is not None:
                sw_version = self.convert_version_format(response)
        else:
            major, minor, revision = [0], [0], [0]
            err, major_get, minor_get, revision_get = self.client.serialClient.HAND_GetFirmwareVersion(id, major, minor, revision, [])
            if err == SUCCESS:
                sw_version = f'v{major_get}.{minor_get}.{revision_get}'
        return sw_version

    def get_device_info(self, port):
        """获取设备信息"""
        connect_status = STATUS_CONNECTED_UI
        for device_id in range(2, MAX_ID):
            if self.protocol_type == self.MODBUS_PROTOCOL:
                response = self.mb_receive_data_from_device(ROH_FW_VERSION, 2, device_id)
                if response is not None:
                    sw_version = self.convert_version_format(response)
                    return build_device_info(
                        port=port,
                        sw_version=sw_version,
                        device_id=device_id,
                        connect_status=connect_status,
                    )
            else:
                major, minor, revision = [0], [0], [0]
                err, major_get, minor_get, revision_get = self.client.serialClient.HAND_GetFirmwareVersion(device_id, major, minor, revision, [])
                if err == SUCCESS:
                    sw_version = f'V{major_get}.{minor_get}.{revision_get}'
                    return build_device_info(
                        port=port,
                        sw_version=sw_version,
                        device_id=device_id,
                        connect_status=connect_status,
                    )
        return None

    def query_port_device_fields(self, port):
        """查询端口设备字段"""
        sw, dev_id, status = "-", "-", STATUS_NOT_CONNECTED
        try:
            if not self.create_client(port):
                return sw, dev_id, status
            info = self.get_device_info(port)
            if info:
                return (
                    str(info.get(COL_SOFTWARE_VERSION, "-")),
                    str(info.get(COL_DEVICE_ID, "-")),
                    str(info.get(COL_CONNECT_STATUS, STATUS_CONNECTED_UI)),
                )
            try:
                node_id = getattr(self, "node_id", 2)
                ver = self.get_firmware_version(node_id)
                if ver and "无法获取" not in ver:
                    return str(ver), str(node_id), STATUS_CONNECTED_UI
                return sw, dev_id, STATUS_UNKNOWN_DEVICE
            except Exception:
                return sw, dev_id, STATUS_UNKNOWN_DEVICE
        except Exception:
            return sw, dev_id, STATUS_READ_FAIL
        finally:
            try:
                if self and getattr(self, "client", None):
                    self.client.disconnect()
            except Exception:
                pass


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

    # 测试配置文件读取（使用 RohanManager 模块级 API）
    demo_cfg = os.path.join(os.path.dirname(__file__), "..", "config", "config.ini")
    demo_cfg = os.path.normpath(demo_cfg)
    baudrate = RohanManager.read_config_value(demo_cfg, "CAN", "baudrate", default="500000")
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