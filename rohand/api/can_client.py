#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

import logging

from rohand.api.abs_api_client import ABSApiClient
from rohand.api.OHandSerialAPI import HAND_PROTOCOL_UART, OHandSerialAPI
from rohand.api.can_interface import CAN_Init, send_data_impl, get_milli_seconds_impl, recv_data_impl, \
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
    SUCCESS = 0x00

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
        """
        安全断开CAN连接（优化版）
        - 先关闭API客户端，再关闭CAN总线
        - 兼容无shutdown方法的场景
        - 强制清空属性，避免残留引用
        """
        # 1. 关闭OHandSerialAPI客户端
        if self.serialClient:
            try:
                if hasattr(self.serialClient, "shutdown"):
                    self.serialClient.shutdown()
                    logger.info(f"[CAN {self.port}] API shutdown successfully")
                else:
                    logger.warning(f"[CAN {self.port}] API has no shutdown method, skip")
            except Exception as e:
                logger.error(f"[CAN {self.port}] Error during API shutdown: {str(e)}", exc_info=True)
            finally:
                # 强制清空，无论是否报错
                self.serialClient = None

        # 2. 关闭CAN总线接口
        if self.can_interface_instance:
            try:
                if hasattr(self.can_interface_instance, "shutdown"):
                    self.can_interface_instance.shutdown()
                    logger.info(f"[CAN {self.port}] CAN bus connection closed successfully")
                else:
                    logger.warning(f"[CAN {self.port}] CAN interface has no shutdown method, skip")
            except Exception as e:
                logger.error(f"[CAN {self.port}] Error closing CAN bus: {str(e)}", exc_info=True)
            finally:
                # 强制清空，无论是否报错
                self.can_interface_instance = None

        # 3. 额外兜底：清空端口属性（可选，根据需要）
        # self.port = None
        logger.info(f"[CAN {self.port}] Disconnect completed")


    # def has_device(self,id):
    #     major, minor, revision = [0], [0], [0]
    #     err, major_get, minor_get, revision_get = self.serialClient.HAND_GetFirmwareVersion(id, major, minor,
    #                                                                                           revision, [])
    #     if err != self.SUCCESS:
    #         return False
    #     else:
    #         return True

