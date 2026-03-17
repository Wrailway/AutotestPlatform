#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import can
import configparser
from pymodbus.client import serial

# ==============================
# 一些通用功能实现
# ==============================
class RohanManager:
    # modbus：0，Can ：1
    protocol_tye =0
    MODBUS_PROTOCOL = 0X0
    PEAK_CAN_PROTOCOL = 0X1

    def __init__(self,protocol_tye):
        self.protocol_tye = protocol_tye

    def read_port_info(self):
        ports = None
        if self.protocol_tye == self.MODBUS_PROTOCOL:
            portInfos = serial.tools.list_ports.comports()
            ports = [portInfo.device for portInfo in portInfos if portInfo]
        else:
            available_configs = can.interface.detect_available_configs()
            peak_configs = [cfg for cfg in available_configs if cfg.get("channel", "").startswith("PCAN_USBBUS")]
            ports = [cfg["channel"] for cfg in peak_configs] if peak_configs else []

        return ports

    class ConfigReader:
        """读取配置文件config.ini的工具类"""

        def __init__(self, config_file_path):
            self.config_file_path = config_file_path
            self.config = configparser.ConfigParser()
            self.config.read(self.config_file_path, encoding='UTF-8')

        def get_value(self, section, key):
            """获取指定 section 和 key 对应的配置值"""
            try:
                return self.config.get(section, key)
            except (configparser.NoSectionError, configparser.NoOptionError):
                return None

        def get_section(self, section):
            """获取指定 section 下的所有配置项"""
            try:
                return dict(self.config.items(section))
            except configparser.NoSectionError:
                return None