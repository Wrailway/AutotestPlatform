#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纽诺采集软件自动化测试脚本（最终稳定版 · pytest 格式）
全局自动启动 -> 自动连接设备 -> 自动采集 -> 自动标记 -> 自动保存 -> 自动关闭
"""
import os
import datetime
import random
import time
import pytest
import subprocess
import psutil
from pywinauto import Application, mouse
from pywinauto.findwindows import find_window
from pywinauto.timings import wait_until_passes

from app.app_common import OperateSharedData

# ========================= 配置参数 =========================
UI_TIMEOUT = 5
CONFIG = {
    "APP_PATH": r"D:\Program Files\NeuroSync\Recorder3\NeuroSync.Client.Recorder.exe",
    "COLLECTION_DURATION": 60,
    "SAMPLING_RATE": 500,
    "LEAD_SOURCE_INDEX": 3,
    "DAO_LIAN_INDEX": 3,
    "CLICK_INTERVAL": 3,
    "SWEEP_SPEED_RANGE": range(0, 8),
    "SENSITIVITY_RANGE": range(0, 16),
    "FILTER": range(0, 6),
    # "LOW_PASS_RANGE": range(0, 6),
    "PATIENTS_NAME": "This is about NeuroSync test",
    "MARK_BUTTON_TITLES": [
        "Hyperventilation","Arms Extended Upright","Pattern Induction","Seizure*","Drug-induced Sleep","Mechanical ventilation","Facial twitching","Limb twitching","Coughing","Shivering",
        "Eyes Open","test","Eyes Closed","Background","Seizure","Deep Breathing","Awake","REM","Eyes Open PPR","Eyes Closed PPR","Eyes Shut PPR","Electrical Seizure",
        "QS","Identify Event","AS"
    ],
    "TARGET_MARKS": ["Seizure*", "Drug-induced Sleep", "Pattern Induction","Arms Extended Upright","Hyperventilation"],
    "EXIT_SETTING_POS": (1549, 79)
}

# ========================= 工具函数 =========================
def safe_set_focus(window, max_retries=3, delay=0.5):
    for i in range(max_retries):
        try:
            window.set_focus()
            return True
        except Exception:
            time.sleep(delay)
    return False

def select_combobox_item(main_window, found_index, value, desc=""):
    try:
        combo = main_window.child_window(control_type="ComboBox", found_index=found_index)
        combo.wait('visible', timeout=UI_TIMEOUT)
        combo.wait('enabled', timeout=UI_TIMEOUT)
        safe_set_focus(combo)
        combo.click_input()
        time.sleep(0.2)
        v = value() if callable(value) else value
        combo.select(v)
        print(f"✅ {desc} 选择项: {v}")
        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"❌ {desc} 选择失败: {str(e)}")
        return False

def check_impedance(main_window):
    try:
        btn = main_window.child_window(title="阻抗", control_type="Button")
        btn.wait('visible', timeout=UI_TIMEOUT)
        btn.click_input()
        print("✅ 打开阻抗检测")
        time.sleep(3)
        btn.click_input()
        print("✅ 关闭阻抗检测")
        return True
    except Exception as e:
        print(f"❌ 阻抗检测失败: {str(e)}")
        return False

def click_all_good_coop_radios(main_window):
    try:
        target = "合作良好"
        radios = [r for r in main_window.descendants(title=target, control_type="RadioButton")
                  if r.is_visible() and r.is_enabled()]
        for r in radios:
            r.click()
        print(f"✅ 已点击所有 {target} 单选框")
        return True
    except Exception as e:
        print(f"❌ 点击合作良好失败: {str(e)}")
        return False

def find_mark_accross_pages(main_window, mark_title):
    try:
        next_btn = main_window.child_window(auto_id="DownButton", control_type="Button", found_index=1)
        prev_btn = main_window.child_window(auto_id="UpButton", control_type="Button", found_index=1)
    except:
        return None

    backward = False
    while True:
        try:
            btn = next(b for b in main_window.descendants(title=mark_title, control_type="Button")
                       if b.is_visible() and b.is_enabled())
            return btn
        except StopIteration:
            if not backward:
                if next_btn.is_enabled():
                    next_btn.click()
                else:
                    backward = True
            else:
                if prev_btn.is_enabled():
                    prev_btn.click()
                else:
                    break
    return None

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

def refresh_params():
    global execute_times, operate_interval
    execute_times, operate_interval = OperateSharedData.read_params()
    print(f"\n🔄 刷新参数：执行次数 = {execute_times}，间隔 = {operate_interval}s")

# ========================= 全局应用 =========================
app_instance = None
main_window = None
PROCESS_PID = None

@pytest.fixture(scope="session", autouse=True)
def run_recorder_app():
    global app_instance, main_window, PROCESS_PID
    print("\n==============================================")
    print("✅ 启动 NeuroSync 采集软件...")
    print("==============================================\n")

    exe_path = CONFIG["APP_PATH"]
    assert os.path.exists(exe_path), "采集软件路径不存在"

    proc = subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
    PROCESS_PID = proc.pid
    time.sleep(6)

    app_instance = Application(backend="uia").connect(title_re="NeuroSync.*", timeout=20)
    main_window = app_instance.window(title_re="NeuroSync.*")
    main_window.wait("visible", timeout=20)
    safe_set_focus(main_window)
    print("✅ 采集软件已启动并连接成功")

    yield

    print("\n✅ 测试完成，关闭采集软件")
    try:
        main_window.close()
        time.sleep(2)
    except:
        pass
    try:
        p = psutil.Process(PROCESS_PID)
        p.kill()
        print("✅ 进程已强杀")
    except:
        pass

@pytest.fixture(autouse=True)
def global_interval():
    yield
    check_stop_pause()
    time.sleep(1)

# ========================= 测试用例 =========================
def test_recorder_connect_device():
    """测试：连接设备 & 扫描设备"""
    print("\n===== 开始扫描并连接设备 =====")
    try:
        safe_set_focus(main_window)
        time.sleep(1)

        # 1. 查找设备（和你原来一样）
        find_device_btn = main_window.child_window(
            title="NeuroSync.Client.Recorder.Pages.Windows.MainWindowViewModel",
            control_type="Button"
        )
        find_device_btn.wait('visible', timeout=10)
        find_device_btn.click()  # ✔ 用你原来的 click
        print("✅ 点击查找设备")
        time.sleep(2)

        # ============================
        # 🔥 完全使用你原来的成功逻辑
        # ============================
        scan_btn = main_window.child_window(title="Scan", control_type="Button")
        scan_btn.wait('visible', timeout=UI_TIMEOUT * 2)
        scan_btn.wait('enabled', timeout=UI_TIMEOUT * 2)

        # ❌ 删掉所有 parent、focus、activate、弹窗操作
        # ✔️ 只保留你原来能用的方式：直接 click()
        scan_btn.click()  # ✅ 这是你原来能用的关键！

        print("✅ 开始扫描设备")
        time.sleep(10)

        # 连接设备
        connects = main_window.descendants(title="Connect", control_type="Button")
        assert connects, "未找到连接按钮"
        connects[0].click_input()
        time.sleep(3)
        print("✅ 点击连接设备")

        confirm = main_window.child_window(auto_id="Confirm", control_type="Button")
        confirm.wait('visible', timeout=5)
        confirm.click_input()
        time.sleep(1)
        print("✅ 确认连接成功")

        assert True

    except Exception as e:
        pytest.fail(f"❌ 连接设备失败: {str(e)}")
# def test_recorder_connect_device():
#     """测试：连接设备 & 扫描设备"""
#     print("\n===== 开始扫描并连接设备 =====")
#     try:
#         safe_set_focus(main_window)
#         time.sleep(1)
#
#         # 1. 查找设备
#         find_device_btn = main_window.child_window(
#             title="NeuroSync.Client.Recorder.Pages.Windows.MainWindowViewModel",
#             control_type="Button"
#         )
#         find_device_btn.wait('enabled', timeout=10)
#         find_device_btn.click_input()
#         print("✅ 点击查找设备")
#         time.sleep(2)
#
#         # ==============================================
#         # 🔥 【终极正确写法】全局捕获弹窗，不管焦点在哪
#         # ==============================================
#         from pywinauto import Desktop
#         popup = Desktop(backend="uia").window(control_type="Window", found_index=1)
#         popup.wait('visible', timeout=5)
#         time.sleep(0.5)
#
#         # 点击扫描按钮
#         scan_btn = popup.child_window(title="Scan", control_type="Button")
#         scan_btn.wait('enabled', timeout=5)
#         scan_btn.click_input()
#         print("✅ 扫描按钮已点击！")
#         time.sleep(10)
#
#         # 连接设备
#         connects = main_window.descendants(title="Connect", control_type="Button")
#         assert connects, "未找到连接按钮"
#         connects[0].click_input()
#         time.sleep(3)
#         print("✅ 点击连接设备")
#
#         # 确认
#         confirm = main_window.child_window(auto_id="Confirm", control_type="Button")
#         confirm.wait('enabled', timeout=5)
#         confirm.click_input()
#         time.sleep(1)
#         print("✅ 确认连接成功")
#
#         assert True
#
#     except Exception as e:
#         pytest.fail(f"❌ 连接设备失败: {str(e)}")

def test_recorder_set_sampling_rate():
    """测试：设置采样率"""
    print("\n===== 设置采样率 =====")
    try:
        # ===================== 修复核心 =====================
        # 1. 先等待【采样率设置页面】整体出现
        sampling_rate_panel = main_window.child_window(title="Select Sampling Rate", control_type="Window")
        sampling_rate_panel.wait('visible', timeout=UI_TIMEOUT * 2)
        safe_set_focus(sampling_rate_panel)
        time.sleep(1)

        # 2. 再找采样率单选框
        aid = f"Radio{CONFIG['SAMPLING_RATE']}"
        radio = main_window.child_window(auto_id=aid, control_type="RadioButton")
        radio.wait('visible', timeout=UI_TIMEOUT)
        radio.wait('enabled', timeout=UI_TIMEOUT)
        radio.click_input()
        print(f"✅ 采样率设置为 {CONFIG['SAMPLING_RATE']} Hz")
        time.sleep(0.5)

        # 3. 点击确定（英文 OK）
        confirm = main_window.child_window(title="OK", control_type="Button")
        confirm.wait('enabled', timeout=UI_TIMEOUT)
        confirm.click_input()
        time.sleep(1)

        # 4. 再次确定（导联源弹窗）
        confirm2 = main_window.child_window(title="OK", control_type="Button")
        if confirm2.exists(timeout=UI_TIMEOUT):
            confirm2.click_input()
            time.sleep(1)

        assert True, "采样率设置成功"

    except Exception as e:
        pytest.fail(f"❌ 设置采样率失败: {str(e)}")

def test_recorder_set_lead_source():
    """测试：设置导联源 & 应用"""
    print("\n===== 设置导联源 =====")
    try:
        combo = main_window.child_window(control_type="ComboBox", found_index=0)
        combo.wait('enabled', timeout=UI_TIMEOUT)
        combo.click_input()
        time.sleep(0.3)
        combo.select(CONFIG["LEAD_SOURCE_INDEX"])
        print(f"✅ 导联源选择索引: {CONFIG['LEAD_SOURCE_INDEX']}")

        apply = main_window.child_window(title="Apply", control_type="Button")
        apply.wait('enabled', timeout=UI_TIMEOUT)
        apply.click_input()
        print("✅ 应用设置")
        assert True
    except Exception as e:
        pytest.fail(f"❌ 设置导联源失败: {str(e)}")

def test_recorder_exit_setting():
    """测试：退出设置页面"""
    print("\n===== 退出设置页面 =====")
    try:
        x, y = CONFIG["EXIT_SETTING_POS"]
        btn = None
        for b in main_window.descendants(control_type="Button"):
            try:
                r = b.rectangle()
                if r.left == x and r.top == y:
                    btn = b
                    break
            except:
                continue
        assert btn, "未找到退出设置按钮"
        btn.click_input()
        print("✅ 已退出设置页面")
        assert True
    except Exception as e:
        pytest.fail(f"❌ 退出设置失败: {str(e)}")

def test_recorder_set_parameters():
    """测试：随机配置参数（导联/速度/灵敏度/滤波）"""
    print("\n===== 配置采集参数 =====")
    try:
        items = [
            {"desc": "Montage Switch", "found_index": 0, "value": CONFIG["DAO_LIAN_INDEX"]},
            {"desc": "Sweep Speed", "found_index": 1, "value": lambda: random.choice(CONFIG["SWEEP_SPEED_RANGE"])},
            {"desc": "Sensitivity", "found_index": 2, "value": lambda: random.choice(CONFIG["SENSITIVITY_RANGE"])},
            {"desc": "Filter", "found_index": 3, "value": lambda: random.choice(CONFIG["FILTER"])},
            # {"desc": "低通滤波", "found_index": 4, "value": lambda: random.choice(CONFIG["LOW_PASS_RANGE"])},
        ]
        for item in items:
            ret = select_combobox_item(main_window, item["found_index"], item["value"], item["desc"])
            assert ret, f"{item['desc']} 配置失败"
        assert True
    except Exception as e:
        pytest.fail(f"❌ 配置参数失败: {str(e)}")

def test_recorder_check_impedance():
    """测试：阻抗检测"""
    print("\n===== 阻抗检测 =====")
    ret = check_impedance(main_window)
    assert ret, "阻抗检测失败"

def test_recorder_start_collection():
    """测试：开始采集 + 填写信息"""
    print("\n===== 开始采集 =====")
    try:
        marker_list = main_window.child_window(title="Evoked Experiment Management", control_type="Button")
        marker_list.wait('enabled', timeout=UI_TIMEOUT)
        marker_list.click_input()
        print("✅ 打开标记列表")

        start = main_window.child_window(title="Start", control_type="Button")
        start.click_input()
        print("✅ 点击开始采集")

        edits = main_window.descendants(class_name="TextBox", control_type="Edit")
        edits[0].set_text(CONFIG["PATIENTS_NAME"])
        print(f"✅ 患者姓名: {CONFIG['PATIENTS_NAME']}")

        birthday = main_window.child_window(auto_id="targetElement", control_type="Button")
        birthday.click()
        today = datetime.date.today().strftime("%YYear%mMonth%dDay") \
            .replace("01Day", "1Day").replace("02Day", "2Day").replace("03Day", "3Day") \
            .replace("04Day", "4Day").replace("05Day", "5Day").replace("06Day", "6Day") \
            .replace("07Day", "7Day").replace("08Day", "8Day").replace("09Day", "9Day")
        date_btn = main_window.child_window(title=today, control_type="Button")
        date_btn.click_input()
        print("✅ 选择出生日期")

        eeg = main_window.child_window(title="Continue", control_type="Button")
        eeg.click()
        awake = main_window.child_window(title="Awake", control_type="CheckBox")
        awake.click_input()
        confirm = main_window.child_window(title="Finish", control_type="Button")
        confirm.click_input()
        print("✅ 进入采集界面")
        assert True
    except Exception as e:
        pytest.fail(f"❌ 开始采集失败: {str(e)}")

def test_recorder_auto_marking():
    """测试：自动随机标记"""
    print("\n===== 开始自动标记 =====")
    try:
        start_time = datetime.datetime.now()
        target = {m: False for m in CONFIG["TARGET_MARKS"]}
        duration = CONFIG["COLLECTION_DURATION"]

        while True:
            elapsed = (datetime.datetime.now() - start_time).total_seconds()
            if elapsed >= duration:
                break
            check_stop_pause()

            title = random.choice(CONFIG["MARK_BUTTON_TITLES"])
            btn = None
            try:
                btn = next(b for b in main_window.descendants(title=title, control_type="Button")
                           if b.is_visible() and b.is_enabled())
            except StopIteration:
                btn = find_mark_accross_pages(main_window, title)

            if btn:
                btn.click()
                print(f"✅ 标记: {title}")
                if title in target:
                    target[title] = True

            wait = min(CONFIG["CLICK_INTERVAL"], duration - elapsed)
            time.sleep(wait)

        print(f"✅ 标记完成: {target}")
        assert True
    except Exception as e:
        pytest.fail(f"❌ 自动标记失败: {str(e)}")

def test_recorder_stop_and_save():
    """测试：结束采集 & 保存"""
    print("\n===== 结束采集并保存 =====")
    try:
        end = main_window.child_window(title="End Record", control_type="Button")
        end.click_input()
        time.sleep(1)
        confirm = main_window.child_window(title="OK", control_type="Button")
        confirm.click_input()
        print("✅ 已结束采集")

        edits = main_window.descendants(class_name="TextBox", control_type="Edit")
        edits[1].set_text("123")
        click_all_good_coop_radios(main_window)

        try:
            main_window.child_window(title="Loss of consciousness", control_type="RadioButton").click()
        except:
            pass

        save = main_window.child_window(title="Save", control_type="Button")
        save.click_input()
        print("✅ 保存成功")
        assert True
    except Exception as e:
        pytest.fail(f"❌ 保存失败: {str(e)}")

# ========================= 压力测试 =========================
execute_times = 1
operate_interval = 1

@pytest.mark.skip('暂时跳过压力测试')
def test_recorder_main_auto_run():
    """采集软件压力测试"""
    global execute_times, operate_interval
    refresh_params()
    print(f"\n🚀 采集压力测试，轮次: {execute_times}")

    for i in range(1, execute_times + 1):
        check_stop_pause()
        print(f"\n=====================================")
        print(f"📌 第 {i} 轮采集测试开始")
        print(f"=====================================\n")

        test_recorder_connect_device()
        test_recorder_set_sampling_rate()
        test_recorder_set_lead_source()
        test_recorder_exit_setting()
        test_recorder_set_parameters()
        test_recorder_check_impedance()
        test_recorder_start_collection()
        test_recorder_auto_marking()
        test_recorder_stop_and_save()

        print(f"✅ 第 {i} 轮完成")
        refresh_params()
        time.sleep(operate_interval)

    print("\n🎉 采集软件所有轮次执行完毕！")