#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

import logging

from rohand.OHandSerialAPI import HAND_PROTOCOL_UART, OHandSerialAPI
from rohand.abs_api_client import ABSApiClient
from rohand.can_interface import CAN_Init, send_data_impl, get_milli_seconds_impl, recv_data_impl, \
    delay_milli_seconds_impl


# ==============================
# Can协议客户端实现部分
# ==============================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CanClient(ABSApiClient):
    baudrate = 1000000
    ADDRESS_MASTER = 0x01
    serialClient = None
    can_interface_instance = None

    def __init__(self, port):
        ABSApiClient.__init__(self, port)

    def connect(self):
        try:
            port_num = int(re.findall(r'\d+', self.port)[0])
            logger.info(f'port_num={port_num}')
            self.can_interface_instance = CAN_Init(port_name=port_num, baudrate=self.baudrate)
            if self.can_interface_instance is None:
                logger.info("port init failed\n")
            protocol = HAND_PROTOCOL_UART
            self.serialClient = OHandSerialAPI(self.can_interface_instance, protocol, self.ADDRESS_MASTER,
                                               send_data_impl,
                                               recv_data_impl)
            self.serialClient.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
            self.serialClient.HAND_SetCommandTimeOut(255)
        except Exception as e:
            logger.info(f"\n初始化异常: {str(e)}")

    def disconnect(self):
        if self.serialClient and hasattr(self.serialClient, "shutdown"):
            try:
                self.client_NotNone()
                self.serialClient = None
                logger.info("API shutdown successfully")
            except Exception as e:
                logger.error(f"Error during API shutdown: {e}")

        if self.can_interface_instance and hasattr(self.can_interface_instance, "shutdown"):
            try:
                self.can_interface_instance.shutdown()
                self.can_interface_instance = None
                logger.info("CAN bus connection closed")
            except Exception as e:
                logger.error(f"Error closing CAN bus: {e}")

    def client_NotNone(self):
        self.serialClient.shutdown()
