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

# ==============================
# 日志配置（关键：让 logger.info 能打印）
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # 控制台输出
        logging.FileHandler("rohan_manager.log", encoding="utf-8")  # 日志文件
    ]
)
logger = logging.getLogger(__name__)

# ==============================
# 通用 CAN/Modbus 端口管理类
# ==============================
class RohanManager:
    # 协议类型常量（大写+注释，规范）
    MODBUS_PROTOCOL = 0    # 串口 Modbus
    PEAK_CAN_PROTOCOL = 1  # PEAK CAN 总线

    def __init__(self, protocol_type):
        """
        初始化端口管理器
        :param protocol_type: 协议类型（0=Modbus，1=PEAK CAN）
        """
        self.protocol_type = protocol_type
        logger.info(f"初始化管理器，协议类型：{self._get_protocol_name()}")

    def _get_protocol_name(self):
        """辅助函数：返回协议名称（日志友好）"""
        return "Modbus" if self.protocol_type == self.MODBUS_PROTOCOL else "PEAK CAN"

    def read_port_info(self):
        """
        读取可用端口列表
        :return: 端口列表（如 ["COM1", "COM2"] 或 ["PCAN_USBBUS1"]）
        """
        ports = []
        logger.info(f"开始读取 {self._get_protocol_name()} 端口...")

        try:
            if self.protocol_type == self.MODBUS_PROTOCOL:
                # ========== 修复：Modbus 串口读取 ==========
                port_infos = serial.tools.list_ports.comports()
                # 过滤有效串口（排除空设备、蓝牙串口等）
                ports = [
                    port_info.device
                    for port_info in port_infos
                    if port_info.device and "BLUETOOTH" not in port_info.description.upper()
                ]

            else:
                # ========== 修复：CAN 端口读取 ==========
                # 兼容 python-can 不同版本的接口
                try:
                    available_configs = can.interface.detect_available_configs()
                except AttributeError:
                    # 旧版本 python-can 兼容
                    available_configs = can.Bus._detect_available_configs()

                # 过滤 PEAK CAN 端口（PCAN_USBBUS 开头）
                peak_configs = [
                    cfg for cfg in available_configs
                    if cfg.get("channel", "").startswith("PCAN_USBBUS")
                ]
                ports = [cfg["channel"] for cfg in peak_configs] if peak_configs else []

            # 处理无端口场景
            if not ports:
                logger.warning(f"未检测到 {self._get_protocol_name()} 端口")
                ports = ["无可用端口"]  # 与前端逻辑对齐
            else:
                logger.info(f"检测到 {len(ports)} 个 {self._get_protocol_name()} 端口：{ports}")

        except Exception as e:
            # 捕获所有异常，避免崩溃
            logger.error(f"读取 {self._get_protocol_name()} 端口失败：{str(e)}", exc_info=True)
            ports = ["无可用端口"]

        return ports

    # ==============================
    # 配置文件读取内部类（保留+优化）
    # ==============================
    class ConfigReader:
        """读取 config.ini 配置文件的工具类（支持中文、异常处理）"""

        def __init__(self, config_file_path="config.ini"):
            self.config_file_path = config_file_path
            self.config = configparser.ConfigParser()
            # 读取配置文件（兼容不同编码）
            try:
                self.config.read(self.config_file_path, encoding='UTF-8')
                logger.info(f"成功加载配置文件：{self.config_file_path}")
            except FileNotFoundError:
                logger.error(f"配置文件不存在：{self.config_file_path}")
            except Exception as e:
                logger.error(f"读取配置文件失败：{str(e)}", exc_info=True)

        def get_value(self, section, key, default=None):
            """
            获取指定配置值
            :param section: 配置段
            :param key: 配置键
            :param default: 默认值（可选）
            :return: 配置值 / 默认值
            """
            try:
                return self.config.get(section, key, fallback=default)
            except Exception as e:
                logger.warning(f"获取配置 [{section}][{key}] 失败：{str(e)}")
                return default

        def get_section(self, section):
            """
            获取指定配置段的所有键值对
            :param section: 配置段
            :return: 字典 / None
            """
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
# 测试代码（验证功能）
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
    # 示例：读取 [CAN] 段的 baudrate 配置
    baudrate = config_reader.get_value("CAN", "baudrate", default="500000")
    print(f"\nCAN 波特率配置：{baudrate}")