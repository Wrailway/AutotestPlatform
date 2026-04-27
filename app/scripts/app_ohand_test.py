# -*- coding: utf-8 -*-
"""
设备连接自动化测试
流程：启动APP → 同意隐私协议 → 扫描设备 → 连接设备 → 关闭APP
全局控制：支持暂停、停止、动态参数刷新
"""
import random
import uiautomator2 as u2
import pytest
import time

from app.app_common import OperateSharedData

# ====================== 全局配置常量 ======================
APP_PACKAGE_NAME = "com.oymotion.ohand_app"

# 超时时间
WAIT_TIMEOUT_VERY_SHORT = 2
WAIT_TIMEOUT_SHORT = 5
WAIT_TIMEOUT_NORMAL = 10
WAIT_TIMEOUT_LONG = 15

# 休眠时间
SLEEP_DEFAULT = 2
SLEEP_COLLECT = 10

# 页面描述/文本常量
DESC_VIEW_WAVEFORM = "波形/阈值"
DESC_CONNECT = "连接"
DESC_FIND_DEVICE = "查找设备"
DESC_READY = "就绪"
DESC_START = "开始"
TEXT_BTN_CONFIRM = "确定"
DESC_VIEW_PRODUCT_INFO = "查看产品信息"
DESC_ABOUT = "关于"
DESC_DEBUG_INFO = "查看调试信息"
DESC_GESTURE_SETTINGS = "手势设置"
DESC_DEVICE_CONTROL = "设备控制"
DESC_CLOUD_SETTINGS = "云端设置"
DESC_BUZZER_TITLE = "蜂鸣器开关"
DESC_POWER_OFF_TITLE = "关闭电源"
DESC_BTN_SHUTDOWN = "关机"
TEXT_BTN_EXPAND = "展开"
TEXT_FLEXOR_LABEL = "屈肌信号阈值"
TEXT_EXTENSOR_LABEL = "伸肌信号阈值"
TEXT_RESTORE_DEFAULT = "恢复默认设置"

# 校验关键字
DEVICE_ADDRESS_KEY = "设备地址"
SOFTWARE_NAME_KEY = "软件名称"

# 波形类型常量
WAVE_TYPE_NONE = "NONE"
WAVE_TYPE_EMG = "EMG"
WAVE_TYPE_RAW = "RAW"
WAVE_TYPE_DC = "DC"
WAVE_TYPE_AC = "AC"

# 传感器类型常量
SENSOR_NORMAL = "普通肌电传感器"
SENSOR_BUTTON = "按钮开关/包络线传感器"

# 页面偏移配置
SWITCH_OFFSET_X = 450

# ====================== 公共工具函数 ======================
def back_page(driver, sleep_sec: int = SLEEP_DEFAULT):
    """
    统一封装：物理返回按键
    :param driver: u2设备驱动
    :param sleep_sec: 返回后休眠时长
    """
    driver.press("back")
    time.sleep(sleep_sec)

def check_test_stop_pause():
    """检查测试暂停/停止"""
    is_stop, is_pause = OperateSharedData.read_control()
    if is_stop:
        pytest.exit("🛑 测试已手动停止")

    while is_pause:
        for _ in range(10):
            time.sleep(0.2)
            is_stop, is_pause = OperateSharedData.read_control()
            if is_stop:
                pytest.exit("🛑 测试已手动停止")

# 全局动态参数
execute_total_times = 1
case_interval_seconds = 2

def refresh_test_params():
    """刷新动态配置参数"""
    global execute_total_times, case_interval_seconds
    execute_total_times, case_interval_seconds = OperateSharedData.read_params()

# ====================== 测试夹具 ======================
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

# ====================== 底层工具方法 ======================
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
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            x1, y1 = min(x_coords), min(y_coords)
            x2, y2 = max(x_coords), max(y_coords)
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
    click_if_exists(device_driver, TEXT_BTN_CONFIRM, timeout=WAIT_TIMEOUT_SHORT)

def test_start_device_scan(device_driver):
    """扫描设备"""
    MAX_RETRY = 3
    found_device = False
    for _ in range(MAX_RETRY):
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
    """进入波形/阈值"""
    device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_WAVEFORM).click()
    time.sleep(SLEEP_DEFAULT)

