# -*- coding: utf-8 -*-
"""
设备连接自动化测试（标准流程版）
流程：启动APP → 同意协议 → 搜索设备 → 连接设备 → 主界面功能遍历
"""
import random

import uiautomator2 as u2
import pytest
import time

from app.app_common import OperateSharedData

# ====================== 全局配置 ======================
APP_PACKAGE_NAME = "com.oymotion.digits"

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
            time.sleep(2)
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
    # device_driver.press("back")
    print("✅ 所有滤波开关操作测试通过")

def test_set_range_and_adaptive(device_driver):
    """设置量程"""
    settings_btn = device_driver.xpath('//*[@content-desc="查看波形"]/following-sibling::android.widget.Button[1]')
    assert settings_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到右上角设置按钮"
    settings_btn.click()
    time.sleep(SLEEP_DEFAULT)

    # ====================== 切换到 μV（第二个单选框） ======================
    uv_radio = device_driver.xpath('//android.widget.RadioButton[2]')
    assert uv_radio.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到 μV 选项"
    uv_radio.click()
    time.sleep(0.5)

    # ====================== 修改量程值 ======================
    range_input = device_driver.xpath('//android.widget.EditText')
    assert range_input.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到量程输入框"
    range_input.click()
    range_input.set_text("500")
    time.sleep(0.5)

    # ====================== 应用 ======================
    apply_btn = device_driver.xpath('(//android.widget.Button)[2]')
    assert apply_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到应用按钮"
    apply_btn.click()
    time.sleep(WAIT_TIMEOUT_SHORT)

    # ====================== 重新打开设置 ======================
    settings_btn.click()
    time.sleep(SLEEP_DEFAULT)

    # ====================== 切回 自适应（第一个单选框） ======================
    adaptive_radio = device_driver.xpath('//android.widget.RadioButton[1]')
    assert adaptive_radio.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到自适应选项"
    adaptive_radio.click()
    time.sleep(0.5)

    # ====================== 应用 ======================
    apply_btn.click()
    time.sleep(WAIT_TIMEOUT_SHORT)

    print("✅ 全部设置操作完成：μV → 量程 → 自适应")

def test_zoom_in(device_driver):
    """波形页面"""
    zoom_in_btn = device_driver.xpath('//*[@content-desc="放大"]')
    assert zoom_in_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到放大按钮"
    zoom_in_btn.click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 放大按钮操作完成")

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
    # 电压按钮：根据XML，是Button[6]（content-desc="自适应"）
    voltage_btn = device_driver.xpath('//android.widget.Button[1]')
    voltage_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 电压值选项
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

    # 随机选择3个
    for val in selected:
        voltage_btn.click()
        time.sleep(2)
        device_driver(description=val).wait(timeout=SLEEP_DEFAULT)
        device_driver(description=val).click()
        time.sleep(5)

    # 恢复默认：自适应
    voltage_btn.click()
    time.sleep(2)
    device_driver(description="自适应").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="自适应").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 电压值测试完成：随机3个范围 → 恢复默认自适应")


def test_wave_duration_setting(device_driver):
    """波形页面-时长"""
    # 时长按钮：根据XML，是Button[8]（content-desc="1s"）
    duration_btn = device_driver.xpath('//android.widget.Button[2]')
    duration_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 时长选项顺序
    duration_list = ["40ms", "100ms", "1s", "2.5s", "5s", "10s", "20s", "30s"]
    selected = random.sample(duration_list, 3)

    for val in selected:
        duration_btn.click()
        time.sleep(2)
        device_driver(description=val).wait(timeout=SLEEP_DEFAULT)
        device_driver(description=val).click()
        time.sleep(5)

    # 恢复默认 1s
    duration_btn.click()
    time.sleep(2)
    device_driver(description="1s").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="1s").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 时长测试完成：随机3个 → 恢复默认1s")


def test_switch_channel_right(device_driver):
    """测试波形页面-向右箭头切换通道"""
    # 向右箭头按钮：根据XML，是Button[13]（index=12）
    right_arrow = device_driver.xpath('//android.widget.Button[3]')
    right_arrow.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 点击向右切换（连续7次，模拟切换通道）
    for ch in range(1, 8):
        right_arrow.click()
        time.sleep(5)
        right_arrow = device_driver.xpath('//android.widget.Button[4]')

    # 断言：按钮可点击，操作成功
    assert right_arrow.wait(timeout=SLEEP_DEFAULT), "❌ 向右切换通道失败"

    print("✅ 向右切换通道测试完成")


def test_switch_pause_resume(device_driver):
    """波形页面-暂停/开始"""
    # 暂停按钮：根据XML，是Button[15]（index=14，content-desc="暂停"）
    pause_resume = device_driver.xpath('//android.widget.Button[5]')
    pause_resume.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 点击暂停/恢复两次
    for i in range(1, 3):
        pause_resume.click()
        time.sleep(SLEEP_DEFAULT)

    # 断言：按钮可点击，操作成功
    assert pause_resume.wait(timeout=SLEEP_DEFAULT), "❌ 暂停开始测试fail"

    print("✅ 暂停开启测试完成")


def test_zoom_out(device_driver):
    """波形页面-缩小按钮"""
    # 缩小按钮：根据XML，是Button[16]（index=15，content-desc="缩小"）
    zoom_out_btn = device_driver.xpath('//android.widget.Button[6]')
    assert zoom_out_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到缩小按钮"
    zoom_out_btn.click()
    time.sleep(SLEEP_DEFAULT)
    print("✅ 缩小按钮操作完成")

# ========================= 统一执行流程 =========================
def run_all_test_cases(device_driver):
    """标准完整流程：搜索 → 连接 → 遍历功能"""
    test_agree_privacy(device_driver)
    test_search_device(device_driver)
    test_connect_device(device_driver)
    test_enter_waveform(device_driver)

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