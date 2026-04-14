#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公共常量与工具模块
提供测试常量定义、设备信息构造、共享数据读写等通用功能
"""
import os
import json
import threading
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

# 运行环境
ENVIRONMENT_TEST = '测试环境'
ENVIRONMENT_PRODUCTION = '正式环境'

DEFAULT_OPERATE_ENVIRONMENT_OPTIONS = [
    ENVIRONMENT_TEST,
    ENVIRONMENT_PRODUCTION
]

# 执行次数选项
DEFAULT_EXECUTE_TIMES_OPTIONS = [
    "1次", "5次", "20次", "50次", "100次", "200次", "500次", "1000次", "2000次", "5000次", "10000次"
]

# 操作间隔选项
DEFAULT_OPERATE_INTERVAL_OPTIONS = [
    "1秒", "2秒","3秒","5秒", "10秒", "15秒", "20秒", "30秒", "45秒", "60秒"
]

# 线程数目
DEFAULT_NUM_OF_THREADS_OPTIONS = ["1", "5", "10", "20", "50", "100", "500", "1000", "2000", "5000", "10000"]

# 并发用户数
DEFAULT_NUM_OF_CONCURRENT_USERS_OPTIONS = ["1", "5", "10", "20", "50", "100", "500", "1000", "2000", "5000", "10000"]

# 运行时间
DEFAULT_DURATION_OPTIONS = [
    "3分钟", "10分钟","30分钟","60分钟", "120分钟", "480分钟", "960分钟", "1440分钟", "2880分钟"
]

# 爬坡时间
DEFAULT_RAMP_UP_OPTIONS = [
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
        COL_ID: case_id,
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

    # ===================== 【测试环境参数：运行环境】 =====================
    @classmethod
    def write_environment_params(cls, operate_environment: str = None):
        """
        支持单独写入任意一个参数
        传哪个就更新哪个，不传就保持原有值，不影响、不覆盖
        """
        with FILE_LOCK:
            data = cls._load_all()
            if operate_environment is not None:
                data["operate_environment"] = operate_environment
            cls._save_all(data)

    @classmethod
    def read_environment_params(cls):
        with FILE_LOCK:
            data = cls._load_all()
            return data.get("operate_environment", ENVIRONMENT_TEST),

    # ===================== 【功能测试参数：执行次数 / 操作间隔 / 线程数】 =====================
    @classmethod
    def write_fun_params(cls, execute_times: int = None, operate_interval: float = None, threads_num: int = None):
        """
        支持单独写入任意一个参数
        传哪个就更新哪个，不传就保持原有值
        """
        with FILE_LOCK:
            data = cls._load_all()
            if execute_times is not None:
                data["execute_times"] = execute_times
            if operate_interval is not None:
                data["operate_interval"] = operate_interval
            if threads_num is not None:
                data["threads_num"] = threads_num
            cls._save_all(data)

    @classmethod
    def read_fun_params(cls):
        with FILE_LOCK:
            data = cls._load_all()
            return (
                data.get("execute_times", 1),
                data.get("operate_interval", 1.0),
                data.get("threads_num", 1)
            )

    # ===================== 【性能测试参数：并发用户数 / 运行时间 / 爬坡时间】 =====================
    @classmethod
    def write_perf_params(cls, concurrent_user_nums: int = None, duration: int = None, ramp_up: int = None):
        with FILE_LOCK:
            data = cls._load_all()
            if concurrent_user_nums is not None:
                data["concurrent_user_nums"] = concurrent_user_nums
            if duration is not None:
                data["duration"] = duration
            if ramp_up is not None:
                data["ramp_up"] = ramp_up
            cls._save_all(data)

    @classmethod
    def read_perf_params(cls):
        with FILE_LOCK:
            data = cls._load_all()
            return (
                data.get("concurrent_user_nums", 1),
                data.get("duration", 3),
                data.get("ramp_up", 1)
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