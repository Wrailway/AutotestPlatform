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
