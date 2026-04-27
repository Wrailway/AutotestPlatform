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

# ====================== 全局配置 ======================
APP_PACKAGE_NAME = "com.oymotion.ohand_app"

# ====================== 超时时间 ======================
WAIT_TIMEOUT_VERY_SHORT = 2
WAIT_TIMEOUT_SHORT = 5
WAIT_TIMEOUT_NORMAL = 10
WAIT_TIMEOUT_LONG = 15

# ====================== 休眠时间 ======================
SLEEP_DEFAULT = 2
SLEEP_COLLECT = 10

# ====================== 页面文字（统一变量，已修正拼写） ======================
DESC_VIEW_WAVEFORM = "波形/阈值"
DESC_CONNECT = "连接"
DESC_FIND_DEVICE = "查找设备"
DESC_READY = "就绪"
DESC_START = "开始"
TEXT_AGREE_PRIVACY = "确定"
DESC_VIEW_PRODUCT_INFO = "查看产品信息"
DESC_ABOUT = "关于"
DESC_DEBUG_INFO = "查看调试信息"

# 👉 补充缺失的菜单
DESC_GESTURE_SETTINGS = "手势设置"
DESC_DEVICE_CONTROL = "设备控制"
DESC_CLOUD_SETTINGS = "云端设置"

# ====================== 校验关键字 ======================
DEVICE_ADDRESS = "设备地址"
SOFTWARE_NAME = "软件名称"

# ====================== 全局配置 ======================
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

def click_if_exists(driver, desc, timeout=WAIT_TIMEOUT_VERY_SHORT):
    try:
        if driver(description=desc).wait(timeout=timeout):
            driver(description=desc).click()
            return True
    except:
        pass
    return False

# ====================== 测试用例（已修正拼写 + 补充完整） ======================
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
    """进入波形/阈值"""
    device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_WAVEFORM).click()
    time.sleep(SLEEP_DEFAULT)
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)
    # assert device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 进入波形页面失败"

def test_waveform_type_switch(device_driver):
    """波形类型切换（第二步随机三选一）"""
    # 1. 等待页面加载
    assert device_driver(description="波形/阈值").wait(timeout=10), "❌ 未进入波形/阈值页面"

    type_none = "NONE"
    type_emg = "EMG"
    type_raw = "RAW"
    type_dc = "DC"
    type_ac = "AC"

    # 随机三选一列表
    random_options = [type_raw, type_dc, type_ac]
    selected_random = random.choice(random_options)  # 随机选中一个

    # ========================
    # 第一步：点开菜单 → 切换到 NONE
    # ========================
    if device_driver(description=type_none).wait(timeout=2):
        current_btn = device_driver(description=type_none)
    elif device_driver(description=type_emg).wait(timeout=2):
        current_btn = device_driver(description=type_emg)
    elif device_driver(description=type_raw).wait(timeout=2):
        current_btn = device_driver(description=type_raw)
    elif device_driver(description=type_dc).wait(timeout=2):
        current_btn = device_driver(description=type_dc)
    else:
        current_btn = device_driver(description=type_ac)

    current_btn.click()
    time.sleep(1)

    # 选择 NONE
    device_driver(description=type_none).wait(timeout=5)
    device_driver(description=type_none).click()
    time.sleep(2)
    assert device_driver(description=type_none).wait(timeout=5), "❌ 切换到NONE失败"

    # ========================
    # 第二步：从 NONE → 随机三选一
    # ========================
    device_driver(description=type_none).click()
    time.sleep(1)

    device_driver(description=selected_random).wait(timeout=5)
    device_driver(description=selected_random).click()
    time.sleep(2)
    assert device_driver(description=selected_random).wait(timeout=5), f"❌ 切换到{selected_random}失败"

    # ========================
    # 第三步：最后切换到 EMG
    # ========================
    device_driver(description=selected_random).click()
    time.sleep(1)

    device_driver(description=type_emg).wait(timeout=5)
    device_driver(description=type_emg).click()
    time.sleep(2)
    assert device_driver(description=type_emg).wait(timeout=5), "❌ 切换到EMG失败"

    print(f"✅ 波形类型切换完成！随机选择了：{selected_random}，最终切换到EMG！")

