#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纽诺软件自动化测试脚本（最终稳定版）
全局自动启动 -> 加载文件 -> 统一间隔执行用例 -> 自动关闭
"""
import os
import random
import time

import pytest
import subprocess
from pywinauto import Application, mouse
from pywinauto.findwindows import find_window
from pywinauto.timings import wait_until_passes
import psutil

from app.app_common import OperateSharedData

# ========================= 配置参数 =========================
UI_TIMIEOUT = 3
CONFIG = {
    "APP_PATH": r"D:\Program Files\Neucir_Pro-Test-1.0.3\Neucir_Pro-Test-1.0.3",
}

# ========================= 工具函数 =========================

# ====================== 工具函数 ======================
# def click_text_by_ocr(driver, target_text, offset_x=0, offset_y=0):
#     """
#     增强版：支持偏移点击，专门点复选框/开关
#     :param offset_x: 水平偏移（正数向右，负数向左）
#     :param offset_y: 垂直偏移（正数向下，负数向上）
#     """
#     try:
#         from rapidocr_onnxruntime import RapidOCR
#         _ocr = RapidOCR()
#
#         img = driver.screenshot()
#         img.save("tmp_screenshot.png")
#         results, _ = _ocr("tmp_screenshot.png")
#
#         for item in results:
#             box = item[0]
#             text = item[1]
#
#             x_coords = [p[0] for p in box]
#             y_coords = [p[1] for p in box]
#
#             x1 = min(x_coords)
#             y1 = min(y_coords)
#             x2 = max(x_coords)
#             y2 = max(y_coords)
#
#             if target_text in text:
#                 cx = int((x1 + x2) / 2)
#                 cy = int((y1 + y2) / 2)
#
#                 final_x = cx + offset_x
#                 final_y = cy + offset_y
#
#                 driver.click(final_x, final_y)
#                 return True
#
#     except Exception as e:
#         print(f"⚠️ OCR异常: {e}")
#     return False
#
# def get_page_text(driver):
#     try:
#         from rapidocr_onnxruntime import RapidOCR
#         _ocr = RapidOCR()
#
#         img = driver.screenshot()
#         img.save("tmp_screenshot.png")
#         results, _ = _ocr("tmp_screenshot.png")
#         return " ".join([item[1] for item in results])
#     except Exception as e:
#         print(f"⚠️ OCR识别失败: {e}")
#         return ""

def safe_set_focus(window, max_retries=3, delay=0.5):
    for i in range(max_retries):
        try:
            window.set_focus()
            return True
        except Exception:
            time.sleep(delay)
    return False

def check_stop_pause():
    stop, pause = OperateSharedData.read_control()
    if stop:
        print("\n🛑 检测到停止信号，退出测试")
        pytest.exit("测试已停止")
    while pause:
        print("⏸️ 测试暂停中...")
        for _ in range(10):
            time.sleep(0.2)
            stop, pause = OperateSharedData.read_control()
            if stop:
                pytest.exit("测试已停止")
        check_stop_pause()

# 全局参数
execute_times = 1
operate_interval = 5

def refresh_params():
    global execute_times, operate_interval
    execute_times, operate_interval = OperateSharedData.read_params()
    print(f"\n🔄 刷新参数：执行次数 = {execute_times}，间隔 = {operate_interval}s")


# ========================= 全局自动启动 & 加载文件 =========================
app_instance = None
main_window = None
PROCESS_PID = None

@pytest.fixture(scope="session", autouse=True)
def run_app_and_load_file():
    global app_instance, main_window, PROCESS_PID
    from pywinauto import actionlogger
    actionlogger.ActionLogger.log = lambda *args, **kwargs: None

    print("\n==============================================")
    print("✅ 启动应用并加载文件...")
    print("==============================================\n")
    app_dir = CONFIG['APP_PATH']
    exe_files = [f for f in os.listdir(app_dir) if f.lower().endswith(".exe")]
    assert len(exe_files) > 0, "未找到EXE"
    exe_path = os.path.join(app_dir, exe_files[0])

    proc = subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
    PROCESS_PID = proc.pid
    time.sleep(5)

    try:
        app_instance = Application(backend="uia").connect(process=PROCESS_PID, timeout=20)
        main_window = app_instance.top_window()
        main_window.wait("visible", timeout=20)
        safe_set_focus(main_window)
        print("✅ 应用连接成功！")
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        raise

    yield

    print("\n✅ 全部用例完成，关闭应用")
    try:
        main_window.close()
        time.sleep(2)
    except:
        pass

    try:
        p = psutil.Process(PROCESS_PID)
        p.kill()
        print("✅ 进程已强杀关闭")
    except:
        pass

@pytest.fixture(autouse=True)
def global_interval():
    yield
    refresh_params()
    time.sleep(operate_interval)
    check_stop_pause()

# ========================= 测试用例=========================
def test_verify_exe():
    """检查软件是否存在"""
    files = [f for f in os.listdir(CONFIG['APP_PATH']) if f.lower().endswith(".exe")]
    assert files, "应用目录下未找到EXE文件"
    print("✅ EXE文件校验通过")

def test_agree_privacy_policy():
    """同意隐私协议"""
    try:
        # 使用已连接的app_instance定位弹窗
        privacy_popup = app_instance.window(title_re="Neucir Pro.*", control_type="Window")
        assert privacy_popup.exists(timeout=10), "❌ 未找到隐私协议弹窗"
        rect = privacy_popup.rectangle()
        # 根据弹窗位置，按钮在右下角，计算相对位置
        click_x = rect.right - 100
        click_y = rect.bottom - 60
        mouse.move(coords=(click_x, click_y))
        mouse.click(coords=(click_x, click_y))
        print("✅ 已通过坐标点击【确定】按钮")

    except AssertionError as e:
        print(f"❌ 隐私协议处理失败: {e}")
        raise
    except Exception as e:
        print(f"⚠️ 未检测到隐私协议弹窗，跳过处理: {e}")

# @pytest.mark.skip('test_find_device')
def test_find_device():
    """点击查找设备"""
    try:
        find_device_window = app_instance.window(title="Neucir Pro")
        find_device_window.wait("visible", timeout=10)
        find_device_window.set_focus()
        rect = find_device_window.rectangle()

        # ✅ 精准点击右下角放大镜（你界面真实位置）
        click_x = rect.right - 55
        click_y = rect.bottom - 55

        mouse.move(coords=(click_x, click_y))
        time.sleep(0.3)
        mouse.click(coords=(click_x, click_y))

        print("✅ 查找设备按钮点击成功！")
        time.sleep(4)  # 等待扫描完成

    except Exception as e:
        print(f"❌ 失败: {e}")
        raise

def test_connect_device():
    """连接设备"""
    try:
        find_device_window = app_instance.window(title="Neucir Pro")
        find_device_window.wait("visible", timeout=10)
        find_device_window.set_focus()
        rect = find_device_window.rectangle()

        # ✅ 精准点击右上角【连接】按钮（你截图真实位置）
        connect_x = rect.right - 100
        connect_y = rect.top + 50

        mouse.move(coords=(connect_x, connect_y))
        time.sleep(0.3)
        mouse.click(coords=(connect_x, connect_y))

        print("✅ 连接按钮点击成功！")
        time.sleep(2)

    except Exception as e:
        print(f"❌ 失败: {e}")
        raise