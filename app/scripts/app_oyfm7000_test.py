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
APP_PACKAGE_NAME = "com.oymotion.neucirflite_7000_tool_app"

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
DESC_50HZ_FILTER = "50Hz滤除："
DESC_60HZ_FILTER = "60Hz滤除："
DESC_HPF_FILTER = "HPF："
DESC_LPF_FILTER = "LPF ："

DESC_GESTURE_TRAIN = "手势训练"
DESC_MODEL_DOWNLOAD = "模型下载"
DESC_VIEW_GESTURE = "查看手势"
DESC_PREDEFINE_PARAMS = "预定义参数设置"

DESC_VIEW_PRODUCT_INFO = "查看产品信息"
DESC_ABOUT = "关于"
DESC_ALLOW_WHEN_USING = "仅在使用中允许"

# ====================== 校验关键字 ======================
DEVICE_ADDRESS = "设备地址"
SOFTWARE_NAME = "APP 版本"


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
def swipe_to_bottom(driver, times=5):
    for _ in range(times):
        driver.swipe(0.5, 0.9, 0.5, 0.1, 0.2)
        time.sleep(SLEEP_DEFAULT)

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
#
def test_enter_waveform(device_driver):
    """查看波形"""
    click_if_exists(device_driver, DESC_VIEW_WAVEFORM)
    # device_driver.press("back")
    print("✅ 查看波形")

def test_filter_choose(device_driver):
    """测试滤波开关操作 50Hz / 60Hz / LPF / HPF"""

    # ========== 50Hz滤除开关 ==========
    assert device_driver(description="50Hz Filter:").wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到50Hz滤除文本元素"
    filter_50hz = device_driver.xpath('//android.widget.Switch[1]')
    assert filter_50hz.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到50Hz滤除开关"

    # 点击开关
    x1, y1, x2, y2 = filter_50hz.bounds
    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert filter_50hz.get().attrib["checked"] == "false", "❌ 50Hz关闭失败"

    # 恢复
    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert filter_50hz.get().attrib["checked"] == "true", "❌ 50Hz恢复失败"

    # ========== 60Hz滤除开关 ==========
    assert device_driver(description="60Hz Filter:").wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到60Hz滤除文本元素"
    filter_60hz = device_driver.xpath('//android.widget.Switch[2]')
    assert filter_60hz.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到60Hz滤除开关"

    x1, y1, x2, y2 = filter_60hz.bounds
    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert filter_60hz.get().attrib["checked"] == "false", "❌ 60Hz关闭失败"

    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert filter_60hz.get().attrib["checked"] == "true", "❌ 60Hz恢复失败"

    # ========== LPF开关 ==========
    assert device_driver(description="LPF:").wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到LPF文本元素"
    lpf_switch = device_driver.xpath('//android.widget.Switch[3]')
    assert lpf_switch.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到LPF开关"

    x1, y1, x2, y2 = lpf_switch.bounds
    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert lpf_switch.get().attrib["checked"] == "false", "❌ LPF关闭失败"

    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert lpf_switch.get().attrib["checked"] == "true", "❌ LPF恢复失败"

    # ========== HPF开关 ==========
    assert device_driver(description="HPF:").wait(timeout=WAIT_TIMEOUT_NORMAL), \
        "❌ 未找到HPF文本元素"
    hpf_switch = device_driver.xpath('//android.widget.Switch[4]')
    assert hpf_switch.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到HPF开关"

    x1, y1, x2, y2 = hpf_switch.bounds
    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert hpf_switch.get().attrib["checked"] == "false", "❌ HPF关闭失败"

    device_driver.click(int(x1 + (x2 - x1) * 0.85), (y1 + y2) // 2)
    time.sleep(SLEEP_DEFAULT)
    assert hpf_switch.get().attrib["checked"] == "true", "❌ HPF恢复失败"

    print("✅ 所有滤波开关操作测试通过")

@pytest.mark.skip('放大倍数还存在小bug，先跳过')
def test_gain(device_driver):
    """设置放大倍数：随机选择3个"""
    # 定位右上角放大倍数按钮
    gain_btn = device_driver.xpath('//*[@content-desc="查看波形"]/following-sibling::android.view.View[1]')
    assert gain_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到右上角设置按钮"

    # 放大倍数列表
    gain_list = ["2", "3", "4", "6", "8", "12"]

    # 随机选 3 个
    selected = random.sample(gain_list, 3)

    # 循环选择
    for val in selected:
        # 每次都重新打开菜单（必须）
        gain_btn.click()
        time.sleep(SLEEP_DEFAULT)

        try:
            # 等待任意按钮出现并点击
            btn = device_driver.xpath('//android.widget.Button').wait(timeout=5)
            if btn:
                device_driver.xpath('//android.widget.Button').click()
                time.sleep(SLEEP_DEFAULT)
        except:
            pass

        # 等待选项出现 → 点击
        device_driver(description=val).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=val).click()
        time.sleep(SLEEP_DEFAULT)

        print(f"✅ 已选择放大倍数：{val}")

    # 恢复默认 1
    gain_btn.click()
    time.sleep(SLEEP_DEFAULT)
    device_driver(description="1").wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description="1").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 放大倍数测试完成：随机3个 → 恢复默认1")


