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
APP_PACKAGE_NAME = "com.oymotion.synchronympro"

# ====================== 超时时间 ======================
WAIT_TIMEOUT_VERY_SHORT = 2
WAIT_TIMEOUT_SHORT = 5
WAIT_TIMEOUT_NORMAL = 10
WAIT_TIMEOUT_LONG = 15

# ====================== 休眠时间 ======================
SLEEP_DEFAULT = 2
SLEEP_COLLECT = 10

# ====================== 页面文字 ======================
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

# ====================== OCR 校验关键字 ======================
OCR_KEY_PRODUCT_INFO = ["设备地址"]
OCR_KEY_ABOUT_PAGE = ["软件名称"]

# ====================== 全局配置 ======================
# 开关点击偏移量（根据你的设备分辨率修改）
# 1200*2000 Pad → 450
# 其他设备 → 自己测试后改这里
SWITCH_OFFSET_X = 450
# ======================================================

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
    """
    增强版：支持偏移点击，专门点复选框/开关
    :param offset_x: 水平偏移（正数向右，负数向左）
    :param offset_y: 垂直偏移（正数向下，负数向上）
    """
    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()

        img = driver.screenshot()
        img.save("tmp_screenshot.png")
        results, _ = _ocr("tmp_screenshot.png")

        for item in results:
            box = item[0]
            text = item[1]

            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]

            x1 = min(x_coords)
            y1 = min(y_coords)
            x2 = max(x_coords)
            y2 = max(y_coords)

            if target_text in text:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                final_x = cx + offset_x
                final_y = cy + offset_y

                driver.click(final_x, final_y)
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
    is_connected = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_LONG)
    assert is_connected, "❌ 设备连接失败"

def test_navigate_to_waveform(device_driver):
    """进入波形界面"""
    device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_WAVEFORM).click()
    time.sleep(SLEEP_DEFAULT)
    is_page_open = device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_page_open, "❌ 进入波形页面失败"

def test_filter_choose(device_driver):
    """测试滤波开关"""
    device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_START).click()
    time.sleep(SLEEP_DEFAULT)

    # 50Hz滤除：打开 → 关闭
    assert click_text_by_ocr(device_driver, "50Hz滤除", offset_x=SWITCH_OFFSET_X), "50Hz滤除 点击失败"
    time.sleep(SLEEP_DEFAULT)
    assert click_text_by_ocr(device_driver, "50Hz滤除", offset_x=SWITCH_OFFSET_X), "50Hz滤除 点击失败"
    time.sleep(SLEEP_DEFAULT)

    # 60Hz滤除：打开 → 关闭
    assert click_text_by_ocr(device_driver, "60Hz滤除", offset_x=SWITCH_OFFSET_X), "60Hz滤除 点击失败"
    time.sleep(SLEEP_DEFAULT)
    assert click_text_by_ocr(device_driver, "60Hz滤除", offset_x=SWITCH_OFFSET_X), "60Hz滤除 点击失败"
    time.sleep(SLEEP_DEFAULT)

    # HPF：打开 → 关闭
    assert click_text_by_ocr(device_driver, "HPF", offset_x=SWITCH_OFFSET_X), "HPF 点击失败"
    time.sleep(SLEEP_DEFAULT)
    assert click_text_by_ocr(device_driver, "HPF", offset_x=SWITCH_OFFSET_X), "HPF 点击失败"
    time.sleep(SLEEP_DEFAULT)

    # LPF：打开 → 关闭
    assert click_text_by_ocr(device_driver, "LPF", offset_x=SWITCH_OFFSET_X), "LPF 点击失败"
    time.sleep(SLEEP_DEFAULT)
    assert click_text_by_ocr(device_driver, "LPF", offset_x=SWITCH_OFFSET_X), "LPF 点击失败"
    time.sleep(SLEEP_DEFAULT)

def test_start_data_collection(device_driver):
    """开始数据采集"""
    # device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    # device_driver(description=DESC_START).click()
    # time.sleep(SLEEP_DEFAULT)

    swipe_to_bottom(device_driver)

    device_driver(description=DESC_DATA_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DATA_COLLECT_BDF).click()
    time.sleep(SLEEP_DEFAULT)

    click_if_exists(device_driver, DESC_ALWAYS_ALLOW)

    collect_running = device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert collect_running, "❌ 采集开启失败"

def test_stop_data_collection(device_driver):
    """停止数据采集"""
    time.sleep(SLEEP_COLLECT)
    device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_STOP_COLLECT_BDF).click()
    time.sleep(SLEEP_DEFAULT)

    stop_success = device_driver(description=DESC_CONFIRM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert stop_success, "❌ 停止采集失败"

    device_driver(description=DESC_CONFIRM).click()
    time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    is_back_success = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_success, "❌ 返回设备页面失败"

@pytest.mark.skip('skpi test_enter_data_distribution')
def test_enter_data_distribution(device_driver):
    """进入数据分发页面"""
    device_driver(description=DESC_DATA_DISTRIBUTION_LSL).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DATA_DISTRIBUTION_LSL).click()
    time.sleep(SLEEP_DEFAULT)

    click_if_exists(device_driver, DESC_ALLOW_WHEN_USING, timeout=WAIT_TIMEOUT_VERY_SHORT)
    time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

def test_check_product_info(device_driver):
    """查看产品信息"""
    device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
    time.sleep(SLEEP_DEFAULT)

    page_text = get_page_text(device_driver)
    assert any(kw in page_text for kw in OCR_KEY_PRODUCT_INFO), "❌ 产品信息页面异常"

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

def test_enter_about_page(device_driver):
    """进入关于页面"""
    device_driver(description=DESC_ABOUT).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_ABOUT).click()
    time.sleep(SLEEP_DEFAULT)

    page_text = get_page_text(device_driver)
    assert any(kw in page_text for kw in OCR_KEY_ABOUT_PAGE), "❌ 关于页面内容异常"
    time.sleep(SLEEP_DEFAULT)
    # assert click_text_by_ocr(device_driver, OCR_KEY_ABOUT_PAGE[0])
    # time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)


# ========================= 统一用例入口 =========================
def run_all_test_cases(device_driver):
    """一轮完整测试流程（所有业务用例）"""
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
@pytest.mark.skip(' skip test_main_auto_run')
def test_main_auto_run():
    """压力测试（每次循环重启APP）"""
    import uiautomator2 as u2
    refresh_test_params()
    print(f"\n🚀 开始执行压力测试，总轮次：{execute_total_times}")

    for i in range(1, execute_total_times + 1):
        check_test_stop_pause()
        print(f"\n=====================================")
        print(f"📌 第 {i}/{execute_total_times} 轮测试开始")
        print(f"=====================================\n")

        # ==============================================
        # ✅ 每次循环都：重启 APP
        # ==============================================
        driver = u2.connect()
        driver.app_stop(APP_PACKAGE_NAME)
        time.sleep(1)
        driver.app_start(APP_PACKAGE_NAME, stop=True)
        time.sleep(SLEEP_DEFAULT)

        # 执行一轮全量用例
        run_all_test_cases(driver)

        # 关闭 APP，准备下一轮重启
        driver.app_stop(APP_PACKAGE_NAME)
        time.sleep(2)

        print(f"\n✅ 第 {i} 轮执行完成")
        refresh_test_params()
        time.sleep(case_interval_seconds)

    print("\n🎉 所有压力测试轮次全部执行完毕！")