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

# 执行次数选项
DEFAULT_EXECUTE_TIMES_OPTIONS = [
    "1次", "5次", "20次", "50次", "100次", "200次", "500次", "1000次", "2000次", "5000次", "10000次"
]

#操作间隔选项
DEFAULT_OPERATE_INTERVAL_OPTIONS = [
    "1秒", "2秒","3秒","5秒", "10秒", "15秒", "20秒", "30秒", "45秒", "60秒"
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
    _FILE = "shared_data.json"

    # ===================== 【控制：停止 / 暂停】 =====================
    @classmethod
    def write_control(cls, stop_test: bool, pause_test: bool):
        with FILE_LOCK:
            data = cls._load_all()
            data["stop_test"] = stop_test
            data["pause_test"] = pause_test
            cls._save_all(data)

    @classmethod
    def read_control(cls):
        with FILE_LOCK:
            data = cls._load_all()
            return data.get("stop_test", False), data.get("pause_test", False)

    # ===================== 【参数：执行次数 / 操作间隔】 =====================
    @classmethod
    def write_params(cls, execute_times: int = None, operate_interval: float = None):
        """
        支持单独写入任意一个参数
        传哪个就更新哪个，不传就保持原有值，不影响、不覆盖
        """
        with FILE_LOCK:
            data = cls._load_all()

            # 只有传了值才更新，不传不碰
            if execute_times is not None:
                data["execute_times"] = execute_times
            if operate_interval is not None:
                data["operate_interval"] = operate_interval

            cls._save_all(data)

    @classmethod
    def read_params(cls):
        with FILE_LOCK:
            data = cls._load_all()
            return (
                data.get("execute_times", 1),
                data.get("operate_interval", 1.0)
            )

    # ===================== 内部工具 =====================
    @classmethod
    def _load_all(cls):
        try:
            with open(cls._FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    @classmethod
    def _save_all(cls, data):
        with open(cls._FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

    @classmethod
    def delete_shared_data_file(cls):
        try:
            if os.path.exists(cls._FILE):
                os.remove(cls._FILE)
        except:
            pass