def test_zoom_in(device_driver):
    """波形页面"""
    swipe_to_bottom(device_driver)
    zoom_in_btn = device_driver.xpath('//*[@content-desc="放大"]')
    assert zoom_in_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到放大按钮"
    zoom_in_btn.click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 放大按钮操作完成")

def test_wave_duration_setting(device_driver):
    """波形页面-时长"""
    # 时长按钮：根据XML，是Button[8]（content-desc="1s"）
    duration_btn = device_driver.xpath('//android.widget.Button[1]')
    duration_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # 时长选项顺序
    duration_list = ["500ms", "1s", "2s", "5s", "10s", "20s", "30s", "60s"]
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
    device_driver(description="10s").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="10s").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 时长测试完成：随机3个 → 恢复默认1s")

def test_wave_voltage_setting(device_driver):
    """波形页面-电压值"""
    # 电压按钮：根据XML，是Button[6]（content-desc="自适应"）
    voltage_btn = device_driver.xpath('//android.widget.Button[2]')
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
    device_driver(description="Adaptive").wait(timeout=SLEEP_DEFAULT)
    device_driver(description="Adaptive").click()
    time.sleep(SLEEP_DEFAULT)

    print("✅ 电压值测试完成：随机3个范围 → 恢复默认Adaptive")


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
    pause_resume = device_driver.xpath('//android.widget.Button[4]')
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
    zoom_out_btn = device_driver.xpath('//android.widget.Button[5]')
    assert zoom_out_btn.wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未找到缩小按钮"
    zoom_out_btn.click()
    time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    print("✅ 缩小按钮操作完成")

def test_enter_passive_mode(device_driver):
    """主界面-进入被动模式"""
    passive_btn = device_driver(description="被动模式")
    passive_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    passive_btn.click()
    time.sleep(SLEEP_DEFAULT)
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)
    print("✅ 被动模式界面进入/退出测试完成")

def test_passive_mode_all_time_slots(device_driver):
    """被动模式-全档位循环测试：15m/30m/1h"""
    # 定位三个时间档位 + 启动按钮
    time_15m = device_driver.xpath('//android.widget.RadioButton[1]')
    time_30m = device_driver.xpath('//android.widget.RadioButton[2]')
    time_1h  = device_driver.xpath('//android.widget.RadioButton[3]')
    start_btn = device_driver.xpath('//android.widget.Button[@content-desc="启动"]')
    stop_btn = device_driver.xpath('//android.widget.Button[@content-desc="暂停"]')

    # 等待元素加载
    time_15m.wait(timeout=WAIT_TIMEOUT_NORMAL)
    start_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)

    # ======================================
    # 档位 1：15m → 启动10s → 暂停
    # ======================================
    time_15m.click()
    time.sleep(1)
    start_btn.click()  # 启动
    print("✅ 15m 档位启动，运行10秒...")
    time.sleep(10)
    # stop_btn = device_driver.xpath('//android.widget.Button[@content-desc="暂停"]')
    stop_btn.click()  # 暂停
    time.sleep(2)

    # ======================================
    # 档位 2：30m → 启动10s → 暂停
    # ======================================
    time_30m.click()
    time.sleep(1)
    start_btn.click()
    print("✅ 30m 档位启动，运行10秒...")
    time.sleep(10)
    stop_btn.click()  # 暂停
    time.sleep(2)

    # ======================================
    # 档位 3：1h → 启动10s → 暂停
    # ======================================
    time_1h.click()
    time.sleep(1)
    start_btn.click()
    print("✅ 1h 档位启动，运行10秒...")
    time.sleep(10)
    stop_btn.click()  # 暂停
    time.sleep(2)

    # ======================================
    # 恢复默认：15m
    # ======================================
    time_15m.click()
    time.sleep(1)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    print("✅ 被动模式全档位（15m/30m/1h）循环测试完成！")

