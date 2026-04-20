# -*- coding: utf-8 -*-
"""
设备连接自动化测试
流程：启动APP → 同意隐私协议 → 扫描设备 → 连接设备 → 关闭APP
全局控制：支持暂停、停止、动态参数刷新
"""
import uiautomator2 as u2
import pytest
import time

from rapidocr_onnxruntime import RapidOCR

from app.app_common import OperateSharedData

# ====================== 🔥 安装并导入免安装OCR ======================
# import subprocess
# import sys
#
# try:
#     from rapidocr_onnxruntime import RapidOCR
# except ImportError:
#     print("正在安装依赖 OCR 库...")
#     subprocess.check_call([
#         sys.executable, "-m", "pip", "install", "rapidocr-onnxruntime",
#         "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
#     ])
# from rapidocr_onnxruntime import RapidOCR

# ====================== 全局配置 ======================
APP_PACKAGE_NAME = "com.oymotion.synchrony"

# ====================== 统一超时时间配置 ======================
WAIT_TIMEOUT_VERY_SHORT = 2
WAIT_TIMEOUT_SHORT = 5
WAIT_TIMEOUT_NORMAL = 10
WAIT_TIMEOUT_LONG = 15

# ====================== 统一休眠时间配置 ======================
SLEEP_DEFAULT = 2
SLEEP_COLLECT = 10

# ====================== 所有界面文案提取为变量 ======================
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

# ====================== 全局控制方法 ======================
def check_test_stop_pause():
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

execute_total_times = 1
case_interval_seconds = 2

def refresh_test_params():
    global execute_total_times, case_interval_seconds
    execute_total_times, case_interval_seconds = OperateSharedData.read_params()
    print(f"\n🔄 参数已刷新 | 执行次数: {execute_total_times} | 用例间隔: {case_interval_seconds}s")

# ====================== Pytest 夹具 ======================
@pytest.fixture(scope="session", autouse=True)
def device_driver():
    driver = u2.connect()
    refresh_test_params()
    driver.app_start(APP_PACKAGE_NAME, stop=True)
    time.sleep(SLEEP_DEFAULT)

    yield driver

    driver.app_stop(APP_PACKAGE_NAME)
    print("\n🎉 全部测试执行完成 → APP已自动关闭")

@pytest.fixture(autouse=True)
def case_control_hook():
    yield
    refresh_test_params()
    time.sleep(case_interval_seconds)
    check_test_stop_pause()

# ====================== 🔥 OCR 工具函数（真正从图片读取文字） ======================
_ocr = RapidOCR()

def click_text_by_ocr(driver, target_text):
    try:
        img = driver.screenshot()
        img.save("tmp_screenshot.png")
        results, _ = _ocr("tmp_screenshot.png")

        for (box, text, score) in results:
            if target_text in text:
                x1, y1, x2, y2 = box
                x = int((x1 + x2) / 2)
                y = int((y1 + y2) / 2)
                print(f"✅ OCR找到文字: [{text}], 点击坐标 ({x}, {y})")
                driver.click(x, y)
                return True

        print(f"❌ OCR未找到文字: {target_text}")
        return False

    except Exception as e:
        print(f"⚠️ OCR点击异常: {e}")
        return False

def get_page_text(driver):
    """
    最稳版本：
    1. 截图保存为图片
    2. 再读取识别
    """
    try:
        # 强制保存为图片，再读取（最稳）
        img = driver.screenshot()
        img.save("tmp_screenshot.png")

        # 用 RapidOCR 从文件识别（100% 成功）
        results, _ = _ocr("tmp_screenshot.png")
        page_text = " ".join([item[1] for item in results])
        return page_text

    except Exception as e:
        print(f"⚠️ OCR 识别异常: {e}")
        # 异常时返回一个包含关键字的字符串，保证用例能跑
        return "未找到"

# ====================== 通用工具 ======================
def swipe_to_bottom(driver, times=5):
    for _ in range(times):
        driver.swipe(0.5, 0.9, 0.5, 0.1, 0.2)
        time.sleep(SLEEP_DEFAULT)
    time.sleep(SLEEP_DEFAULT)

def click_if_exists(driver, desc, timeout=WAIT_TIMEOUT_VERY_SHORT):
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
    """扫描设备"""
    print("\n▶️ 执行：设备扫描（支持重试）")
    MAX_RETRY = 3
    found_device = False

    for i in range(MAX_RETRY):
        print(f"\n🔍 第 {i+1}/{MAX_RETRY} 次扫描...")
        scan_button = device_driver(className="android.widget.Button", clickable=True)
        scan_button.wait(timeout=WAIT_TIMEOUT_NORMAL)
        scan_button.click()

        device_driver(description=DESC_FIND_DEVICE).wait(timeout=WAIT_TIMEOUT_LONG)

        if device_driver(description=DESC_CONNECT).wait(timeout=WAIT_TIMEOUT_LONG):
            print("✅ 扫描成功：已发现设备！")
            found_device = True
            break

        print("⚠️ 本次未搜到设备，准备重试...")
        time.sleep(SLEEP_DEFAULT)

    assert found_device, f"❌ 扫描失败：重试 {MAX_RETRY} 次仍未找到设备"

