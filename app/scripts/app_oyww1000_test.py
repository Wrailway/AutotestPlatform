# -*- coding: utf-8 -*-
"""
设备连接自动化测试（标准流程版）
流程：启动APP → 同意协议 → 搜索设备 → 连接设备 → 主界面功能遍历
"""
import uiautomator2 as u2
import pytest
import time

from app.app_common import OperateSharedData

# ====================== 全局配置 ======================
APP_PACKAGE_NAME = "com.oymotion.oyww"

# ====================== 超时时间 ======================
WAIT_TIMEOUT_VERY_SHORT = 2
WAIT_TIMEOUT_SHORT = 5
WAIT_TIMEOUT_NORMAL = 10
WAIT_TIMEOUT_LONG = 20

# ====================== 休眠时间 ======================
SLEEP_DEFAULT = 2

# ====================== 页面元素描述 ======================
DESC_FIND_DEVICE = "查找设备"
DESC_CONNECT = "连接"
DESC_READY = "就绪"
DESC_BACK = "返回"
DESC_CONFIRM = "确定"

DESC_VIEW_WAVEFORM = "查看波形"
DESC_START = "返回"
DESC_HPF_FILTER = "HPF高通滤波"
DESC_50HZ_FILTER = "50Hz/60Hz工频滤波"
DESC_LPF_FILTER = "LPF低通滤波"

DESC_GESTURE_TRAIN = "手势训练"
DESC_MODEL_DOWNLOAD = "模型下载"
DESC_VIEW_GESTURE = "查看手势"
DESC_PREDEFINE_PARAMS = "预定义参数设置"
DESC_VIEW_PRODUCT_INFO = "查看产品信息"
DESC_ABOUT = "关于"


# ====================== 全局控制 ======================
def check_test_stop_pause():
    is_stop, is_pause = OperateSharedData.read_control()
    if is_stop:
        pytest.exit("🛑 测试已手动停止")

    while is_pause:
        for _ in range(10):
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop:
                pytest.exit("🛑 测试已手动停止")

execute_total_times = 1
case_interval_seconds = 5

def refresh_test_params():
    global execute_total_times, case_interval_seconds
    execute_total_times, case_interval_seconds = OperateSharedData.read_params()

# ====================== 夹具 ======================
@pytest.fixture(scope="session", autouse=True)
def device_driver():
    driver = u2.connect()
    refresh_test_params()
    driver.app_start(APP_PACKAGE_NAME, stop=True)
    time.sleep(SLEEP_DEFAULT)
    yield driver
    driver.app_stop(APP_PACKAGE_NAME)

@pytest.fixture(autouse=True)
def case_control_hook():
    yield
    refresh_test_params()
    time.sleep(case_interval_seconds)
    check_test_stop_pause()

# ====================== 工具函数 ======================
def click_if_exists(driver, desc, timeout=WAIT_TIMEOUT_VERY_SHORT):
    try:
        if driver(description=desc).wait(timeout=timeout):
            driver(description=desc).click()
            time.sleep(1)
            return True
    except:
        pass
    return False

# ====================== 测试用例 ======================
def test_agree_privacy(device_driver):
    """同意隐私协议"""
    click_if_exists(device_driver, DESC_CONFIRM, timeout=WAIT_TIMEOUT_SHORT)

def test_search_device(device_driver):
    """搜索设备"""
    MAX_RETRY = 3
    found_device = False
    for i in range(MAX_RETRY):
        scan_button = device_driver(className="android.widget.Button", clickable=True)
        scan_button.wait(timeout=WAIT_TIMEOUT_NORMAL)
        scan_button.click()

        device_driver(description=DESC_FIND_DEVICE).wait(timeout=WAIT_TIMEOUT_LONG)
        if device_driver(description=DESC_CONNECT).wait(timeout=WAIT_TIMEOUT_LONG):
            found_device = True
            break
        time.sleep(SLEEP_DEFAULT)
    assert found_device, "❌ 扫描失败：未找到设备"

def test_connect_device(device_driver):
    """连接设备"""
    device_driver(description=DESC_CONNECT).click()
    time.sleep(WAIT_TIMEOUT_SHORT)
    assert device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_LONG), "❌ 设备连接失败"

def test_enter_waveform(device_driver):
    """查看波形"""
    click_if_exists(device_driver, DESC_VIEW_WAVEFORM)
    # device_driver.press("back")
    print("✅ 查看波形")

def test_filter_choose(device_driver):
    """测试滤波开关操作"""
    # ========== HPF开关 ==========
    hpf_xpath = device_driver.xpath('//android.widget.Switch[1]')
    assert hpf_xpath.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到HPF开关"

    # 点击：获取控件范围 → 点右侧 85%
    x1, y1, x2, y2 = hpf_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    hpf_switch = hpf_xpath.get()
    assert hpf_switch.attrib["checked"] == "false", "❌ HPF开关关闭失败"

    # 恢复
    x1, y1, x2, y2 = hpf_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    hpf_switch = hpf_xpath.get()
    assert hpf_switch.attrib["checked"] == "true", "❌ HPF开关恢复失败"

    # ========== 50Hz/60Hz滤除开关 ==========
    filter_50hz_xpath = device_driver.xpath('//android.widget.Switch[2]')
    assert filter_50hz_xpath.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到50Hz滤除开关"

    x1, y1, x2, y2 = filter_50hz_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    filter_50hz_switch = filter_50hz_xpath.get()
    assert filter_50hz_switch.attrib["checked"] == "false", "❌ 50Hz滤除开关关闭失败"

    x1, y1, x2, y2 = filter_50hz_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    filter_50hz_switch = filter_50hz_xpath.get()
    assert filter_50hz_switch.attrib["checked"] == "true", "❌ 50Hz滤除开关恢复失败"

    # ========== LPF开关 ==========
    lpf_xpath = device_driver.xpath('//android.widget.Switch[3]')
    assert lpf_xpath.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到LPF开关"

    x1, y1, x2, y2 = lpf_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    lpf_switch = lpf_xpath.get()
    assert lpf_switch.attrib["checked"] == "false", "❌ LPF开关关闭失败"

    x1, y1, x2, y2 = lpf_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    lpf_switch = lpf_xpath.get()
    assert lpf_switch.attrib["checked"] == "true", "❌ LPF开关恢复失败"
    device_driver.press("back")
    print("✅ 所有滤波开关操作测试通过")

def test_enter_gesture_train(device_driver):
    """手势训练"""
    click_if_exists(device_driver, DESC_GESTURE_TRAIN)
    device_driver.press("back")
    print("✅ 手势训练")

def test_enter_model_download(device_driver):
    """模型下载"""
    click_if_exists(device_driver, DESC_MODEL_DOWNLOAD)
    device_driver.press("back")
    print("✅ 模型下载")

def test_enter_view_gesture(device_driver):
    """查看手势"""
    click_if_exists(device_driver, DESC_VIEW_GESTURE)
    device_driver.press("back")
    print("✅ 查看手势")

def test_enter_predefine_params(device_driver):
    """预定义参数设置"""
    click_if_exists(device_driver, DESC_PREDEFINE_PARAMS)
    device_driver.press("back")
    print("✅ 预定义参数设置")

def test_enter_product_info(device_driver):
    """查看产品信息"""
    click_if_exists(device_driver, DESC_VIEW_PRODUCT_INFO)
    device_driver.press("back")
    print("✅ 查看产品信息")

def test_enter_about(device_driver):
    """关于页面"""
    click_if_exists(device_driver, DESC_ABOUT)
    device_driver.press("back")
    print("✅ 关于页面")

# ========================= 统一执行流程 =========================
def run_all_test_cases(device_driver):
    """标准完整流程：搜索 → 连接 → 遍历功能"""
    test_agree_privacy(device_driver)
    test_search_device(device_driver)
    test_connect_device(device_driver)

    test_enter_waveform(device_driver)
    test_enter_gesture_train(device_driver)
    test_enter_model_download(device_driver)
    test_enter_view_gesture(device_driver)
    test_enter_predefine_params(device_driver)
    test_enter_product_info(device_driver)
    test_enter_about(device_driver)

# ========================= 压力测试 =========================
@pytest.mark.skip('skip test_main_auto_run')
def test_main_auto_run():
    """自动循环测试"""
    refresh_test_params()
    print(f"\n🚀 开始执行压力测试，总轮次：{execute_total_times}")

    for i in range(1, execute_total_times + 1):
        check_test_stop_pause()
        print(f"\n=====================================")
        print(f"📌 第 {i}/{execute_total_times} 轮测试")
        print(f"=====================================\n")

        driver = u2.connect()
        driver.app_stop(APP_PACKAGE_NAME)
        time.sleep(1)
        driver.app_start(APP_PACKAGE_NAME, stop=True)
        time.sleep(SLEEP_DEFAULT)

        run_all_test_cases(driver)

        driver.app_stop(APP_PACKAGE_NAME)
        print(f"\n✅ 第 {i} 轮执行完成")

        refresh_test_params()
        time.sleep(case_interval_seconds)

    print("\n🎉 所有测试完成！")