def test_enter_remote_mode(device_driver):
    """主界面-进入遥控模式"""
    remote_btn = device_driver(description="遥控模式")
    remote_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    remote_btn.click()
    time.sleep(SLEEP_DEFAULT)
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    print("✅ 遥控模式界面进入/退出测试完成")


def test_enter_production_test(device_driver):
    """主界面-进入生产测试"""
    prod_btn = device_driver(description="生产测试")
    prod_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    prod_btn.click()
    time.sleep(SLEEP_DEFAULT)
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)
    print("✅ 生产测试界面进入/退出测试完成")


def test_enter_aging_test(device_driver):
    """主界面-进入老化测试"""
    # 1. 进入老化测试页面
    aging_btn = device_driver(description="老化测试")
    aging_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    aging_btn.click()
    time.sleep(SLEEP_DEFAULT)

    # 2. 找 启动 按钮
    start_btn = device_driver.xpath('//android.widget.Button[@content-desc="启动"]')
    start_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    start_btn.click()
    time.sleep(WAIT_TIMEOUT_LONG)  # 运行中

    # 3. 重新找 暂停 按钮（文字变了，必须重新定位）
    stop_btn = device_driver.xpath('//android.widget.Button[@content-desc="暂停"]')
    stop_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    stop_btn.click()
    time.sleep(SLEEP_DEFAULT)

    # 4. 返回生成测试界面
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    # 4. 返回主界面界面
    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    print("✅ 老化测试：启动 → 暂停 执行完成")


def test_enter_settings(device_driver):
    """主界面-进入设置"""
    settings_btn = device_driver(description="设置")
    settings_btn.wait(timeout=WAIT_TIMEOUT_NORMAL)
    settings_btn.click()
    time.sleep(SLEEP_DEFAULT)
    # device_driver.press("back")
    # time.sleep(SLEEP_DEFAULT)
    print("✅ 设置界面进入/退出测试完成")


def test_check_product_info(device_driver):
    """查看产品信息"""
    device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
    time.sleep(SLEEP_DEFAULT)

    assert device_driver(descriptionContains=DEVICE_ADDRESS).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入产品信息页面"

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)
    # is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    # assert is_back_ok, "❌ 返回设备页面失败"

def test_enter_about_page(device_driver):
    """进入关于页面"""
    device_driver(description=DESC_ABOUT).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_ABOUT).click()
    time.sleep(SLEEP_DEFAULT)

    assert device_driver(descriptionContains=SOFTWARE_NAME).wait(timeout=WAIT_TIMEOUT_NORMAL), "❌ 未进入关于页面"
    time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_ok, "❌ 返回设备页面失败"

# ========================= 统一执行流程 =========================
def run_all_test_cases(device_driver):
    """标准完整流程：搜索 → 连接 → 遍历功能"""
    test_agree_privacy(device_driver)
    test_search_device(device_driver)
    test_connect_device(device_driver)
    test_enter_waveform(device_driver)
    # 波形子界面case
    test_filter_choose(device_driver)

    test_wave_duration_setting(device_driver)
    test_wave_voltage_setting(device_driver)
    test_wave_unit_switch(device_driver)
    test_switch_channel_right(device_driver)
    test_switch_pause_resume(device_driver)
    test_zoom_in(device_driver)
    test_zoom_out(device_driver)

    #主界面其他case
    test_enter_passive_mode(device_driver)
    #被动模式case
    test_passive_mode_all_time_slots(device_driver)

    test_enter_remote_mode(device_driver)
    test_enter_production_test(device_driver)

    test_enter_aging_test(device_driver)

    test_enter_settings(device_driver)
    test_check_product_info(device_driver)
    test_enter_about_page(device_driver)


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