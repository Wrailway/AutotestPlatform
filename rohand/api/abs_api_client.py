#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协议客户端抽象基类模块
定义 Modbus / CAN 等通信客户端的统一接口规范
所有具体协议客户端必须实现 connect / disconnect 方法
"""
from abc import ABC, abstractmethod


# ==============================
# 协议客户端抽象基类定义
# ==============================

class ABSApiClient(ABC):
    """
    通信协议客户端抽象基类
    所有协议客户端（Modbus、CAN等）必须继承并实现抽象方法
    """

    # 通信端口/通道号
    port = None

    def __init__(self, port):
        """
        初始化抽象客户端
        :param port: 通信端口号 / 设备通道名（如 COM3、PCAN_USBBUS1）
        """
        self.port = port

    @abstractmethod
    def connect(self):
        """
        抽象方法：建立设备连接
        子类必须实现连接逻辑
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        抽象方法：断开设备连接
        子类必须实现断开连接逻辑
        """
        pass