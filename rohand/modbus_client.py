#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

from rohand.abs_api_client import ABSApiClient


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
                logger.info(f"[port = {self.port}]Connection to Modbus device closed.\n")
            except Exception as e:
                logger.error(f"[port = {self.port}]Error during teardown: {e}\n")

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