def test_waveform_type_switch(device_driver):
    """波形类型切换"""
    assert device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=10), "❌ 未进入波形/阈值页面"
    random_options = [WAVE_TYPE_RAW, WAVE_TYPE_DC, WAVE_TYPE_AC]
    selected_random = random.choice(random_options)

    if device_driver(description=WAVE_TYPE_NONE).wait(timeout=2):
        current_btn = device_driver(description=WAVE_TYPE_NONE)
    elif device_driver(description=WAVE_TYPE_EMG).wait(timeout=2):
        current_btn = device_driver(description=WAVE_TYPE_EMG)
    elif device_driver(description=WAVE_TYPE_RAW).wait(timeout=2):
        current_btn = device_driver(description=WAVE_TYPE_RAW)
    elif device_driver(description=WAVE_TYPE_DC).wait(timeout=2):
        current_btn = device_driver(description=WAVE_TYPE_DC)
    else:
        current_btn = device_driver(description=WAVE_TYPE_AC)

    current_btn.click()
    time.sleep(1)
    device_driver(description=WAVE_TYPE_NONE).wait(timeout=5)
    device_driver(description=WAVE_TYPE_NONE).click()
    time.sleep(2)
    assert device_driver(description=WAVE_TYPE_NONE).wait(timeout=5), "❌ 切换到NONE失败"

    device_driver(description=WAVE_TYPE_NONE).click()
    time.sleep(1)
    device_driver(description=selected_random).wait(timeout=5)
    device_driver(description=selected_random).click()
    time.sleep(2)
    assert device_driver(description=selected_random).wait(timeout=5), f"❌ 切换到{selected_random}失败"

    device_driver(description=selected_random).click()
    time.sleep(1)
    device_driver(description=WAVE_TYPE_EMG).wait(timeout=5)
    device_driver(description=WAVE_TYPE_EMG).click()
    time.sleep(2)
    assert device_driver(description=WAVE_TYPE_EMG).wait(timeout=5), "❌ 切换到EMG失败"
    print(f"✅ 波形类型切换完成！随机选择了：{selected_random}，最终切换到EMG！")

def test_sensor_type_switch(device_driver):
    """传感器类型切换"""
    assert device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=10), "❌ 未进入波形/阈值页面"
    if device_driver(description=SENSOR_NORMAL).wait(timeout=2):
        sensor = device_driver(description=SENSOR_NORMAL)
    else:
        sensor = device_driver(description=SENSOR_BUTTON)
    assert sensor.wait(timeout=5), "❌ 未找到传感器按钮"
    sensor.click()
    time.sleep(1)

    target_option = device_driver(description=SENSOR_BUTTON)
    assert target_option.wait(timeout=5), "❌ 未找到选项"
    target_option.click()
    time.sleep(2)
    assert device_driver(description=SENSOR_BUTTON).wait(timeout=5), "❌ 切换失败"

    sensor_switch = device_driver(description=SENSOR_BUTTON)
    sensor_switch.click()
    time.sleep(1)
    back_option = device_driver(description=SENSOR_NORMAL)
    back_option.click()
    time.sleep(2)
    assert device_driver(description=SENSOR_NORMAL).wait(timeout=10), "❌ 恢复失败"
    print("✅ 传感器类型切换 测试通过！")

def test_flexor_seekbar_swipe(device_driver):
    """屈肌信号阈值"""
    assert device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=10), "页面错误"
    label = device_driver(description=TEXT_FLEXOR_LABEL)
    seekbar = label.sibling(className="android.widget.SeekBar")[0]
    seekbar.wait(timeout=5)
    seekbar.swipe("down", 0.0)
    time.sleep(0.5)
    seekbar.swipe("up", 1.0)
    time.sleep(0.5)
    print("✅ 屈肌【上方】滑动条 测试通过！")

def test_extensor_seekbar_swipe(device_driver):
    """伸肌信号阈值"""
    assert device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=10), "页面错误"
    label = device_driver(description=TEXT_EXTENSOR_LABEL)
    seekbar = label.sibling(className="android.widget.SeekBar")[1]
    seekbar.wait(timeout=5)
    seekbar.swipe("down", 0.0)
    time.sleep(0.5)
    seekbar.swipe("up", 1.0)
    time.sleep(0.5)
    # 替换为封装的返回函数
    back_page(device_driver)
    print("✅ 伸肌【下方】滑动条 测试通过！")

def test_enter_gesture_settings(device_driver):
    """进入手势设置"""
    device_driver(description=DESC_GESTURE_SETTINGS).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_GESTURE_SETTINGS).click()
    time.sleep(SLEEP_DEFAULT)
    back_page(device_driver)

def test_enter_device_control(device_driver):
    """进入设备控制"""
    device_driver(description=DESC_DEVICE_CONTROL).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DEVICE_CONTROL).click()
    time.sleep(SLEEP_DEFAULT)


def test_buzzer_switch_control(device_driver):
    """蜂鸣器开关"""
    # 等待页面加载
    assert device_driver(description=DESC_DEVICE_CONTROL).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入设备控制页面"

    # 直接定位蜂鸣器开关（最简单稳定）
    buzzer_switch = device_driver(className="android.widget.Switch")
    assert buzzer_switch.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到蜂鸣器开关"

    # 获取当前状态
    original_status = buzzer_switch.info.get("checked", False)

    # 点击开关
    buzzer_switch.click()
    time.sleep(SLEEP_DEFAULT*2)

    # 校验状态变化
    new_status = buzzer_switch.info.get("checked", False)
    assert new_status != original_status, "❌ 蜂鸣器开关状态未改变"

    # 切回原状态，不影响后续测试
    buzzer_switch.click()
    time.sleep(SLEEP_DEFAULT)
    print("✅ 蜂鸣器开关 测试通过")

