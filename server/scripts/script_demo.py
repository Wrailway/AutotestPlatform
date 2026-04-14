#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import pytest
from server.server_common import OperateSharedData, ENVIRONMENT_TEST

# 全局参数（全部用上）
operate_environment = ENVIRONMENT_TEST
execute_times = 1
operate_interval = 1.0
threads_num = 1
concurrent_user_num = 1
duration = 3
ramp_up_time = 1
stop_test = False
pause_test = False


def refresh_params():
    """刷新所有共享参数（全部读取）"""
    global operate_environment, execute_times, operate_interval, threads_num
    global concurrent_user_num, duration, ramp_up_time, stop_test, pause_test

    # 控制参数
    stop_test, pause_test = OperateSharedData.read_control()
    # 环境参数
    operate_environment = OperateSharedData.read_environment_params()[0]
    # 功能参数
    execute_times, operate_interval, threads_num = OperateSharedData.read_fun_params()
    # 性能参数
    concurrent_user_num, duration, ramp_up_time = OperateSharedData.read_perf_params()


# 自动刷新
@pytest.fixture(autouse=True)
def auto_refresh_params():
    refresh_params()


# ===================== 标准测试用例：全部参数控制 + assert 收尾 =====================
def test_business_execution():
    """
    完整使用所有共享参数的测试用例
    """
    # 1. 控制参数：停止则跳过
    business_result = False
    if stop_test:
        pytest.skip("测试已停止")

    print(f"\n=== 运行环境：{operate_environment} ===")
    print(f"并发用户：{concurrent_user_num}")
    print(f"运行时长：{duration}s")
    print(f"爬坡时间：{ramp_up_time}s")
    print(f"执行次数：{execute_times}")
    print(f"操作间隔：{operate_interval}s")
    print(f"线程数：{threads_num}\n")

    start_time = time.time()

    # 2. 按参数控制：执行指定次数
    for i in range(execute_times):
        # 暂停检测
        while pause_test:
            time.sleep(1)
            refresh_params()

        # 3. 运行时长控制
        if time.time() - start_time > duration:
            print("达到运行时长，结束执行")
            break

        # ================== 你的业务逻辑 ==================
        print(f"第 {i+1} 次业务执行")
        business_result = True  # 替换成你的真实接口返回
        # =================================================

        time.sleep(operate_interval)

    # 用例必须：断言收尾
    assert business_result is True, "业务接口执行失败"