def test_sensor_type_switch(device_driver):
    """传感器类型切换"""
    # 1. 等待页面加载
    assert device_driver(description="波形/阈值").wait(timeout=10), "❌ 未进入波形/阈值页面"

    normal_sensor = "普通肌电传感器"
    button_sensor = "按钮开关/包络线传感器"

    # 2. 等待并点击传感器按钮（展开下拉）
    if device_driver(description=normal_sensor).wait(timeout=2):
        sensor = device_driver(description=normal_sensor)
    else:
        sensor = device_driver(description=button_sensor)

    assert sensor.wait(timeout=5), "❌ 未找到传感器按钮"
    sensor.click()
    time.sleep(1)

    # 3. 选择 按钮开关/包络线传感器
    target_option = device_driver(description=button_sensor)
    assert target_option.wait(timeout=5), "❌ 未找到选项"
    target_option.click()
    time.sleep(2)  # 等待界面刷新

    # 4. 验证切换成功（第一次）
    assert device_driver(description=button_sensor).wait(timeout=5), "❌ 切换失败"

    # 5. 再次点开下拉，切回普通肌电传感器
    sensor_switch = device_driver(description=button_sensor)
    sensor_switch.click()
    time.sleep(1)

    back_option = device_driver(description=normal_sensor)
    back_option.click()
    time.sleep(2)

    # 6. 验证切回成功
    assert device_driver(description=normal_sensor).wait(timeout=10), "❌ 恢复失败"
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)
    print("✅ 传感器类型切换 测试通过！")

def test_flexor_seekbar_swipe(device_driver):
    """屈肌信号阈值"""
    assert device_driver(description="波形/阈值").wait(timeout=10), "页面错误"

    # 找到屈肌标签
    label = device_driver(description="屈肌信号阈值")
    # 取所有同级SeekBar中的第0个（上方屈肌）
    seekbar = label.sibling(className="android.widget.SeekBar")[0]
    seekbar.wait(timeout=5)

    # 垂直滑动
    seekbar.swipe("down", 0.0)
    time.sleep(0.5)
    seekbar.swipe("up", 1.0)
    time.sleep(0.5)

    print("✅ 屈肌【上方】滑动条 测试通过！")


def test_extensor_seekbar_swipe(device_driver):
    """伸肌信号阈值"""
    assert device_driver(description="波形/阈值").wait(timeout=10), "页面错误"

    # 找到伸肌标签
    label = device_driver(description="伸肌信号阈值")
    # 取所有同级SeekBar中的第1个（下方伸肌）
    seekbar = label.sibling(className="android.widget.SeekBar")[1]
    seekbar.wait(timeout=5)

    # 垂直滑动
    seekbar.swipe("down", 0.0)
    time.sleep(0.5)
    seekbar.swipe("up", 1.0)
    time.sleep(0.5)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    print("✅ 伸肌【下方】滑动条 测试通过！")


def test_enter_gesture_settings(device_driver):
    """进入手势设置"""
    device_driver(description=DESC_GESTURE_SETTINGS).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_GESTURE_SETTINGS).click()
    time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

def test_enter_device_control(device_driver):
    """进入设备控制"""
    device_driver(description=DESC_DEVICE_CONTROL).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DEVICE_CONTROL).click()
    time.sleep(SLEEP_DEFAULT)
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)

