#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公共常量与工具模块
提供测试常量定义、设备信息构造、共享数据读写等通用功能
"""
import os
import json
import threading
import configparser
from datetime import datetime

import logger

# ---------------------------------------------------------------------------
# 表格列名常量
# ---------------------------------------------------------------------------
COL_ID = '用例编号'
COL_CASE_DESCRIPTION = "用例描述"
COL_TEST_RESULT = "测试结果"

# 表格表头
TABLE_HEADERS = [
    COL_ID,
    COL_CASE_DESCRIPTION,
    COL_TEST_RESULT
]

# 测试结果常量
RESULT_PASS = "通过"
RESULT_FAIL = "失败"
RESULT_SKIP = "跳过"
DEFAULT_TEST_RESULT = "--"

# 设备状态常量
STATUS_CONNECTED_UI = "已连接"
STATUS_WAIT_TEST = "等待测试"
STATUS_TESTING = "测试中"
STATUS_PAUSED = "测试暂停"
STATUS_UNKNOWN_DEVICE = "未识别设备"
STATUS_READ_FAIL = "读取失败"
STATUS_NOT_CONNECTED = "未连接"

# 默认老化时间选项
DEFAULT_EXECUTE_TIMES_OPTIONS = [
    "1次", "5次", "20次", "50次", "100次"
]

DEFAULT_OPERATE_INTERVAL_OPTIONS = [
    "1秒", "2秒","3秒","5秒", "10秒"
]

# 全局线程锁：保证多线程文件读写安全
FILE_LOCK = threading.Lock()


def build_device_info(case_id, description, test_result=DEFAULT_TEST_RESULT):
    """
    统一构建设备信息字典
    供设备管理模块、UI界面复用
    """
    return {
        COL_ID:case_id,
        COL_CASE_DESCRIPTION: description,
        COL_TEST_RESULT: test_result,
    }


class OperateSharedData:
    """
    测试控制状态共享数据操作类
    用于多线程间传递 停止测试/暂停测试 标志位
    """
    _FILE = "shared_data.json"

    @classmethod
    def write(cls, stop_test: bool, pause_test: bool):
        """
        写入共享测试状态
        :param stop_test: 是否停止测试
        :param pause_test: 是否暂停测试
        """
        with FILE_LOCK:
            data = {"stop_test": stop_test, "pause_test": pause_test}
            with open(cls._FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())

    @classmethod
    def read(cls):
        """
        读取共享测试状态
        :return: (stop_test, pause_test) 元组
        """
        with FILE_LOCK:
            try:
                with open(cls._FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                stop = data.get("stop_test", False)
                pause = data.get("pause_test", False)
                return stop, pause
            except Exception:
                return False, False

    @classmethod
    def delete_shared_data_file(cls):
        """删除共享数据文件，异常安全，不抛出错误"""
        file_path = cls._FILE
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass