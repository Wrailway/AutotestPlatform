# -*- coding: utf-8 -*-
"""
设备连接自动化测试（优化稳定版）
流程：启动APP → 同意隐私协议 → 扫描设备 → 连接设备 → 关闭APP
全局控制：支持暂停、停止、动态参数刷新
"""
import uiautomator2 as u2
import pytest
import time

from app.app_common import OperateSharedData

# ====================== 全局配置 ======================
APP_PACKAGE_NAME = "com.oymotion.synchronymp"

# ====================== 超时时间 ======================
WAIT_TIMEOUT_VERY_SHORT = 2
WAIT_TIMEOUT_SHORT = 5
WAIT_TIMEOUT_NORMAL = 10
WAIT_TIMEOUT_LONG = 15

# ====================== 休眠时间 ======================
SLEEP_DEFAULT = 2
SLEEP_COLLECT = 10

# ====================== 页面元素描述 ======================
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
DESC_FIND_DEVICE = "查找设备"
DESC_READY = "就绪"
TEXT_AGREE_PRIVACY = "确定"

# ====================== 校验关键字 ======================
DEVICE_ADDRESS = "设备地址"
SOFTWARE_NAME = "软件名称"

# ====================== 滤波开关定义 ======================
DESC_50HZ_FILTER = "50Hz滤除："
DESC_60HZ_FILTER = "60Hz滤除："
DESC_HPF_FILTER = "HPF："
DESC_LPF_FILTER = "LPF ："

# ====================== 开关点击偏移配置 ======================
SWITCH_OFFSET_X = 450

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
case_interval_seconds = 2

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
def click_text_by_ocr(driver, target_text, offset_x=0, offset_y=0):
    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
        img = driver.screenshot()
        img.save("tmp_screenshot.png")
        results, _ = _ocr("tmp_screenshot.png")

        for item in results:
            box = item[0]
            text = item[1]
            x1 = min(p[0] for p in box)
            y1 = min(p[1] for p in box)
            x2 = max(p[0] for p in box)
            y2 = max(p[1] for p in box)

            if target_text in text:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                driver.click(cx + offset_x, cy + offset_y)
                return True
    except Exception as e:
        print(f"⚠️ OCR异常: {e}")
    return False

def get_page_text(driver):
    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
        img = driver.screenshot()
        img.save("tmp_screenshot.png")
        results, _ = _ocr("tmp_screenshot.png")
        return " ".join([item[1] for item in results])
    except Exception as e:
        print(f"⚠️ OCR识别失败: {e}")
        return ""

def swipe_to_bottom(driver, times=5):
    for _ in range(times):
        driver.swipe(0.5, 0.9, 0.5, 0.1, 0.2)
        time.sleep(SLEEP_DEFAULT)

def click_if_exists(driver, desc, timeout=WAIT_TIMEOUT_VERY_SHORT):
    try:
        if driver(description=desc).wait(timeout=timeout):
            driver(description=desc).click()
            return True
    except:
        pass
    return False

# ====================== 测试用例 ======================
def test_agree_privacy_policy(device_driver):
    """同意隐私协议"""
    click_if_exists(device_driver, TEXT_AGREE_PRIVACY, timeout=WAIT_TIMEOUT_SHORT)

def test_start_device_scan(device_driver):
    """扫描设备"""
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

def test_connect_first_detected_device(device_driver):
    """连接设备"""
    device_driver(description=DESC_CONNECT).click()
    time.sleep(SLEEP_DEFAULT)
    assert device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_LONG), "❌ 设备连接失败"

def test_navigate_to_waveform(device_driver):
    """进入波形界面"""
    device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_WAVEFORM).click()
    time.sleep(SLEEP_DEFAULT)
    assert device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 进入波形页面失败"

