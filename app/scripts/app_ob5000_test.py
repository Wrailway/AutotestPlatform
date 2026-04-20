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

# ====================== 统一超时时间配置 ======================
WAIT_TIMEOUT_VERY_SHORT = 2    # 弹窗、可选元素
WAIT_TIMEOUT_SHORT = 5         # 常规弹窗
WAIT_TIMEOUT_NORMAL = 10       # 标准页面加载
WAIT_TIMEOUT_LONG = 15         # 扫描、连接设备

# ====================== 统一休眠时间配置 ======================
SLEEP_DEFAULT = 2    # 所有休眠统一2秒
SLEEP_COLLECT = 10   # 仅采集时长10秒

# ====================== 所有中文文案提取为变量 ======================
DESC_VIEW_WAVEFORM = "查看波形"
DESC_START = "开始"
DESC_DATA_COLLECT_BDF = "数据采集(bdf)"
DESC_STOP_COLLECT_BDF = "停止采集(bdf)"
DESC_ALWAYS_ALLOW = "始终允许"
DESC_CONFIRM = "确定"
DESC_DATA_DISTRIBUTION_LSL = "数据分发 (LSL)"
DESC_ALLOW_WHEN_USING = "仅在使用中允许"
DESC_VIEW_PRODUCT_INFO = "查看产品信息"
DESC_ABOUT = "关于"
DESC_CONNECT = "连接"

TEXT_AGREE_PRIVACY = "确定"

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
case_interval_seconds = 2

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
    time.sleep(SLEEP_DEFAULT)

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

# ====================== 工具函数 ======================
def swipe_to_bottom(driver, times=5):
    """滑动到页面最底部（通用工具函数）"""
    for _ in range(times):
        driver.swipe(0.5, 0.9, 0.5, 0.1, 0.2)
        time.sleep(SLEEP_DEFAULT)
    time.sleep(SLEEP_DEFAULT)

def click_if_exists(driver, desc, timeout=WAIT_TIMEOUT_VERY_SHORT):
    """如果元素存在就点击，不存在跳过（权限弹窗专用）"""
    try:
        if driver(description=desc).wait(timeout=timeout):
            driver(description=desc).click()
            print(f"✅ 已点击: {desc}")
            return True
    except:
        pass
    print(f"ℹ️ 未找到: {desc}，跳过")
    return False

# ====================== 测试用例 ======================
def test_agree_privacy_policy(device_driver):
    """同意隐私协议弹窗"""
    print("\n▶️ 执行：同意隐私协议")
    click_if_exists(device_driver, TEXT_AGREE_PRIVACY, timeout=WAIT_TIMEOUT_SHORT)

def test_start_device_scan(device_driver):
    """启动设备扫描功能"""
    print("\n▶️ 执行：启动设备扫描")
    try:
        scan_button = device_driver(className="android.widget.Button", clickable=True)
        scan_button.wait(timeout=WAIT_TIMEOUT_NORMAL)
        scan_button.click()
        print("✅ 设备扫描已启动")
    except Exception as error:
        pytest.fail(f"❌ 启动扫描失败: {str(error)}")

def test_connect_first_detected_device(device_driver):
    """连接扫描到的第一个设备"""
    print("\n▶️ 执行：连接第一个扫描到的设备")
    try:
        connect_button = device_driver(description=DESC_CONNECT)
        connect_button.wait(timeout=WAIT_TIMEOUT_LONG)
        connect_button.click()
        time.sleep(SLEEP_DEFAULT)
        print("✅ 设备连接成功")
    except Exception as error:
        pytest.fail(f"❌ 设备连接失败: {str(error)}")

def test_enter_waveform_page(device_driver):
    """查看波形"""
    print("\n▶️ 执行：查看波形")

    try:
        device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_VIEW_WAVEFORM).click()
        print("✅ 进入波形页面成功")
        time.sleep(SLEEP_DEFAULT)

        device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_START).click()
        time.sleep(SLEEP_DEFAULT)

        # 滑到底部
        swipe_to_bottom(device_driver, times=5)

        device_driver(description=DESC_DATA_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_DATA_COLLECT_BDF).click()

        # 权限弹窗
        click_if_exists(device_driver, DESC_ALWAYS_ALLOW, timeout=WAIT_TIMEOUT_VERY_SHORT)

        # 数据采集10秒
        time.sleep(SLEEP_COLLECT)

        device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_STOP_COLLECT_BDF).click()
        time.sleep(SLEEP_DEFAULT)

        device_driver(description=DESC_CONFIRM).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_CONFIRM).click()
        time.sleep(SLEEP_DEFAULT)

        device_driver.press("back")
        time.sleep(SLEEP_DEFAULT)

        print("✅ 波形采集流程完成")

    except Exception as e:
        pytest.fail(f"❌ 查看波形失败: {str(e)}")

def test_enter_data_distribution(device_driver):
    """数据分发页面"""
    print("\n▶️ 执行：数据分发")

    try:
        device_driver(description=DESC_DATA_DISTRIBUTION_LSL).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_DATA_DISTRIBUTION_LSL).click()
        print("✅ 进入数据分发页面成功")
        time.sleep(SLEEP_DEFAULT)

        click_if_exists(device_driver, DESC_ALLOW_WHEN_USING, timeout=WAIT_TIMEOUT_VERY_SHORT)

        time.sleep(SLEEP_DEFAULT)
        device_driver.press("back")
        time.sleep(SLEEP_DEFAULT)

    except Exception as e:
        pytest.fail(f"❌ 数据分发失败: {str(e)}")

def test_check_product_info(device_driver):
    """查看产品信息"""
    print("\n▶️ 执行：查看产品信息")

    try:
        device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
        print("✅ 查看产品信息成功")
        time.sleep(SLEEP_DEFAULT)

        device_driver.press("back")
        time.sleep(SLEEP_DEFAULT)

    except Exception as e:
        pytest.fail(f"❌ 查看产品信息失败: {str(e)}")

def test_enter_about_page(device_driver):
    """进入关于页面"""
    print("\n▶️ 执行：关于页面")

    try:
        about = device_driver(description=DESC_ABOUT, clickable=True)
        about.wait(timeout=WAIT_TIMEOUT_NORMAL)
        about.click()
        print("✅ 进入关于页面成功")
        time.sleep(SLEEP_DEFAULT)

        device_driver.press("back")
        time.sleep(SLEEP_DEFAULT)

    except Exception as e:
        pytest.fail(f"❌ 进入关于页面失败: {str(e)}")