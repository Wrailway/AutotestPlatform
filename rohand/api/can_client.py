#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAN 协议客户端实现
继承抽象接口 ABSApiClient，完成 CAN 总线连接、断开、设备通信封装
"""
import re
import logging

from rohand.api.abs_api_client import ABSApiClient
from rohand.api.OHandSerialAPI import HAND_PROTOCOL_UART, OHandSerialAPI
from rohand.api.can_interface import (
    CAN_Init,
    send_data_impl,
    get_milli_seconds_impl,
    recv_data_impl,
    delay_milli_seconds_impl
)

# ==============================
# 日志配置
# ==============================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ==============================
# CAN 协议客户端实现
# ==============================
class CanClient(ABSApiClient):
    """
    CAN 总线通信客户端
    实现连接、断开、底层接口封装，对接 OHandSerialAPI
    """
    # 通信参数常量
    baudrate = 1000000
    ADDRESS_MASTER = 0x01
    SUCCESS = 0x00

    # 实例对象
    serialClient = None
    can_interface_instance = None

    def __init__(self, port):
        """
        初始化 CAN 客户端
        :param port: CAN 通道名，如 PCAN_USBBUS1
        """
        ABSApiClient.__init__(self, port)

    def connect(self):
        """
        建立 CAN 总线连接
        1. 解析端口号
        2. 初始化 CAN 接口
        3. 初始化 OHandSerialAPI 协议层
        """
        try:
            # 从端口名提取数字（PCAN_USBBUS1 → 1）
            port_num = int(re.findall(r'\d+', self.port)[0])
            logger.info(f'port_num={port_num}')

            # 初始化 CAN 硬件接口
            self.can_interface_instance = CAN_Init(port_name=port_num, baudrate=self.baudrate)
            if self.can_interface_instance is None:
                logger.info("port init failed\n")
                return

            # 初始化协议 API
            protocol = HAND_PROTOCOL_UART
            self.serialClient = OHandSerialAPI(
                self.can_interface_instance,
                protocol,
                self.ADDRESS_MASTER,
                send_data_impl,
                recv_data_impl
            )
            self.serialClient.HAND_SetTimerFunction(get_milli_seconds_impl, delay_milli_seconds_impl)
            self.serialClient.HAND_SetCommandTimeOut(255)
            logger.info(f"[CAN {self.port}] Connect successfully")

        except Exception as e:
            logger.info(f"\n初始化异常: {str(e)}")

    def disconnect(self):
        """
        安全断开 CAN 连接
        - 关闭 API 客户端
        - 关闭 CAN 总线
        - 强制清空对象引用，避免内存残留
        """
        # 关闭 API 客户端
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
                self.serialClient = None

        # 关闭 CAN 硬件接口
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
                self.can_interface_instance = None

        logger.info(f"[CAN {self.port}] Disconnect completed")