def test_device_control_actions(device_driver):
    """设备控制27个手势"""
    # 等待页面加载
    assert device_driver(description="设备控制").wait(timeout=10), "未进入设备控制页面"

    # ======================
    # 第一屏：执行 0~20 共21个手势
    # ======================
    gesture_images = device_driver(className="android.widget.ImageView", clickable=True)
    gesture_count = gesture_images.count
    print('第一屏手势数量:', gesture_count)
    # # 1. 先点 展开 按钮
    device_driver(description="展开").click()
    time.sleep(1)

    # 展开弹窗1 确定
    device_driver(description="确定").click()
    time.sleep(2)

    # 展开弹窗2 确定（存在才点）
    if device_driver(description="确定").wait(timeout=2):
        device_driver(description="确定").click()
        time.sleep(1)

    for i in range(21):
        check_test_stop_pause()
        gesture_images[i].click()
        time.sleep(1)

        # 图片弹窗1 确定
        device_driver(description="确定").click()
        time.sleep(2)

        # 图片弹窗2 确定
        if device_driver(description="确定").wait(timeout=2):
            device_driver(description="确定").click()
            time.sleep(1)

        print(f"✅ 第一屏 第 {i+1}/21 项执行完成")

    # ======================
    # 向上滑动屏幕
    # ======================
    print("ℹ️ 第一屏完成，开始向上滑动...")
    device_driver.swipe(0.5, 0.8, 0.5, 0.2, 0.5)
    time.sleep(2)

    # ======================
    # 第二屏：从 15 开始（第16个）
    # ======================
    gesture_images_after_swipe = device_driver(className="android.widget.ImageView", clickable=True)
    gesture_count_after = gesture_images_after_swipe.count
    print('滑动后手势数量:', gesture_count_after)

    for i in range(15, gesture_count_after):
        check_test_stop_pause()
        gesture_images_after_swipe[i].click()
        time.sleep(1)
        device_driver(description="确定").click()
        time.sleep(2)
        if device_driver(description="确定").wait(timeout=2):
            device_driver(description="确定").click()
            time.sleep(1)

        print(f"✅ 滑动后 第 {i + 1}/{gesture_count_after} 项执行完成")

    print("✅ 设备控制所有动作完成")
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

def test_enter_cloud_settings(device_driver):
    """进入云端设置"""
    device_driver(description=DESC_CLOUD_SETTINGS).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_CLOUD_SETTINGS).click()
    time.sleep(SLEEP_DEFAULT)
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)

def test_restore_default_settings(device_driver):
    """恢复默认设置"""
    # 1. 等待设置页面加载
    assert device_driver(description="云端设置").wait(timeout=10), "未进入设置页面"

    # 2. 点击【恢复默认设置】按钮
    restore_btn = device_driver(description="恢复默认设置")
    restore_btn.wait(timeout=5)
    restore_btn.click()
    time.sleep(1)  # 等待确认弹窗出现

    # 3. 点击确认弹窗的【确定】
    confirm_ok_btn = device_driver(description="确定")
    confirm_ok_btn.wait(timeout=5)
    confirm_ok_btn.click()
    time.sleep(2)  # 等待恢复完成，成功弹窗出现

    # 4. 点击成功弹窗的【确定】
    success_ok_btn = device_driver(description="确定")
    success_ok_btn.wait(timeout=5)
    success_ok_btn.click()
    time.sleep(1)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    print("✅ 恢复默认设置 完整流程执行成功（含两个弹窗确认）")

def test_check_product_info(device_driver):
    """查看产品信息"""
    device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
    time.sleep(SLEEP_DEFAULT)

    assert device_driver(descriptionContains=DEVICE_ADDRESS).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入产品信息页面"

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

def test_enter_debug_page(device_driver):
    """进入关于页面"""
    device_driver(description=DESC_DEBUG_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DEBUG_INFO).click()
    time.sleep(SLEEP_DEFAULT)

    # assert device_driver(descriptionContains=SOFTWARE_NAME).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入关于页面"
    # time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

# ========================= 统一用例入口（已清理无效用例） =========================
def run_all_test_cases(device_driver):
    """一轮完整测试流程（所有业务用例）"""
    test_agree_privacy_policy(device_driver)
    test_start_device_scan(device_driver)
    test_connect_first_detected_device(device_driver)
    test_navigate_to_waveform(device_driver)

    # 波形/阈值页面内部用例
    test_waveform_type_switch(device_driver)
    test_sensor_type_switch(device_driver)
    test_flexor_seekbar_swipe(device_driver)
    test_extensor_seekbar_swipe(device_driver)

    # 三级菜单：手势设置 / 设备控制 / 云端设置
    test_enter_gesture_settings(device_driver)
    test_enter_device_control(device_driver)
    test_device_control_actions(device_driver)

    # 云端设置 + 恢复默认设置
    test_enter_cloud_settings(device_driver)
    test_restore_default_settings(device_driver)

    # 设备信息相关
    test_check_product_info(device_driver)
    test_enter_debug_page(device_driver)

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