def test_filter_choose(device_driver):
    """测试滤波开关操作（打开→关闭）"""
    device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_START).click()
    time.sleep(SLEEP_DEFAULT)

    # ========== 50Hz ==========
    assert device_driver(description=DESC_50HZ_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到50Hz滤除文本"
    filter_50hz = device_driver.xpath('//android.widget.Switch[@index="2"]')
    assert filter_50hz.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到50Hz开关"

    filter_50hz.click()
    time.sleep(SLEEP_DEFAULT)
    assert filter_50hz.get().attrib["checked"] == "false", "❌ 50Hz关闭失败"

    filter_50hz.click()
    time.sleep(SLEEP_DEFAULT)
    assert filter_50hz.get().attrib["checked"] == "true", "❌ 50Hz恢复失败"

    # ========== 60Hz ==========
    assert device_driver(description=DESC_60HZ_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到60Hz滤除文本"
    filter_60hz = device_driver.xpath('//android.widget.Switch[@index="4"]')
    assert filter_60hz.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到60Hz开关"

    filter_60hz.click()
    time.sleep(SLEEP_DEFAULT)
    assert filter_60hz.get().attrib["checked"] == "false", "❌ 60Hz关闭失败"

    filter_60hz.click()
    time.sleep(SLEEP_DEFAULT)
    assert filter_60hz.get().attrib["checked"] == "true", "❌ 60Hz恢复失败"

    # ========== HPF ==========
    assert device_driver(description=DESC_HPF_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到HPF文本"
    hpf = device_driver.xpath('//android.widget.Switch[@index="6"]')
    assert hpf.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到HPF开关"

    hpf.click()
    time.sleep(SLEEP_DEFAULT)
    assert hpf.get().attrib["checked"] == "false", "❌ HPF关闭失败"

    hpf.click()
    time.sleep(SLEEP_DEFAULT)
    assert hpf.get().attrib["checked"] == "true", "❌ HPF恢复失败"

    # ========== LPF ==========
    assert device_driver(description=DESC_LPF_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到LPF文本"
    lpf = device_driver.xpath('//android.widget.Switch[@index="8"]')
    assert lpf.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到LPF开关"

    lpf.click()
    time.sleep(SLEEP_DEFAULT)
    assert lpf.get().attrib["checked"] == "false", "❌ LPF关闭失败"

    lpf.click()
    time.sleep(SLEEP_DEFAULT)
    assert lpf.get().attrib["checked"] == "true", "❌ LPF恢复失败"

    print("✅ 所有滤波开关操作测试通过")

def test_start_data_collection(device_driver):
    """开始数据采集"""
    swipe_to_bottom(device_driver)
    device_driver(description=DESC_DATA_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DATA_COLLECT_BDF).click()
    time.sleep(SLEEP_DEFAULT)
    click_if_exists(device_driver, DESC_ALWAYS_ALLOW)
    assert device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 采集开启失败"

def test_stop_data_collection(device_driver):
    """停止数据采集"""
    time.sleep(SLEEP_COLLECT)
    device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_STOP_COLLECT_BDF).click()
    time.sleep(SLEEP_DEFAULT)

    assert device_driver(description=DESC_CONFIRM).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 停止采集失败"
    device_driver(description=DESC_CONFIRM).click()
    time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    assert device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 返回设备页面失败"

@pytest.mark.skip('skip test_enter_data_distribution')
def test_enter_data_distribution(device_driver):
    """进入数据分发页面"""
    device_driver(description=DESC_DATA_DISTRIBUTION_LSL).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DATA_DISTRIBUTION_LSL).click()
    time.sleep(SLEEP_DEFAULT)
    click_if_exists(device_driver, DESC_ALLOW_WHEN_USING)
    time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

def test_check_product_info(device_driver):
    """查看产品信息"""
    device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
    time.sleep(SLEEP_DEFAULT)

    # 稳定断言：已进入产品信息页
    assert device_driver(descriptionContains=DEVICE_ADDRESS).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入产品信息页面"

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    assert device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 返回就绪页面失败"

def test_enter_about_page(device_driver):
    """进入关于页面"""
    device_driver(description=DESC_ABOUT).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_ABOUT).click()
    time.sleep(SLEEP_DEFAULT)

    assert device_driver(descriptionContains=SOFTWARE_NAME).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入关于页面"
    time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

# ========================= 统一用例入口 =========================
def run_all_test_cases(device_driver):
    """一轮完整测试流程"""
    test_agree_privacy_policy(device_driver)
    test_start_device_scan(device_driver)
    test_connect_first_detected_device(device_driver)
    test_navigate_to_waveform(device_driver)
    test_filter_choose(device_driver)
    test_start_data_collection(device_driver)
    test_stop_data_collection(device_driver)
    test_check_product_info(device_driver)
    test_enter_about_page(device_driver)

# ========================= 主测试函数 =========================
@pytest.mark.skip('skip test_main_auto_run')
def test_main_auto_run():
    """压力测试（每次循环重启APP）"""
    refresh_test_params()
    print(f"\n🚀 开始执行压力测试，总轮次：{execute_total_times}")

    for i in range(1, execute_total_times + 1):
        check_test_stop_pause()
        print(f"\n=====================================")
        print(f"📌 第 {i}/{execute_total_times} 轮测试开始")
        print(f"=====================================\n")

        driver = u2.connect()
        driver.app_stop(APP_PACKAGE_NAME)
        time.sleep(1)
        driver.app_start(APP_PACKAGE_NAME, stop=True)
        time.sleep(SLEEP_DEFAULT)

        run_all_test_cases(driver)

        driver.app_stop(APP_PACKAGE_NAME)
        time.sleep(2)
        print(f"\n✅ 第 {i} 轮执行完成")

        refresh_test_params()
        time.sleep(case_interval_seconds)

    print("\n🎉 所有压力测试轮次全部执行完毕！")