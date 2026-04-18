# -*- coding: utf-8 -*-
"""
设备连接自动化测试
流程：启动APP → 同意隐私协议 → 扫描设备 → 连接设备 → 关闭APP
全局控制：支持暂停、停止、动态参数刷新
"""
import uiautomator2 as u2
import pytest
import time
from app.app_common import OperateSharedData

# ====================== 全局配置 ======================
APP_PACKAGE_NAME = "com.oymotion.synchrony"

# ====================== 全局控制方法 ======================
def check_test_stop_pause():
    """
    检查测试控制状态
    支持停止测试、暂停测试
    """
    is_stop, is_pause = OperateSharedData.read_control()

    if is_stop:
        print("\n🛑 检测到停止信号，测试终止")
        pytest.exit("测试已手动停止")

    while is_pause:
        print("⏸️ 测试已暂停，等待恢复...")
        for _ in range(10):
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop:
                print("\n🛑 暂停期间检测到停止信号，测试终止")
                pytest.exit("测试已手动停止")

# 全局动态参数
execute_total_times = 1
case_interval_seconds = 5

def refresh_test_params():
    """
    从共享数据模块刷新测试参数
    """
    global execute_total_times, case_interval_seconds
    execute_total_times, case_interval_seconds = OperateSharedData.read_params()
    print(f"\n🔄 参数已刷新 | 执行次数: {execute_total_times} | 用例间隔: {case_interval_seconds}s")

# ====================== Pytest 夹具 ======================
@pytest.fixture(scope="session", autouse=True)
def device_driver():
    """
    全局设备驱动管理
    负责APP启动、驱动初始化、测试结束关闭APP
    """
    driver = u2.connect()
    refresh_test_params()
    driver.app_start(APP_PACKAGE_NAME, stop=True)

    yield driver

    driver.app_stop(APP_PACKAGE_NAME)
    print("\n🎉 全部测试执行完成 → APP已自动关闭")

@pytest.fixture(autouse=True)
def case_control_hook():
    """
    全局用例控制钩子
    每个用例执行后自动刷新参数、等待间隔、检查暂停/停止
    """
    yield
    refresh_test_params()
    time.sleep(case_interval_seconds)
    check_test_stop_pause()

# ====================== 测试用例 ======================
def test_agree_privacy_policy(device_driver):
    """
    同意隐私协议弹窗
    """
    print("\n▶️ 执行：同意隐私协议")

    try:
        if device_driver(description="确定").wait(timeout=5):
            device_driver(description="确定").click()
            print("✅ 隐私协议已确认")
    except Exception:
        print("ℹ️ 未检测到隐私协议弹窗，跳过")

def test_start_device_scan(device_driver):
    """
    启动设备扫描功能
    """
    print("\n▶️ 执行：启动设备扫描")

    try:
        scan_button = device_driver(
            className="android.widget.Button",
            clickable=True
        )
        if scan_button.wait(timeout=10):
            scan_button.click()
            print("✅ 设备扫描已启动")
    except Exception as error:
        pytest.fail(f"❌ 启动扫描失败: {str(error)}")

def test_connect_first_detected_device(device_driver):
    """
    连接扫描到的第一个设备
    """
    print("\n▶️ 执行：连接第一个扫描到的设备")

    try:
        connect_button = device_driver(description="连接")
        if connect_button.wait(timeout=10):
            connect_button.click()
            print("✅ 设备连接成功")
    except Exception as error:
        pytest.fail(f"❌ 设备连接失败: {str(error)}")


def test_enter_waveform_page(device_driver):
    """
    查看波形
    """
    print("\n▶️ 执行：查看波形")

    try:
        # 按照【关于】成功的方式：用 content-desc
        device_driver(description="查看波形").wait(timeout=10)
        device_driver(description="查看波形").click()
        print("✅ 进入波形页面成功")
        time.sleep(1)
        device_driver(description="开始").wait(timeout=10)
        device_driver(description="开始").click()
        time.sleep(2)
        device_driver.press("back")
        time.sleep(1)
    except Exception as e:
        pytest.fail(f"❌ 查看波形失败: {str(e)}")


def test_enter_data_distribution(device_driver):
    """
    数据分发页面
    """
    print("\n▶️ 执行：数据分发")

    try:
        # 按成功经验：用 description
        device_driver(description="数据分发 (LSL)").wait(timeout=10)
        device_driver(description="数据分发 (LSL)").click()
        print("✅ 进入数据分发页面成功")

        time.sleep(2)
        device_driver.press("back")
        time.sleep(1)
    except Exception as e:
        pytest.fail(f"❌ 数据分发失败: {str(e)}")


def test_check_product_info(device_driver):
    """
    查看用户信息
    """
    print("\n▶️ 执行：查看用户信息")

    try:
        # 按成功经验：用 description
        device_driver(description="查看产品信息").wait(timeout=10)
        device_driver(description="查看产品信息").click()
        print("✅ 查看产品信息成功")

        time.sleep(2)
        device_driver.press("back")
        time.sleep(1)
    except Exception as e:
        pytest.fail(f"❌ 查看用户信息失败: {str(e)}")


def test_enter_about_page(device_driver):
    """
    进入关于页面
    """
    print("\n▶️ 执行：关于页面")

    try:
        about = device_driver(description="关于", clickable=True)
        about.wait(timeout=10)
        about.click()

        print("✅ 进入关于页面成功")

        time.sleep(2)
        device_driver.press("back")
        time.sleep(2)
    except Exception as e:
        pytest.fail(f"❌ 进入关于页面失败: {str(e)}")