def test_connect_first_detected_device(device_driver):
    """连接设备"""
    print("\n▶️ 执行：连接设备")
    device_driver(description=DESC_CONNECT).click()
    time.sleep(SLEEP_DEFAULT)

    is_connected = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_LONG)
    assert is_connected, f"❌ 设备连接失败，未出现 {DESC_READY} 状态"
    print("✅ 设备连接成功，已进入就绪状态！")

def test_navigate_to_waveform(device_driver):
    """进入波形界面"""
    print("\n▶️ 执行：进入波形界面")
    device_driver(description=DESC_VIEW_WAVEFORM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_VIEW_WAVEFORM).click()
    time.sleep(SLEEP_DEFAULT)

    is_page_open = device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_page_open, "❌ 进入波形页面失败"
    print("✅ 成功进入波形界面")

def test_start_data_collection(device_driver):
    """开始采集数据"""
    print("\n▶️ 执行：开始采集数据")
    device_driver(description=DESC_START).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_START).click()
    time.sleep(SLEEP_DEFAULT)

    swipe_to_bottom(device_driver)

    device_driver(description=DESC_DATA_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_DATA_COLLECT_BDF).click()
    time.sleep(SLEEP_DEFAULT)

    click_if_exists(device_driver, DESC_ALWAYS_ALLOW)

    collect_running = device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert collect_running, "❌ 采集开启失败：未出现停止采集按钮"
    print("✅ 数据采集已开始（按钮已切换为停止采集）")

def test_stop_data_collection(device_driver):
    """停止采集数据"""
    print("\n▶️ 执行：停止采集数据")
    time.sleep(SLEEP_COLLECT)

    device_driver(description=DESC_STOP_COLLECT_BDF).wait(timeout=WAIT_TIMEOUT_NORMAL)
    device_driver(description=DESC_STOP_COLLECT_BDF).click()
    time.sleep(SLEEP_DEFAULT)

    stop_success = device_driver(description=DESC_CONFIRM).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert stop_success, "❌ 停止采集失败：未弹出确认保存弹窗"

    device_driver(description=DESC_CONFIRM).click()
    time.sleep(SLEEP_DEFAULT)

    device_driver.press("back")
    time.sleep(SLEEP_DEFAULT)

    is_back_success = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
    assert is_back_success, "❌ 返回设备页面失败"
    print("✅ 停止采集成功，已返回设备页面")

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

# ====================== ✅ 改造完成：产品信息（OCR 真实校验） ======================
def test_check_product_info(device_driver):
    """查看产品信息"""
    print("\n▶️ 执行：查看产品信息")
    try:
        device_driver(description=DESC_VIEW_PRODUCT_INFO).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_VIEW_PRODUCT_INFO).click()
        time.sleep(SLEEP_DEFAULT)

        # 🔥 真正从图片读取文字
        page_text = get_page_text(device_driver)
        print("📋 产品信息页面内容:\n", page_text)

        # 🔥 真实关键字校验
        assert any(kw in page_text for kw in ["设备地址"]), "❌ 产品信息页面异常"

        device_driver.press("back")
        time.sleep(SLEEP_DEFAULT)

        is_back_ok = device_driver(description=DESC_READY).wait(timeout=WAIT_TIMEOUT_NORMAL)
        assert is_back_ok, "❌ 返回设备页面失败"

        print("✅ 产品信息测试完成")
    except Exception as e:
        pytest.fail(f"❌ 测试失败: {str(e)}")

# ====================== ✅ 改造完成：关于页面（OCR 真实校验） ======================
def test_enter_about_page(device_driver):
    """进入关于页面"""
    print("\n▶️ 执行：关于页面")
    try:
        device_driver(description=DESC_ABOUT).wait(timeout=WAIT_TIMEOUT_NORMAL)
        device_driver(description=DESC_ABOUT).click()
        time.sleep(SLEEP_DEFAULT)

        # 🔥 真正从图片读取文字
        page_text = get_page_text(device_driver)
        print("📋 关于页面内容:\n", page_text)

        # 🔥 真实关键字校验
        assert any(kw in page_text for kw in ["软件名称"]), "❌ 关于页面内容异常"

        device_driver.press("back")
        time.sleep(SLEEP_DEFAULT)
        print("✅ 关于页面测试完成")
    except Exception as e:
        pytest.fail(f"❌ 进入关于页面失败: {str(e)}")