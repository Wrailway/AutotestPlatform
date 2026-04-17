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

import keyboard
import pyautogui
import pytest
import subprocess
import psutil
from pywinauto import Application, mouse, Desktop
from pywinauto.findwindows import find_window
from pywinauto.timings import wait_until_passes

from app.app_common import OperateSharedData

# ========================= 配置参数 =========================
UI_TIMEOUT = 3
CONFIG = {
    "APP_PATH": r"D:\Program Files\NeuroSync\Recorder3",
    "COLLECTION_DURATION": 60,
    "SAMPLING_RATE": 500,
    "LEAD_SOURCE_INDEX": 2,
    "DAO_LIAN_INDEX": 2,
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
        btn = main_window.child_window(title="Impedance", control_type="Button")
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

execute_times = 1
operate_interval = 1

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
    from pywinauto import actionlogger
    actionlogger.ActionLogger.log = lambda *args, **kwargs: None
    print("\n==============================================")
    print("✅ 启动 NeuroSync 采集软件...")
    print("==============================================\n")

    app_dir = CONFIG['APP_PATH']
    exe_files = [f for f in os.listdir(app_dir) if f.lower().endswith(".exe")]
    assert len(exe_files) > 0, "未找到EXE"
    exe_path = os.path.join(app_dir, exe_files[0])

    proc = subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
    PROCESS_PID = proc.pid
    time.sleep(8)

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
    refresh_params()
    time.sleep(operate_interval)
    check_stop_pause()

# ========================= 测试用例 =========================
# @pytest.mark.skip('skip test_recorder_connect_device')
def test_recorder_connect_device():
    """扫描设备&连接设备"""
    max_retry = 3
    connected = False

    for attempt in range(1, max_retry + 1):
        try:
            print(f"\n===== 第 {attempt} 次扫描设备 =====")

            # 1. 点击查找设备
            find_device_btn = main_window.child_window(
                title="NeuroSync.Client.Recorder.Pages.Windows.MainWindowViewModel",
                control_type="Button"
            )
            find_device_btn.wait('visible', timeout=UI_TIMEOUT)
            find_device_btn.click()
            time.sleep(1)

            # 2. 点击扫描
            scan_btn = main_window.child_window(title="Scan", control_type="Button")
            scan_btn.wait('visible', timeout=UI_TIMEOUT)
            scan_btn.click()
            print("✅ 开始扫描...")
            time.sleep(10)  # 扫描时间

            # 3. 检查是否出现设备
            connects = main_window.descendants(title="Connect", control_type="Button")
            if connects:
                print("✅ 发现设备，点击连接")
                connects[0].click()
                time.sleep(3)
                connected = True
                break  # 成功就退出循环
            else:
                print(f"⚠️  第 {attempt} 次未扫描到设备，重试中...")

        except Exception as e:
            print(f"⚠️  第 {attempt} 次扫描异常: {str(e)}")
            continue

    # ===================== 核心修复 =====================
    # 必须先判断是否成功，否则直接失败
    assert connected, "❌ 3次扫描均未发现设备"

    # 只有连接成功后，才执行确认
    try:
        confirm = main_window.child_window(auto_id="Confirm", control_type="Button")
        if confirm.exists(timeout=2):
            confirm.click()
            time.sleep(5)
    except:
        print("⚠️ 未找到确认弹窗，跳过")

    print("✅ 设备连接成功！")
    assert True

# @pytest.mark.skip('skip test_recorder_set_sampling_rate')
def test_recorder_set_sampling_rate():
    """设置采样率"""
    try:
        # 等待采样率弹窗出现（必须等！连续执行必备）
        sampling_rate_panel = main_window.child_window(title="Select SampleRate", control_type="Window")
        # sampling_rate_panel.wait('visible', timeout=UI_TIMEOUT)
        # sampling_rate_panel.wait('enabled', timeout=UI_TIMEOUT)

        # 安全聚焦弹窗
        safe_set_focus(sampling_rate_panel)
        time.sleep(0.5)

        # 选择采样率
        aid = f"Radio{CONFIG['SAMPLING_RATE']}"
        radio = sampling_rate_panel.child_window(auto_id=aid, control_type="RadioButton")
        # radio.wait('enabled', timeout=UI_TIMEOUT)
        radio.click()
        time.sleep(1)

        # 点击确认
        confirm = sampling_rate_panel.child_window(title="OK", control_type="Button")
        # confirm.wait('enabled', timeout=UI_TIMEOUT)
        confirm.click()
        time.sleep(2)  # 让弹窗关闭，保证下一个case稳定

        print("✅ 采样率设置成功！")
        assert True

    except Exception as e:
        pytest.fail(f"❌ 设置采样率失败: {str(e)}")

# @pytest.mark.skip('skip test_recorder_set_lead_source')
def test_recorder_set_lead_source():
    """配置导联源"""
    try:
        # 连续执行必须加等待！！！
        lead_source_confirm_panel = main_window.child_window(title="Information", control_type="Window")
        # lead_source_confirm_panel.wait('visible', timeout=UI_TIMEOUT)
        # lead_source_confirm_panel.wait('enabled', timeout=UI_TIMEOUT)

        safe_set_focus(lead_source_confirm_panel)
        time.sleep(0.5)

        Cancel = lead_source_confirm_panel.child_window(title="Cancel", control_type="Button")
        Cancel.wait('enabled', timeout=UI_TIMEOUT)
        Cancel.click()
        time.sleep(2)

        lead_combo = main_window.child_window(control_type="ComboBox",found_index=0)
        # lead_combo.wait('visible', timeout=UI_TIMEOUT)
        # lead_combo.wait('enabled', timeout=UI_TIMEOUT)
        safe_set_focus(lead_combo)

        lead_combo.click_input()
        time.sleep(0.3)
        lead_combo.select(CONFIG["LEAD_SOURCE_INDEX"])

        print("✅ 导联源窗口已关闭")
        assert True

    except Exception as e:
        pytest.fail(f"❌ 设置导联源失败: {str(e)}")

# @pytest.mark.skip('skip test_recorder_set_sweep_speed')
def test_recorder_set_sweep_speed():
    """配置扫描速度"""
    print("\n===== 配置扫描速度 =====")
    try:
        # 随机选择
        value = random.choice(CONFIG["SWEEP_SPEED_RANGE"])
        ret = select_combobox_item(main_window, found_index=1, value=value, desc="Sweep Speed")
        assert ret, "Sweep Speed 配置失败"
        assert True
    except Exception as e:
        pytest.fail(f"❌ Sweep Speed 配置失败: {str(e)}")

# @pytest.mark.skip('skip test_recorder_set_sensitivity')
def test_recorder_set_sensitivity():
    """配置灵敏度"""
    print("\n===== 配置灵敏度 =====")
    try:
        value = random.choice(CONFIG["SENSITIVITY_RANGE"])
        ret = select_combobox_item(main_window, found_index=2, value=value, desc="Sensitivity")
        assert ret, "Sensitivity 配置失败"
        assert True
    except Exception as e:
        pytest.fail(f"❌ Sensitivity 配置失败: {str(e)}")

# @pytest.mark.skip('skip test_recorder_set_filter')
def test_recorder_set_filter():
    """配置滤波"""
    print("\n===== 配置滤波 =====")
    try:
        value = random.choice(CONFIG["FILTER"])
        ret = select_combobox_item(main_window, found_index=3, value=value, desc="Filter")
        assert ret, "Filter 配置失败"
        assert True
    except Exception as e:
        pytest.fail(f"❌ Filter 配置失败: {str(e)}")

# @pytest.mark.skip('skip test_recorder_check_impedance')
def test_recorder_check_impedance():
    """阻抗检测"""
    print("\n===== 阻抗检测 =====")
    ret = check_impedance(main_window)
    assert ret, "阻抗检测失败"


# @pytest.mark.skip('skip:test_recorder_start_collection')
def test_recorder_start_collection():
    """开始采集 + 填写信息"""
    print("\n===== 开始采集 =====")
    try:
        start = main_window.child_window(title="Start", control_type="Button")
        start.click()
        print("✅ 点击开始采集")

        edits = main_window.descendants(class_name="TextBox", control_type="Edit")
        edits[0].set_text(CONFIG["PATIENTS_NAME"])
        print(f"✅ 患者姓名: {CONFIG['PATIENTS_NAME']}")

        # 3. 点开日期选择器
        birthday_fields = main_window.child_window(auto_id="targetElement", control_type="Button")
        birthday_fields.click()
        time.sleep(2)

        day = str(datetime.date.today().day)
        choose_date_btn = main_window.child_window(title=day, control_type="Text",found_index=0 )
        choose_date_btn.wait('visible', timeout=3000)
        choose_date_btn.click_input()

        continue_btn = main_window.child_window(title="Continue", control_type="Button")
        continue_btn.wait('visible', timeout=UI_TIMEOUT)
        continue_btn.click()

        awake = main_window.child_window(title="Awake", control_type="CheckBox")
        awake.click_input()

        confirm = main_window.child_window(title="Finish", control_type="Button")
        confirm.click_input()
        print("✅ 进入采集界面")
        assert True
    except Exception as e:
        pytest.fail(f"❌ 开始采集失败: {str(e)}")

# @pytest.mark.skip('skip test_recorder_auto_marking')
def test_recorder_auto_marking():
    """自动随机标记"""
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

# @pytest.mark.skip('skip:test_recorder_stop_and_save')
def test_recorder_stop_and_save():
    """结束采集 & 保存"""
    print("\n===== 结束采集并保存 =====")
    try:
        # 1. 结束录制
        end = main_window.child_window(title="End", control_type="Button")
        end.wait('enabled', timeout=UI_TIMEOUT)  # 等待可点击
        end.click()
        print("✅ 点击结束采集")
        time.sleep(1)

        # 2. 确认弹窗 OK
        confirm = main_window.child_window(title="OK", control_type="Button")
        confirm.wait('enabled', timeout=UI_TIMEOUT)
        confirm.click()
        print("✅ 已结束采集")
        time.sleep(1)

        # 3. 输入框输入内容
        edits = main_window.descendants(class_name="TextBox", control_type="Edit")
        if len(edits) >= 2:
            edits[1].set_text("123")
            print("✅ 已输入备注: 123")

        # 4. 勾选所有正常选项
        click_all_good_coop_radios(main_window)

        # 5. 勾选意识丧失（容错）
        try:
            loss = main_window.child_window(title="Loss of consciousness", control_type="RadioButton")
            if loss.exists(timeout=1):
                loss.click()
        except Exception:
            print("ℹ️ 未找到意识丧失选项，跳过")

        # 6. 保存
        save = main_window.child_window(title="Save", control_type="Button")
        save.wait('enabled', timeout=UI_TIMEOUT)
        save.click()
        print("✅ 保存成功")

        assert True

    except Exception as e:
        pytest.fail(f"❌ 保存失败: {str(e)}")

def run_all_test_cases():
    test_recorder_connect_device()
    test_recorder_set_sampling_rate()
    test_recorder_set_lead_source()

    test_recorder_set_sweep_speed()
    test_recorder_set_sensitivity()
    test_recorder_set_filter()

    test_recorder_check_impedance()
    test_recorder_start_collection()
    test_recorder_auto_marking()
    test_recorder_stop_and_save()

@pytest.mark.skip('skip test_recorder_main_auto_run')
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

        run_all_test_cases()

        print(f"✅ 第 {i} 轮完成")
        refresh_params()
        time.sleep(operate_interval)

    print("\n🎉 采集软件所有轮次执行完毕！")