@pytest.mark.skip('skip test_device_shutdown_btn')
def test_device_shutdown_btn(device_driver):
    """关机按钮（标准点击版）"""
    # 确保在设备控制页面
    device_driver(description=DESC_DEVICE_CONTROL).wait(timeout=5)

    # 标准点击 关机 按钮
    device_driver(description=DESC_BTN_SHUTDOWN).click()
    time.sleep(2)

    # 点击确认弹窗
    device_driver(text="确定").wait(timeout=3)
    device_driver(text="确定").click()

    print("✅ 关机操作已执行")

def test_device_control_actions(device_driver):
    """设备控制27个手势"""
    assert device_driver(description=DESC_DEVICE_CONTROL).wait(timeout=10), "未进入设备控制页面"
    gesture_images = device_driver(className="android.widget.ImageView", clickable=True)
    print('第一屏手势数量:', gesture_images.count)
    device_driver(description=TEXT_BTN_EXPAND).click()
    time.sleep(1)

    device_driver(description=TEXT_BTN_CONFIRM).click()
    time.sleep(2)
    if device_driver(description=TEXT_BTN_CONFIRM).wait(timeout=2):
        device_driver(description=TEXT_BTN_CONFIRM).click()
        time.sleep(1)

    for i in range(21):
        check_test_stop_pause()
        gesture_images[i].click()
        time.sleep(1)
        device_driver(description=TEXT_BTN_CONFIRM).click()
        time.sleep(2)
        if device_driver(description=TEXT_BTN_CONFIRM).wait(timeout=2):
            device_driver(description=TEXT_BTN_CONFIRM).click()
            time.sleep(1)
        print(f"✅ 第一屏 第 {i+1}/21 项执行完成")

    print("ℹ️ 第一屏完成，开始向上滑动...")
    device_driver.swipe(0.5, 0.8, 0.5, 0.2, 0.5)
    time.sleep(2)

    gesture_images_after_swipe = device_driver(className="android.widget.ImageView", clickable=True)
    for i in range(15, gesture_images_after_swipe.count):
        check_test_stop_pause()
        gesture_images_after_swipe[i].click()
        time.sleep(1)
        device_driver(description=TEXT_BTN_CONFIRM).click()
        time.sleep(2)
        if device_driver(description=TEXT_BTN_CONFIRM).wait(timeout=2):
            device_driver(description=TEXT_BTN_CONFIRM).click()
            time.sleep(1)
        print(f"✅ 滑动后 第 {i + 1}/{gesture_images_after_swipe.count} 项执行完成")

    print("✅ 设备控制所有动作完成")
    back_page(device_driver)

def test_enter_cloud_settings(device_driver):
    """进入云端设置"""
    device_driver(description=DESC_CLOUD_SETTINGS).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_CLOUD_SETTINGS).click()
    time.sleep(SLEEP_DEFAULT)

def test_restore_default_settings(device_driver):
    """恢复默认设置"""
    assert device_driver(description=DESC_CLOUD_SETTINGS).wait(timeout=10), "未进入设置页面"
    restore_btn = device_driver(description=TEXT_RESTORE_DEFAULT)
    restore_btn.wait(timeout=5)
    restore_btn.click()
    time.sleep(1)
    confirm_ok_btn = device_driver(description=TEXT_BTN_CONFIRM)
    confirm_ok_btn.wait(timeout=5)
    confirm_ok_btn.click()
    time.sleep(2)
    success_ok_btn = device_driver(description=TEXT_BTN_CONFIRM)
    success_ok_btn.wait(timeout=5)
    success_ok_btn.click()
    time.sleep(1)
    back_page(device_driver)
    print("✅ 恢复默认设置 完整流程执行成功（含两个弹窗确认）")

def test_check_product_info(device_driver):
    """查看产品信息"""
    device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
    time.sleep(SLEEP_DEFAULT)
    assert device_driver(descriptionContains=DEVICE_ADDRESS_KEY).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入产品信息页面"
    back_page(device_driver)
    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

def test_enter_debug_page(device_driver):
    """进入关于页面"""
    device_driver(description=DESC_DEBUG_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DEBUG_INFO).click()
    time.sleep(SLEEP_DEFAULT)
    back_page(device_driver)
    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

# ========================= 统一用例入口 =========================
def run_all_test_cases(device_driver):
    """一轮完整测试流程（所有业务用例）"""
    test_agree_privacy_policy(device_driver)
    test_start_device_scan(device_driver)
    test_connect_first_detected_device(device_driver)
    test_navigate_to_waveform(device_driver)

    test_waveform_type_switch(device_driver)
    test_sensor_type_switch(device_driver)
    test_flexor_seekbar_swipe(device_driver)
    test_extensor_seekbar_swipe(device_driver)

    test_enter_gesture_settings(device_driver)
    test_enter_device_control(device_driver)
    test_buzzer_switch_control(device_driver)
    test_device_control_actions(device_driver)

    test_enter_cloud_settings(device_driver)
    test_restore_default_settings(device_driver)

    test_check_product_info(device_driver)
    test_enter_debug_page(device_driver)

# ========================= 主测试函数 =========================
@pytest.mark.skip(' skip test_main_auto_run')
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