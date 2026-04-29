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

# ====================== 校验关键字 ======================
DEVICE_ADDRESS = "设备地址"
SOFTWARE_NAME = "软件名称"

# ====================== 滤波开关定义 ======================
DESC_50HZ_FILTER = "50Hz滤除："
DESC_60HZ_FILTER = "60Hz滤除："
DESC_HPF_FILTER = "HPF："
DESC_LPF_FILTER = "LPF ："

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
    time.sleep(SLEEP_DEFAULT*2)
    is_connected = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_LONG)
    assert is_connected, "❌ 设备连接失败"

def test_navigate_to_waveform(device_driver):
    """进入波形界面"""
    device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_WAVEFORM).click()
    time.sleep(SLEEP_DEFAULT)
    is_page_open = device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_page_open, "❌ 进入波形页面失败"

# def test_filter_choose(device_driver):
#     """测试滤波开关"""
#     device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
#     device_driver(description=DESC_START).click()
#     time.sleep(SLEEP_DEFAULT)
#
#     # 50Hz滤除：打开 → 关闭
#     assert click_text_by_ocr(device_driver, "50Hz滤除", offset_x=SWITCH_OFFSET_X), "50Hz滤除 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#     assert click_text_by_ocr(device_driver, "50Hz滤除", offset_x=SWITCH_OFFSET_X), "50Hz滤除 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#
#     # 60Hz滤除：打开 → 关闭
#     assert click_text_by_ocr(device_driver, "60Hz滤除", offset_x=SWITCH_OFFSET_X), "60Hz滤除 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#     assert click_text_by_ocr(device_driver, "60Hz滤除", offset_x=SWITCH_OFFSET_X), "60Hz滤除 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#
#     # HPF：打开 → 关闭
#     assert click_text_by_ocr(device_driver, "HPF", offset_x=SWITCH_OFFSET_X), "HPF 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#     assert click_text_by_ocr(device_driver, "HPF", offset_x=SWITCH_OFFSET_X), "HPF 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#
#     # LPF：打开 → 关闭
#     assert click_text_by_ocr(device_driver, "LPF", offset_x=SWITCH_OFFSET_X), "LPF 点击失败"
#     time.sleep(SLEEP_DEFAULT)
#     assert click_text_by_ocr(device_driver, "LPF", offset_x=SWITCH_OFFSET_X), "LPF 点击失败"
#     time.sleep(SLEEP_DEFAULT)
def test_filter_choose(device_driver):
    """测试滤波开关操作"""
    # 步骤1：校验返回按钮存在并点击（确认页面加载完成）
    device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_START).click()
    time.sleep(SLEEP_DEFAULT)

    # ========== 50Hz滤除开关 ==========
    assert device_driver(description=DESC_50HZ_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到50Hz滤除文本元素"
    filter_50hz_xpath = device_driver.xpath('//android.widget.Switch[1]')
    assert filter_50hz_xpath.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到50Hz滤除开关"

    # 点击：获取控件范围 → 点右侧 85%
    x1, y1, x2, y2 = filter_50hz_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    filter_50hz_switch = filter_50hz_xpath.get()
    assert filter_50hz_switch.attrib["checked"] == "false", "❌ 50Hz滤除开关关闭失败"

    # 恢复
    x1, y1, x2, y2 = filter_50hz_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    filter_50hz_switch = filter_50hz_xpath.get()
    assert filter_50hz_switch.attrib["checked"] == "true", "❌ 50Hz滤除开关恢复失败"

    # ========== 60Hz滤除开关 ==========
    assert device_driver(description=DESC_60HZ_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到60Hz滤除文本元素"
    filter_60hz_xpath = device_driver.xpath('//android.widget.Switch[@index="1"]')
    assert filter_60hz_xpath.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到60Hz滤除开关"

    x1, y1, x2, y2 = filter_60hz_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    filter_60hz_switch = filter_60hz_xpath.get()
    assert filter_60hz_switch.attrib["checked"] == "false", "❌ 60Hz滤除开关关闭失败"

    x1, y1, x2, y2 = filter_60hz_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    filter_60hz_switch = filter_60hz_xpath.get()
    assert filter_60hz_switch.attrib["checked"] == "true", "❌ 60Hz滤除开关恢复失败"

    # ========== HPF开关 ==========
    assert device_driver(description=DESC_HPF_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到HPF文本元素"
    hpf_xpath = device_driver.xpath('//android.widget.Switch[@index="2"]')
    assert hpf_xpath.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到HPF开关"

    x1, y1, x2, y2 = hpf_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    hpf_switch = hpf_xpath.get()
    assert hpf_switch.attrib["checked"] == "false", "❌ HPF开关关闭失败"

    x1, y1, x2, y2 = hpf_xpath.bounds
    device_driver.click(int(x1 + (x2-x1)*0.85), (y1+y2)//2)
    time.sleep(SLEEP_DEFAULT)
    hpf_switch = hpf_xpath.get()
    assert hpf_switch.attrib["checked"] == "true", "❌ HPF开关恢复失败"

    # ========== LPF开关 ==========
    assert device_driver(description=DESC_LPF_FILTER).wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到LPF文本元素"
    lpf_xpath = device_driver.xpath('//android.widget.Switch[@index="3"]')
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

    print("✅ 所有滤波开关操作测试通过")

def test_switch_all_views(device_driver):
    """波形界面：切换视图"""

    # 右上角菜单按钮（保留你原来的写法）
    menu_btn = device_driver.xpath('//*[@content-desc="波形图"]/following-sibling::android.widget.Button[1]')
    assert menu_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到菜单按钮"

    # 默认已是波形图
    print("✅ 默认视图：波形图")

    # ---------------------- 切换 IMU视图 ----------------------
    menu_btn.click()
    device_driver(description="IMU视图").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="IMU视图").click()
    print("✅ 切换到：IMU视图")

    # ---------------------- 切换 FFT视图 ----------------------
    menu_btn = device_driver.xpath('//*[@content-desc="IMU视图"]/following-sibling::android.widget.Button[1]')
    assert menu_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到菜单按钮"
    menu_btn.click()
    device_driver(description="FFT视图").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="FFT视图").click()
    print("✅ 切换到：FFT视图")

    # ---------------------- 切换 直方图 ----------------------
    menu_btn = device_driver.xpath('//*[@content-desc="FFT视图"]/following-sibling::android.widget.Button[1]')
    assert menu_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到菜单按钮"
    menu_btn.click()
    device_driver(description="直方图").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="直方图").click()
    print("✅ 切换到：直方图")

    # ---------------------- 切回 波形图 ----------------------
    menu_btn = device_driver.xpath('//*[@content-desc="直方图"]/following-sibling::android.widget.Button[1]')
    assert menu_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到菜单按钮"
    menu_btn.click()
    device_driver(description="波形图").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="波形图").click()
    print("✅ 切回默认：波形图")

    print("\n✅ 所有视图切换完成")

