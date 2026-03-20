#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
from typing import Optional, List

from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from abs_api_client import ABSApiClient
from OHandSerialAPI import OHandSerialAPI, HAND_PROTOCOL_UART, HAND_RESP_SUCCESS

try:
    import serial.tools.list_ports
except Exception:  # pragma: no cover
    serial = None


# ==============================
# modbus协议客户端实现部分
# ==============================


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ModbusClient(ABSApiClient):
    serialClient = None
    ROH_FW_VERSION = 1001
    ROH_SUB_EXCEPTION = (1006)  # R

    def __init__(self, port):
        ABSApiClient.__init__(self, port)
        self._ohand_api: Optional[OHandSerialAPI] = None

    def connect(self):
        try:
            self.serialClient = ModbusSerialClient(port=self.port, framer=FramerType.RTU, baudrate=115200, timeout=0.1)
            if not self.serialClient.connect():
                raise ConnectionException(f"[port = {self.port}]Could not connect to Modbus device.")
            logger.info(f"[port = {self.port}]Successfully connected to Modbus device.")
        except ConnectionException as e:
            logger.error(f"[port = {self.port}]Error during connection: {e}")
            raise

    def disconnect(self):
        if self.serialClient:
            try:
                self.serialClient.close()
                self.serialClient = None
                self._ohand_api = None
                logger.info(f"[port = {self.port}]Connection to Modbus device closed.\n")
            except Exception as e:
                logger.error(f"[port = {self.port}]Error during teardown: {e}\n")

    @staticmethod
    def list_available_ports() -> List[str]:
        """
        返回系统可用串口（如 ["COM3", "COM6"]），过滤掉蓝牙虚拟串口。
        """
        if not hasattr(serial, "tools") or not hasattr(serial.tools, "list_ports"):
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
        尝试从 pymodbus 的 ModbusSerialClient 里拿到底层串口对象，
        避免同一个 COM 口被打开两次导致占用失败。
        """
        if not self.serialClient:
            return None
        return getattr(self.serialClient, "socket", None) or getattr(self.serialClient, "serial", None)

    @staticmethod
    def _get_milli_seconds_impl():
        return int(time.time() * 1000)

    @staticmethod
    def _delay_milli_seconds_impl(ms: int):
        time.sleep(max(0, ms) / 1000.0)

    @staticmethod
    def _uart_send_data_impl(addr, data, length, context):
        """
        与 OHandSerialAPI 兼容的发送函数签名：(addr, data, length, context)
        context 这里传入底层串口对象。
        """
        if context is None:
            return 1
        try:
            context.write(bytes(data[:length]))
            return 0
        except Exception:
            return 1

    # ROH 灵巧手错误代码

    EC01_ILLEGAL_FUNCTION = 0X1  # 无效的功能码
    EC02_ILLEGAL_DATA_ADDRESS = 0X2  # 无效的数据地址
    EC03_ILLEGAL_DATA_VALUE = 0X3  # 无效的数据（协议层，非应用层）
    EC04_SERVER_DEVICE_FAILURE = 0X4  # 设备故障
    UNKNOWN_FAILURE = 0X5  # 未知错误

    roh_exception_list = {
        EC01_ILLEGAL_FUNCTION: '无效的功能码',
        EC02_ILLEGAL_DATA_ADDRESS: '无效的数据地址',
        EC03_ILLEGAL_DATA_VALUE: '无效的数据（协议层，非应用层）',
        EC04_SERVER_DEVICE_FAILURE: '设备故障',
        UNKNOWN_FAILURE: '未知错误'
    }

    # 寄存器 ROH_SUB_EXCEPTION 保存了具体的错误代码
    ERR_STATUS_INIT = 0X1  # 等待初始化或者正在初始化，不接受此读写操作
    ERR_STATUS_CALI = 0X2  # 等待校正，不接受此读写操作
    ERR_INVALID_DATA = 0X3  # 无效的寄存器值
    ERR_STATUS_STUCK = 0X4  # 电机堵转
    ERR_OP_FAILED = 0X5  # 操作失败
    ERR_SAVE_FAILED = 0X6  # 保存失败

    roh_sub_exception_list = {
        ERR_STATUS_INIT: '等待初始化或者正在初始化，不接受此读写操作',
        ERR_STATUS_CALI: '等待校正，不接受此读写操作',
        ERR_INVALID_DATA: '无效的寄存器值',
        ERR_STATUS_STUCK: '电机堵转',
        ERR_OP_FAILED: '操作失败',
        ERR_SAVE_FAILED: '保存失败'
    }

    def get_exception(self, response, node_id=2):
        """
        根据传入的响应确定错误类型。

        参数：
        response：包含错误信息的响应对象。

        返回：
        错误类型的描述字符串。
        """
        strException = ''
        if response.exception_code > self.EC04_SERVER_DEVICE_FAILURE:
            strException = self.roh_exception_list.get(self.UNKNOWN_FAILURE)
        elif response.exception_code == self.EC04_SERVER_DEVICE_FAILURE:
            # response2 = self.client.read_holding_registers(ROH_SUB_EXCEPTION, 1, self.NODE_ID)
            response2 = self.serialClient.read_holding_registers(address=self.ROH_SUB_EXCEPTION, device_id=node_id)
            strException = '设备故障，具体原因为' + self.roh_sub_exception_list.get(response2.registers[0])
        else:
            strException = self.roh_exception_list.get(response.exception_code)
        return strException

    # def has_device(self,id):
    #     response = self.serialClient.read_holding_registers(self.ROH_FW_VERSION, id)
    #
    #     return not response.isError()