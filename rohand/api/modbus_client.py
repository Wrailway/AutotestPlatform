#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modbus 协议客户端实现
继承抽象接口 ABSApiClient，完成串口 Modbus 连接、断开、寄存器读写、错误解析等封装
"""
import logging
import time
from typing import Optional, List

from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from rohand.api.OHandSerialAPI import OHandSerialAPI
from rohand.api.abs_api_client import ABSApiClient

# 兼容 serial 模块导入
try:
    import serial.tools.list_ports
except Exception:
    serial = None

# ==============================
# 日志配置
# ==============================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ==============================
# Modbus 协议客户端实现
# ==============================
class ModbusClient(ABSApiClient):
    """
    Modbus RTU 串口通信客户端
    实现连接、断开、端口扫描、错误解析、底层接口兼容封装
    """

    # 客户端对象
    serialClient = None
    _ohand_api: Optional[OHandSerialAPI] = None

    # 寄存器常量
    ROH_FW_VERSION = 1001
    ROH_SUB_EXCEPTION = 1006

    # ==============================
    # Modbus 主错误码定义
    # ==============================
    EC01_ILLEGAL_FUNCTION = 0x01
    EC02_ILLEGAL_DATA_ADDRESS = 0x02
    EC03_ILLEGAL_DATA_VALUE = 0x03
    EC04_SERVER_DEVICE_FAILURE = 0x04
    UNKNOWN_FAILURE = 0x05

    roh_exception_list = {
        EC01_ILLEGAL_FUNCTION: '无效的功能码',
        EC02_ILLEGAL_DATA_ADDRESS: '无效的数据地址',
        EC03_ILLEGAL_DATA_VALUE: '无效的数据（协议层，非应用层）',
        EC04_SERVER_DEVICE_FAILURE: '设备故障',
        UNKNOWN_FAILURE: '未知错误'
    }

    # ==============================
    # 子错误码定义（设备故障细分）
    # ==============================
    ERR_STATUS_INIT = 0x01
    ERR_STATUS_CALI = 0x02
    ERR_INVALID_DATA = 0x03
    ERR_STATUS_STUCK = 0x04
    ERR_OP_FAILED = 0x05
    ERR_SAVE_FAILED = 0x06

    roh_sub_exception_list = {
        ERR_STATUS_INIT: '等待初始化或者正在初始化，不接受此读写操作',
        ERR_STATUS_CALI: '等待校正，不接受此读写操作',
        ERR_INVALID_DATA: '无效的寄存器值',
        ERR_STATUS_STUCK: '电机堵转',
        ERR_OP_FAILED: '操作失败',
        ERR_SAVE_FAILED: '保存失败'
    }

    def __init__(self, port):
        """
        初始化 Modbus 客户端
        :param port: 串口号，如 COM3、/dev/ttyUSB0
        """
        super().__init__(port)

    def connect(self):
        """
        建立 Modbus RTU 串口连接
        波特率 115200，RTU 帧格式，超时 0.1s
        """
        try:
            self.serialClient = ModbusSerialClient(
                port=self.port,
                framer=FramerType.RTU,
                baudrate=115200,
                timeout=0.1
            )
            if not self.serialClient.connect():
                raise ConnectionException(f"[port = {self.port}] Could not connect to Modbus device.")

            logger.info(f"[port = {self.port}] Successfully connected to Modbus device.")

        except ConnectionException as e:
            logger.error(f"[port = {self.port}] Error during connection: {e}")
            raise

    def disconnect(self):
        """
        安全断开 Modbus 连接
        关闭串口、清空对象引用、释放端口资源
        """
        if self.serialClient:
            try:
                self.serialClient.close()
                self.serialClient = None
                self._ohand_api = None
                logger.info(f"[port = {self.port}] Connection to Modbus device closed.")
            except Exception as e:
                logger.error(f"[port = {self.port}] Error during teardown: {e}")

    @staticmethod
    def list_available_ports() -> List[str]:
        """
        扫描并返回系统可用串口列表
        自动过滤蓝牙虚拟串口
        :return: 可用串口列表
        """
        if not serial:
            return []

        ports = []
        for port_info in serial.tools.list_ports.comports():
            if not port_info.device:
                continue
            desc = (port_info.description or "").upper()
            if "BLUETOOTH" in desc:
                continue
            ports.append(port_info.device)
        return ports

    def _get_underlying_serial(self):
        """
        获取 pymodbus 底层串口对象
        避免同一端口重复打开导致占用
        :return: 底层 serial 对象
        """
        if not self.serialClient:
            return None
        return getattr(self.serialClient, "socket", None) or getattr(self.serialClient, "serial", None)

    @staticmethod
    def _get_milli_seconds_impl() -> int:
        """获取毫秒级时间戳（供 API 层使用）"""
        return int(time.time() * 1000)

    @staticmethod
    def _delay_milli_seconds_impl(ms: int):
        """毫秒级延时函数（供 API 层使用）"""
        time.sleep(max(0, ms) / 1000.0)

    @staticmethod
    def _uart_send_data_impl(addr, data, length, context):
        """
        与 OHandSerialAPI 兼容的发送接口
        :param context: 底层串口对象
        """
        if context is None:
            return 1
        try:
            context.write(bytes(data[:length]))
            return 0
        except Exception:
            return 1

    def get_exception(self, response, node_id=2) -> str:
        """
        解析 Modbus 错误响应，返回可读错误信息
        :param response: Modbus 错误响应
        :param node_id: 设备从机地址
        :return: 错误描述字符串
        """
        str_exception = ''

        if response.exception_code > self.EC04_SERVER_DEVICE_FAILURE:
            str_exception = self.roh_exception_list[self.UNKNOWN_FAILURE]

        elif response.exception_code == self.EC04_SERVER_DEVICE_FAILURE:
            # 读取细分错误码
            resp_sub = self.serialClient.read_holding_registers(
                address=self.ROH_SUB_EXCEPTION,
                device_id=node_id
            )
            sub_code = resp_sub.registers[0] if not resp_sub.isError() else 0
            str_exception = f'设备故障，具体原因为：{self.roh_sub_exception_list.get(sub_code, "未知子错误")}'

        else:
            str_exception = self.roh_exception_list.get(response.exception_code, "未知错误")

        return str_exception