def test_wave_zoom_out(device_driver):
    """波形页面-放大按钮"""

    zoom_out_btn = device_driver.xpath(
        '//android.view.View[@scrollable="true"]'
        '/android.view.View[1]'
        '/android.view.View[2]'
    )

    zoom_out_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    zoom_out_btn.click()

    time.sleep(SLEEP_DEFAULT)
    print("✅ 放大按钮测试完成（纯层级定位）")

def test_wave_unit_switch(device_driver):
    """波形页面-单位切换：μV ↔ mV"""
    # 定位 RadioButton：μV、mV
    unit_mv = device_driver.xpath('//android.widget.RadioButton[1]')
    unit_mv.wait(timeout=WAIT_TIMEOUT_NORMAL)

    unit_uv = device_driver.xpath('//android.widget.RadioButton[2]')
    unit_uv.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 切换到 mV
    unit_uv.click()
    time.sleep(SLEEP_DEFAULT)
    # 断言：单位切换到 mV 成功
    assert unit_uv.wait(timeout=SLEEP_DEFAULT), "❌ 切换到 mV 失败"

    # 再切回 μV（默认）
    unit_mv.click()
    time.sleep(SLEEP_DEFAULT)
    # 断言：单位恢复到 μV 成功
    assert unit_mv.wait(timeout=SLEEP_DEFAULT), "❌ 恢复到 μV 失败"

    print("✅ 单位切换测试完成：mV → 恢复默认μV")


def test_wave_voltage_setting(device_driver):
    """波形页面-电压值"""
    # 电压按钮（从你XML真实获取：Button[2]）
    voltage_btn = device_driver.xpath('//android.widget.Button[1]')
    voltage_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 电压值选项（和你界面一致）
    voltage_list = [
        "-10~10",
        "-20~20",
        "-50~50",
        "-100~100",
        "-200~200",
        "-500~500",
        "-1000~1000",
        "-2000~2000",
        "-5000~5000"
    ]
    selected = random.sample(voltage_list, 3)

    # 随机选择3个（写法和时长完全一致）
    for val in selected:
        voltage_btn.click()
        time.sleep(2)
        device_driver(description=val).wait(timeout=SLEEP_DEFAULT)
        device_driver(description=val).click()
        time.sleep(5)

    # 恢复默认：自适应（完全和你时长写法对齐）
    voltage_btn.click()
    time.sleep(1)
    device_driver(description="自适应").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="自适应").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 电压值测试完成：随机3个范围 → 恢复默认自适应")

def test_wave_eeg_filter_setting(device_driver):
    """波形页面-EEG滤波设置"""
    # EEG滤波按钮（从你XML真实获取：Button[1]，对应index=1）
    filter_btn = device_driver.xpath('//android.widget.Button[2]')
    filter_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 滤波选项（和你界面完全一致）
    filter_list = [
        "δ(0.5~4 Hz)",
        "θ(4~8 Hz)",
        "α (8~13 Hz)",
        "β (13~30 Hz)",
        "γ (30~45 Hz)",
        "标准(0.5~45 HZ)"
    ]
    selected = random.sample(filter_list, 3)

    # 随机选择3个（写法和电压/时长完全一致）
    for val in selected:
        filter_btn.click()
        time.sleep(2)
        device_driver(description=val).wait(timeout=SLEEP_DEFAULT)
        device_driver(description=val).click()
        time.sleep(5)

    # 恢复默认：无（和电压恢复写法对齐）
    filter_btn.click()
    time.sleep(1)
    device_driver(description="无").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="无").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ EEG滤波测试完成：随机3个选项 → 恢复默认无")

