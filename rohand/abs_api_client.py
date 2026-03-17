#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


# ==============================
# 协议客户端实现部分
# ==============================

class ABSApiClient(ABC):

    # 端口定义
    port = None

    def __init__(self, port):
        self.port = port

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    # @abstractmethod
    # def read_messages(self):
    #     pass
    #
    # @abstractmethod
    # def write_messages(self):
    #     pass