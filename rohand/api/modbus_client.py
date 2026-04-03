#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modbus 协议客户端实现
继承抽象接口 ABSApiClient，完成串口 Modbus 连接、断开、寄存器读写、错误解析等封装
"""
import logging
from typing import Optional

from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from rohand.api.abs_api_client import ABSApiClient

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
                logger.info(f"[port = {self.port}] Connection to Modbus device closed.")
            except Exception as e:
                logger.error(f"[port = {self.port}] Error during teardown: {e}")

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