def test_wave_duration_setting(device_driver):
    """波形页面-时长"""
    # 打开时长按钮
    duration_btn = device_driver.xpath('//android.widget.Button[3]')
    duration_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    # 时长选项顺序
    duration_list = ["1s", "2s", "5s", "10s", "20s", "30s", "60s"]
    selected = random.sample(duration_list, 3)

    for val  in selected:
        duration_btn.click()
        time.sleep(2)
        device_driver(description=val).wait(timeout=SLEEP_DEFAULT)
        device_driver(description=val).click()
        time.sleep(5)

    # 恢复默认 500ms
    duration_btn.click()
    time.sleep(0.8)
    device_driver(description="500ms").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="500ms").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 时长测试完成：随机3个 → 恢复默认500ms")


def test_switch_channel_right(device_driver):
    """波形页面-向右箭头切换通道"""
    right_arrow = device_driver.xpath('//android.widget.Button[4]')
    right_arrow.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 点击向右切换
    for ch in range(1, 8):
        right_arrow.click()
        time.sleep(5)
        right_arrow = device_driver.xpath('//android.widget.Button[5]')

    # 断言：按钮可点击，操作成功
    assert right_arrow.wait(timeout=SLEEP_DEFAULT), "❌ 向右切换通道失败"

    print("✅ 向右切换通道测试完成")

# def test_recovery_default_freq(device_driver):
#     """波形页面-恢复默认频率"""
#     recovery_default_freq = device_driver.xpath('//android.widget.Button[5]')
#     recovery_default_freq.wait(timeout=WAIT_TIMEOUT_NORMAL)
#
#
#     recovery_default_freq.click()
#     time.sleep(SLEEP_DEFAULT)
#
#     # 断言：按钮可点击，操作成功
#     assert recovery_default_freq.wait(timeout=SLEEP_DEFAULT), "❌ 恢复默认频率测试fail"
#
#     print("✅ 恢复默认频率测试完成")

def test_switch_pause_resume(device_driver):
    """波形页面-暂停/开始"""
    pause_resume = device_driver.xpath('//android.widget.Button[6]')
    pause_resume.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 点击向右切换
    for i in range(1,3):
        pause_resume.click()
        time.sleep(SLEEP_DEFAULT)

    # 断言：按钮可点击，操作成功
    assert pause_resume.wait(timeout=SLEEP_DEFAULT), "❌ 暂停开始测试fail"

    print("✅ 暂停开启测试完成")

def test_wave_zoom_in(device_driver):
    """波形页面-缩小按钮"""
    zoom_in_btn = device_driver.xpath('//android.widget.Button[@content-desc="缩小"]')

    # 等待元素加载
    zoom_in_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 点击缩小按钮
    zoom_in_btn.click()

    time.sleep(SLEEP_DEFAULT)

    zoom_out_btn = device_driver.xpath(
        '//android.view.View[@scrollable="true"]'
        '/android.view.View[1]'
        '/android.view.View[2]'
    )
    # 断言按钮存在，操作成功
    assert  zoom_out_btn.wait(timeout=SLEEP_DEFAULT), "❌ 回到缩小界面失败"

    print("✅ 缩小按钮测试完成")


def test_start_data_collection(device_driver):
    """开始数据采集"""
    swipe_to_bottom(device_driver)

    device_driver(description=DESC_DATA_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DATA_COLLECT_BDF).click()
    time.sleep(WAIT_TIMEOUT_NORMAL)

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

    assert device_driver(descriptionContains=DEVICE_ADDRESS).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入产品信息页面"

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

def test_enter_about_page(device_driver):
    """进入关于页面"""
    device_driver(description=DESC_ABOUT).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_ABOUT).click()
    time.sleep(SLEEP_DEFAULT)

    assert device_driver(descriptionContains=SOFTWARE_NAME).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入关于页面"
    time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"


# ========================= 统一用例入口 =========================
def run_all_test_cases(device_driver):
    """一轮完整测试流程（所有业务用例）"""
    test_agree_privacy_policy(device_driver)
    test_start_device_scan(device_driver)
    test_connect_first_detected_device(device_driver)
    test_navigate_to_waveform(device_driver)
    test_filter_choose(device_driver)
    test_switch_all_views(device_driver)
    # 波形界面新增case
    test_wave_zoom_out(device_driver)
    test_wave_unit_switch(device_driver)
    test_wave_voltage_setting(device_driver)
    test_wave_duration_setting(device_driver)
    test_wave_eeg_filter_setting(device_driver)
    test_switch_channel_right(device_driver)
    test_switch_pause_resume(device_driver)
    test_wave_zoom_in(device_driver)

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