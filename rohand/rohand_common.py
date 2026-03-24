#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import configparser
from datetime import datetime

# ---------------------------------------------------------------------------
# 表格列名常量
# ---------------------------------------------------------------------------
COL_PORT = "端口号"
COL_SOFTWARE_VERSION = "软件版本"
COL_DEVICE_ID = "设备ID"
COL_CONNECT_STATUS = "连接状态"
COL_TEST_RESULT = "测试结果"

# 表格表头
TABLE_HEADERS = [
    COL_PORT,
    COL_SOFTWARE_VERSION,
    COL_DEVICE_ID,
    COL_CONNECT_STATUS,
    COL_TEST_RESULT,
]

# 测试结果常量
RESULT_PASS = "通过"
RESULT_FAIL = "失败"
RESULT_SKIP = "跳过"
DEFAULT_TEST_RESULT = "--"

# 状态常量
STATUS_CONNECTED_UI = "已连接"
STATUS_WAIT_TEST = "等待测试"
STATUS_TESTING = "测试中"
STATUS_PAUSED = "测试暂停"
STATUS_UNKNOWN_DEVICE = "未识别设备"
STATUS_READ_FAIL = "读取失败"
STATUS_NOT_CONNECTED = "未连接"

# 其他常量
MSG_HINT = "提示"
MSG_REFRESH_PORT = "请刷新端口"
MSG_REFRESHING_PORTS = "正在刷新端口..."
BTN_REFRESH = "刷新"
BTN_LATER = "稍后"
LABEL_SELECT_ALL = "全选"

DIALOG_REFRESH_TITLE = "正在刷新端口"
DIALOG_REFRESH_TIP = "正在刷新端口..."

DEFAULT_AGING_OPTIONS = [
    "0.01小时", "0.1小时", "0.5小时", "1小时", "1.5小时",
    "3小时", "8小时", "12小时", "24小时",
]

# 延迟常量
REFRESH_PROMPT_DELAY_MS = 450


def build_device_info(port, sw_version, device_id, connect_status, test_result=DEFAULT_TEST_RESULT):
    """统一构建设备信息字典，供 manager/UI 复用。"""
    return {
        COL_PORT: port,
        COL_SOFTWARE_VERSION: sw_version,
        COL_DEVICE_ID: device_id,
        COL_CONNECT_STATUS: connect_status,
        COL_TEST_RESULT: test_result,
    }

