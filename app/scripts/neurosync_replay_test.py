#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纽诺软件自动化测试脚本（最终稳定版）
全局自动启动 -> 加载文件 -> 统一间隔执行用例 -> 自动关闭
"""
import os
import random
import time

import mouse
import pytest
import subprocess
from pywinauto import Application, mouse
from pywinauto.findwindows import find_window, ElementNotFoundError
from pywinauto.timings import wait_until_passes

from app.app_common import OperateSharedData

# ========================= 配置参数 =========================
UI_TIMIEOUT = 3
TEST_DURATION = 12 * 3600
CYCLE_INTERVAL = 10
GLOBAL_CASE_INTERVAL = 3  # 全局统一用例间隔（秒）

CONFIG = {
    "APP_PATH": r"D:\Program Files\NeuroSync\Replay3",
    "FILE_DIR": r"D:\edfx\V25OB3000test20250924191457\V25OB3000test20250924191457",
    "DAO_LIAN_INDEX": 0,
    "SWEEP_SPEED_RANGE": range(0, 22),
    "SENSITIVITY_RANGE": range(0, 16),
    # "HIGH_PASS_RANGE": range(0, 11),
    "LOW_PASS_RANGE": range(0, 6),
    "PLAYBACK_SPEED_RANGE": range(0, 8),
    "MAX_DOWN_RETRIES": 5,
    "TAG_LIST": {
        'Eyes Open', 'Eyes Closed', 'Seizure', 'Deep Breath', 'Background', 'Awake',
        'Eyes Closed PPR', 'Eyes Shut PPR', 'Eyes Open PCR', 'Electrical Seizure', 'End',
        'Identify Event', 'Seizure*', 'Drug-induced Sleep', 'Mechanical Ventilation', 'Facial Twitching'
    },
    "NAV_BUTTONS": [
        {"title_re": "Previous Second", "name": "上一秒", "click_count": 5, "interval": 0.3},
        {"title_re": "Next Second", "name": "下一秒", "click_count": 5, "interval": 0.3},
        {"title_re": "Previous Page", "name": "上一页", "click_count": 3, "interval": 0.3},
        {"title_re": "Next Page", "name": "下一页", "click_count": 3, "interval": 0.3}
    ],
    "TARGET_CHANNELS": [2, 3],
    "PROGRESS_BAR_AUTO_ID": "slider_play_jd",
    "DRAG_CYCLES": 10
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

def select_dropdown_option(main_window, combo_box_auto_id, target_range, option_name, is_random=True):
    try:
        dropdown = main_window.child_window(auto_id=combo_box_auto_id, control_type="ComboBox")
        dropdown.wait("visible", timeout=UI_TIMIEOUT)
        dropdown.wait("enabled", timeout=UI_TIMIEOUT)
        safe_set_focus(dropdown)
        dropdown.click_input()
        time.sleep(1.5)

        items = dropdown.descendants(control_type="ListItem")
        if not items:
            raise Exception(f"未找到任何{option_name}选项")
        max_valid_index = len(items) - 1

        if is_random and isinstance(target_range, (range, list, tuple)):
            valid_indices = [idx for idx in target_range if 0 <= idx <= max_valid_index]
            target_index = random.choice(valid_indices)
        else:
            target_index = target_range if isinstance(target_range, int) else target_range[0]

        current_selected = next((item for item in items if item.is_selected()), None)
        current_index = items.index(current_selected) if current_selected else 0

        if current_index == target_index:
            dropdown.type_keys("{ESC}")
            return

        dropdown.type_keys("{UP 20}")
        time.sleep(0.3)
        dropdown.type_keys(f"{{DOWN {target_index}}}")
        time.sleep(0.3)
        items[target_index].click_input()
        dropdown.type_keys("{ESC}")
        print(f"{option_name}已选择第{target_index + 1}项")
    except Exception as e:
        raise Exception(f"{option_name}选择失败：{str(e)}")

def find_and_click_tag(main_window, target_title):
    try:
        tag_btn = main_window.child_window(title_re=target_title, control_type="Text", found_index=0)
        tag_btn.wait("visible", timeout=UI_TIMIEOUT)
        tag_btn.click_input(coords=(5, 5))
        return True
    except:
        return False

def click_button_multiple_times(main_window, title_re, button_name, click_count=1, interval=0.5, timeout=2):
    try:
        btn = main_window.child_window(title_re=title_re, control_type="Button")
        btn.wait("enabled", timeout=timeout)
        safe_set_focus(btn)
        for i in range(click_count):
            btn.click_input()
            if i < click_count - 1:
                time.sleep(interval)
        time.sleep(0.5)
        return True
    except Exception as e:
        raise Exception(f"【{button_name}失败】{str(e)}")

def select_specific_channels(main_window, target_numbers, max_retries=2):
    for num in target_numbers:
        success = False
        for retry in range(max_retries + 1):
            try:
                channel = main_window.child_window(title_re=rf"^\s*{num}\s*$", control_type="CheckBox")
                channel.wait("visible", timeout=UI_TIMIEOUT * 2)
                channel.wait("enabled", timeout=UI_TIMIEOUT * 2)
                safe_set_focus(channel)
                if channel.get_toggle_state() == 0:
                    channel.click_input()
                    time.sleep(0.3)
                print(f"已选中通道 {num}")
                success = True
                break
            except Exception as e:
                if retry == max_retries:
                    raise Exception(f"通道 {num} 失败：{str(e)}")
                time.sleep(0.5)
        if not success:
            raise Exception(f"通道 {num} 未选中")

def drag_progress_in_cycles(main_window, progress_bar_auto_id, cycles=5):
    try:
        progress_bar = main_window.child_window(auto_id=progress_bar_auto_id, control_type="Slider")
        progress_bar.wait("visible", timeout=UI_TIMIEOUT * 2)
        thumb = progress_bar.child_window(control_type="Thumb")
        thumb.wait("visible", timeout=UI_TIMIEOUT)

        progress_rect = progress_bar.rectangle()
        thumb_rect = thumb.rectangle()
        valid_length = progress_rect.width() - thumb_rect.width()
        current_percent = 0

        for i in range(cycles):
            if i == 0:
                target_percent = random.randint(1, 30)
            else:
                target_percent = min(current_percent * 1.5, 100) if i % 5 != 0 else current_percent * 0.4

            target_x = progress_rect.left + int(valid_length * target_percent / 100)
            target_y = progress_rect.top + progress_rect.height() // 2
            start_x = thumb.rectangle().left + thumb.rectangle().width() // 2 if i == 0 else target_x
            start_y = thumb.rectangle().top + thumb.rectangle().height() // 2 if i == 0 else target_y

            mouse.move(coords=(start_x, start_y))
            time.sleep(0.4)
            mouse.press(button="left", coords=(start_x, start_y))
            time.sleep(0.3)
            for step in range(1, 4):
                mouse.move(coords=(start_x + (target_x - start_x) * step // 3, start_y + (target_y - start_y) * step // 3))
                time.sleep(0.15)
            mouse.release(button="left", coords=(target_x, target_y))
            current_percent = target_percent
            time.sleep(1.5)
    except Exception as e:
        raise Exception(f"拖拽失败：{str(e)}")

def check_stop_pause():
    stop, pause = OperateSharedData.read_control()
    if stop:
        pytest.exit("测试已停止")
    while pause:
        time.sleep(0.2)
        stop, pause = OperateSharedData.read_control()
        if stop:
            pytest.exit("测试已停止")

# ========================= 全局自动启动 & 加载文件 =========================
app_instance = None
main_window = None

@pytest.fixture(scope="session", autouse=True)
def run_app_and_load_file():
    global app_instance, main_window
    from pywinauto import actionlogger
    actionlogger.ActionLogger.log = lambda *args, **kwargs: None

    print("\n==============================================")
    print("✅ 启动应用并加载文件...")
    print("==============================================\n")

    app_dir = CONFIG['APP_PATH']
    exe_files = [f for f in os.listdir(app_dir) if f.lower().endswith(".exe")]
    assert len(exe_files) > 0, "未找到EXE"
    exe_path = os.path.join(app_dir, exe_files[0])

    subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(8)

    app_instance = Application(backend="uia").connect(title_re="NeuroSync Replay.*", timeout=30)
    main_window = app_instance.window(title_re="NeuroSync Replay.*")
    main_window.wait("visible", timeout=30)
    safe_set_focus(main_window)

    bdf_files = [f for f in os.listdir(CONFIG['FILE_DIR']) if f.lower().endswith(".bdf")]
    assert bdf_files, "未找到BDF文件"
    file_path = os.path.join(CONFIG['FILE_DIR'], bdf_files[0])

    try:
        main_window.child_window(title="File", control_type="Button").click_input()
        def get_dlg(): return find_window(title="打开", class_name="#32770")
        dlg_hwnd = wait_until_passes(10, 0.5, get_dlg)
        dlg = app_instance.window(handle=dlg_hwnd)
        edit = dlg.child_window(class_name="Edit")
        edit.wait("enabled", timeout=5)
        edit.type_keys("{BACKSPACE}" * 200)
        edit.type_keys(file_path, with_spaces=True, pause=0.02)
        dlg.child_window(title="打开(O)", control_type="Button").click_input()
        time.sleep(6)
        print("✅ 文件加载完成")
    except Exception as e:
        pytest.fail(f"加载失败：{e}")

    yield

    print("\n✅ 全部用例完成，关闭应用")
    try:
        main_window.close()
    except:
        try:
            app_instance.kill()
        except:
            pass

# ========================= 全局统一用例间隔 =========================
@pytest.fixture(autouse=True)
def global_interval():
    time.sleep(GLOBAL_CASE_INTERVAL)
    check_stop_pause()

# ========================= 测试用例 =========================
def test_verify_paras():
    files = [f for f in os.listdir(CONFIG['FILE_DIR']) if f.endswith(".bdf")]
    assert files, "无BDF文件"
    assert os.path.exists(os.path.join(CONFIG['FILE_DIR'], files[0]))
    print("✅ 文件校验通过")

def test_verify_exe():
    files = [f for f in os.listdir(CONFIG['APP_PATH']) if f.endswith(".exe")]
    assert files, "无EXE文件"
    print("✅ EXE校验通过")

def test_play_start():
    btn = main_window.child_window(title_re="Play", control_type="Button")
    btn.wait("enabled", timeout=UI_TIMIEOUT)
    btn.click_input()
    print("▶️ 播放启动成功")

def test_close_video_playback():
    try:
        video_window = main_window.child_window(control_type="Window", title='Video Playback')
        if video_window.exists(timeout=UI_TIMIEOUT):
            safe_set_focus(video_window)
            close_btn = video_window.child_window(control_type="Button", title='关闭')
            close_btn.wait("enabled", timeout=UI_TIMIEOUT)
            close_btn.click()
            print("✅ Video Playback 窗口已关闭")
        else:
            print("✅ Video Playback 窗口未出现，无需关闭")
    except Exception as e:
        print(f"⚠️ 关闭视频窗口时出现异常：{str(e)}")

def test_enable_0_2s_line():
    cb = main_window.child_window(title_re="0.2s Line", control_type="CheckBox")
    cb.wait("enabled", timeout=UI_TIMIEOUT)
    cb.click_input()
    print("✅ 0.2s线已启用")

def test_channel_selection():
    btn_cl = main_window.child_window(auto_id="btn_cl", control_type="Button", found_index=0)
    btn_cl.wait("enabled", timeout=UI_TIMIEOUT)
    safe_set_focus(btn_cl)
    btn_cl.click_input()  # 👈 物理点击
    time.sleep(3)
    print("✅ 展开通道列表")

    cbx_all = main_window.child_window(title='All', control_type="CheckBox")
    cbx_all.wait("enabled", timeout=UI_TIMIEOUT)
    safe_set_focus(cbx_all)

    if cbx_all.get_toggle_state() == 1:
        cbx_all.click_input()  # 👈 物理点击
        time.sleep(0.5)
        print("✅ 已取消全选通道")
    else:
        print("✅ 通道已处于未全选状态")

    select_specific_channels(main_window, CONFIG['TARGET_CHANNELS'])

    btn_confirm = main_window.child_window(auto_id="btn_confirm", control_type="Button")
    btn_confirm.wait("enabled", timeout=UI_TIMIEOUT)
    btn_confirm.click_input()  # 👈 物理点击
    time.sleep(3)
    print(f"✅ 已确认选中指定通道：{CONFIG['TARGET_CHANNELS']}")

def test_random_config_parameters():
    print("正在随机配置参数...")
    try:
        select_dropdown_option(main_window, "cb_zouzhisudu", CONFIG['SWEEP_SPEED_RANGE'], "走纸速度")
        select_dropdown_option(main_window, "cb_lingmindu", CONFIG['SENSITIVITY_RANGE'], "灵敏度")
        select_dropdown_option(main_window, "cb_lvboxiaxian", CONFIG['LOW_PASS_RANGE'], "过滤器")
        select_dropdown_option(main_window, "cb_bofangbeishu", CONFIG['PLAYBACK_SPEED_RANGE'], "播放倍速")
        assert True, "✅ 随机参数配置完成"
    except Exception as e:
        pytest.fail(f"❌ 参数配置失败：{str(e)}")


def test_navigation_buttons_operation():
    print("开始执行导航按钮操作...")
    try:
        for btn_config in CONFIG['NAV_BUTTONS']:
            click_button_multiple_times(
                main_window=main_window,
                title_re=btn_config["title_re"],
                button_name=btn_config["name"],
                click_count=btn_config["click_count"],
                interval=btn_config["interval"]
            )
        assert True, "✅ 导航按钮操作完成"
    except Exception as e:
        pytest.fail(f"❌ 导航按钮操作失败：{str(e)}")


def test_drag_progress_bar():
    print("开始拖拽进度条...")
    try:
        drag_progress_in_cycles(
            main_window=main_window,
            progress_bar_auto_id=CONFIG['PROGRESS_BAR_AUTO_ID'],
            cycles=CONFIG['DRAG_CYCLES']
        )
        assert True, "✅ 进度条拖拽完成"
    except Exception as e:
        pytest.fail(f"❌ 进度条拖拽失败：{str(e)}")


def test_random_add_tags():
    print("开始随机标记标签...")
    try:
        tag_count = random.randint(2, 10)
        print(f"本次循环计划标记 {tag_count} 个标签")
        success_count = 0

        for tag_idx in range(1, tag_count + 1):
            target_tag = random.choice(list(CONFIG['TAG_LIST']))
            print(f"\n第{tag_idx}/{tag_count}个标签：尝试标记「{target_tag}」")

            if find_and_click_tag(main_window, target_tag):
                print(f"成功标记标签「{target_tag}」")
                success_count += 1
                time.sleep(0.8)
                continue

            print(f"未找到标签「{target_tag}」，尝试翻页查找")
            down_button = main_window.child_window(auto_id="DownButton", control_type="Button")
            down_button.wait("visible", timeout=UI_TIMIEOUT)
            found = False

            for down_count in range(1, CONFIG['MAX_DOWN_RETRIES'] + 1):
                down_button.click_input()
                time.sleep(0.4)
                if find_and_click_tag(main_window, target_tag):
                    print(f"第{down_count}次翻页后成功标记「{target_tag}」")
                    found = True
                    success_count += 1
                    time.sleep(5)
                    break

            if not found:
                print(f"翻页{CONFIG['MAX_DOWN_RETRIES']}次未找到「{target_tag}」，跳过")

        # 断言：至少成功打一个标签
        assert success_count >= 1, f"❌ 标签标记失败，成功数：{success_count}"
        print(f"✅ 标签标记完成，成功总数：{success_count}/{tag_count}")

    except Exception as e:
        pytest.fail(f"❌ 标签标记流程异常：{str(e)}")