#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import logging
import time
import traceback
import importlib.util
import threading
import subprocess
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QCheckBox,
    QDialog, QLabel, QProgressBar, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.uic import loadUi

from rohand_manager import RohanManager
from theme_qss import cache_default_qss, apply_black_qss, apply_green_qss, apply_default_qss
from rohand_logger import RoHandLogger

# 创建日志管理器实例
rohand_logger = RoHandLogger()

# ---------------------------------------------------------------------------
# 从公共模块导入常量和工具函数
# ---------------------------------------------------------------------------
from rohand_common import (
    COL_PORT, COL_SOFTWARE_VERSION, COL_DEVICE_ID, COL_CONNECT_STATUS, COL_TEST_RESULT,
    TABLE_HEADERS, RESULT_PASS, RESULT_FAIL, RESULT_SKIP,
    DEFAULT_TEST_RESULT,
    STATUS_CONNECTED_UI, STATUS_WAIT_TEST, STATUS_TESTING, STATUS_PAUSED,
    STATUS_UNKNOWN_DEVICE, STATUS_READ_FAIL, STATUS_NOT_CONNECTED,
    MSG_HINT, MSG_REFRESH_PORT, MSG_REFRESHING_PORTS, BTN_REFRESH, BTN_LATER, LABEL_SELECT_ALL,
    DIALOG_REFRESH_TITLE, DIALOG_REFRESH_TIP, DEFAULT_AGING_OPTIONS, REFRESH_PROMPT_DELAY_MS
)




#自定义 logging Handler：将日志通过 Qt Signal 发送出去，而不是直接操作 GUI。

class ScriptLogHandler(logging.Handler):
    def __init__(self, log_signal):
        super().__init__()
        self.log_signal = log_signal

    def emit(self, record):
        try:
            self.log_signal.emit(self.format(record))
        except Exception:
            pass

@dataclass
class TestRunParams:
    ports: List[str]
    manager: Any
    script: Optional[str]
    aging: str


class TestThread(QThread):
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    table_update = pyqtSignal(int, str, str, str, str)
    result_update = pyqtSignal(int, int, int, int)
    status_update = pyqtSignal(str)

    def __init__(self, params: TestRunParams, parent=None):
        super().__init__(parent)
        self.p = params
        self._win = parent
        self.is_running = True
        self.is_paused = False
        self.script_log_handler = ScriptLogHandler(self.log_update)

    def _emit_log(self, message: str):
        self.log_update.emit(RohanManager.fmt_log(message))

    def _pulse_progress(self, start_time, aging_seconds):
        if not self.is_running:
            return False
        while self.is_paused:
            self.msleep(100)
        elapsed = (datetime.now() - start_time).total_seconds()
        self.progress_update.emit(min(int((elapsed / aging_seconds) * 100), 100))
        self.msleep(100)
        return True

    def run(self):
        try:
            ports = self.p.ports
            total = len(ports)
            if total == 0:
                self.status_update.emit("没有选中的端口进行测试")
                self._emit_log("测试启动失败：没有选中的端口")
                return
            aging_seconds = int(float(self.p.aging.split("小时")[0]) * 3600)
            success = fail = skip = 0
            self.status_update.emit("测试开始...")
            self._emit_log(f"测试启动，总端口数：{total}，老化时间：{self.p.aging}")
            script_module = self.import_script()
            if not script_module:
                self.status_update.emit("测试失败：脚本导入失败")
                self._emit_log("测试失败：脚本导入失败")
                return

            start_time = datetime.now()
            per_port_time = aging_seconds / total if total > 0 else 0
            for i, port in enumerate(ports):
                #停止 / 暂停控制
                if not self.is_running:
                    break
                while self.is_paused:
                    self.msleep(100)

                port_start_time = datetime.now()
                test_result = [RESULT_FAIL]

                # 在子线程中执行端口测试
                def run_test():
                    try:
                        test_result[0] = self.test_port(port, script_module)
                    except Exception as e:
                        self._emit_log(f"测试端口 {port} 执行异常：{str(e)}")
                        test_result[0] = RESULT_FAIL

                worker = threading.Thread(target=run_test, daemon=True)
                worker.start()
                # 等待测试完成，同时更新进度
                while worker.is_alive():
                    if not self._pulse_progress(start_time, aging_seconds):
                        break
                #统计 & 更新UI
                res = test_result[0]
                success += res == RESULT_PASS
                fail += res == RESULT_FAIL
                skip += res == RESULT_SKIP

                self._emit_log(f"测试端口 {port}：{res}")
                self.table_update.emit(i, port, "-", "-", res)
                self.result_update.emit(total, success, fail, skip)
                #端口间等待（时间均分），保证总测试时间 ≈ aging_seconds
                wait_ms = max(0, int((per_port_time - (datetime.now() - port_start_time).total_seconds()) * 1000))
                wait_start = datetime.now()
                while (datetime.now() - wait_start).total_seconds() * 1000 < wait_ms:
                    if not self._pulse_progress(start_time, aging_seconds):
                        break
            # ===== 测试结束 =====
            self.progress_update.emit(100)
            if self.is_running:
                self.status_update.emit("测试完成！")
                self._emit_log(f"测试结束 - 成功：{success} | 失败：{fail} | 跳过：{skip}")
            else:
                self.status_update.emit("测试已停止")
                self._emit_log("测试被手动停止")

            if self._win and getattr(self._win, "test_status_label", None):
                self._win.test_status_label.setText(STATUS_WAIT_TEST)
        except Exception as e:
            self.status_update.emit("测试异常")
            self._emit_log(f"测试线程异常：{str(e)}")
            import traceback
            self._emit_log(f"异常详情：{traceback.format_exc()}")
            self.progress_update.emit(100)
            if self._win and getattr(self._win, "test_status_label", None):
                self._win.test_status_label.setText(STATUS_WAIT_TEST)
    #脚本的加载与导入
    def import_script(self):
        try:
            spec = importlib.util.spec_from_file_location("test_script", self.p.script)
            module = importlib.util.module_from_spec(spec)

            script_logger = logging.getLogger("test_script")
            script_logger.handlers.clear()  # ✔ 防重复
            script_logger.addHandler(self.script_log_handler)

            spec.loader.exec_module(module)

            self._emit_log("脚本导入成功")
            return module

        except Exception as e:
            self._emit_log(f"脚本导入失败：{e}")
            return None

    def _disconnect_client(self):
        try:
            client = getattr(self.p.manager, "client", None)
            if client:
                client.disconnect()
        except Exception:
            pass

    def test_port(self, port, script_module=None):
        """
        测试单个端口：
        1. test_single_port（结构化）
        2. test_port（布尔）
        3. 默认：仅连接测试
        """
        client_created = False

        try:
            # ---------- 默认连接测试 ----------
            def connect_only():
                nonlocal client_created
                if self.p.manager.create_client(port):
                    client_created = True
                    return RESULT_PASS
                return RESULT_FAIL

            if script_module:
                if hasattr(script_module, "test_single_port"):
                    port_result, connected = script_module.test_single_port(port, 2, False)
                    if not connected:
                        return RESULT_FAIL

                    return (
                        RESULT_PASS
                        if all(g["result"] == RESULT_PASS
                               for g in port_result["gestures"])
                        else RESULT_FAIL
                    )

                if hasattr(script_module, "test_port"):
                    client_created = self.p.manager.create_client(port)
                    if not client_created:
                        return RESULT_FAIL
                    return RESULT_PASS if script_module.test_port(port, self.p.manager) else RESULT_FAIL

            return connect_only()

        except Exception as e:
            self._emit_log(f"测试端口 {port} 异常：{str(e)}")
            return RESULT_FAIL

        finally:
            if client_created:
                self._disconnect_client()

    def pause(self):
        self.is_paused = True
        self._emit_log("测试暂停")

    def resume(self):
        self.is_paused = False
        self._emit_log("测试恢复")

    def stop(self):
        self.is_running = False
        self._emit_log("测试停止中...")


class PortRefreshThread(QThread):
    """
      端口刷新线程：
      在后台线程中读取设备端口列表，
      并通过 Qt Signal 将结果返回给主线程。
      """
    finished_with_ports = pyqtSignal(list, str)  # ports, error_message

    def __init__(self, protocol_type: int = 0, simulate_delay_ms: int = 0, parent=None):
        super().__init__(parent)
        self.protocol_type = protocol_type
        self.simulate_delay_ms = max(0, int(simulate_delay_ms or 0))

    def run(self):
        try:
            if self.simulate_delay_ms > 0:
                self.msleep(self.simulate_delay_ms)
            rohan_manager = RohanManager(protocol_type=self.protocol_type)
            ports = rohan_manager.read_port_info() or []
            self.finished_with_ports.emit(ports, "")
        except Exception as e:
            self.finished_with_ports.emit([], str(e))


class PortRefreshingDialog(QDialog):
    """
        端口刷新等待对话框：
        - 显示倒计时
        - 显示进度条
        - 超时自动关闭
        """
    def __init__(self, parent=None, title: str = DIALOG_REFRESH_TITLE, tip: str = DIALOG_REFRESH_TIP, timeout_seconds: int = 60):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(300, 140)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.timeout_seconds = timeout_seconds
        self.remaining_time = timeout_seconds

        # 创建倒计时标签
        self.countdown_label = QLabel(f"{self.remaining_time}秒", self)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #3b82f6;")

        # 创建提示标签
        self.tip_label = QLabel(tip, self)
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setFont(QFont("Arial", 12))

        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, self.timeout_seconds)
        self.progress_bar.setValue(self.timeout_seconds)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e5e7eb;
                border-radius: 5px;
                background-color: #f3f4f6;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)

        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加倒计时标签
        layout.addWidget(self.countdown_label)
        
        # 添加提示标签
        layout.addWidget(self.tip_label)
        
        # 添加进度条
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

        # 创建计时器
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 每秒更新一次
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.remaining_time = self.timeout_seconds
        self.countdown_label.setText(f"{self.remaining_time}秒")
        self.progress_bar.setValue(self.remaining_time)
        self._timer.start()
        self.show()

    def stop(self):
        self._timer.stop()
        self.close()

    def _tick(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            self.countdown_label.setText(f"{self.remaining_time}秒")
            self.progress_bar.setValue(self.remaining_time)
        else:
            self._timer.stop()


class RoHandTestWindow(QMainWindow):
    """RoHand 测试工具主窗口（精简初始化版）"""

    _TEST_THREAD_BINDINGS = (
        ("progress_update", "test_progress_bar", "setValue"),
        ("log_update", "log_text_edit", "append"),
        ("table_update", None, "update_test_table"),
        ("result_update", None, "update_test_result"),
        ("status_update", "status_bar", "showMessage"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)

        # ===== 基础属性 =====
        self._config_path = RohanManager.get_config_path()
        self.protocol_type = 0
        self._did_schedule_refresh_prompt = False
        self._port_refresh_timed_out = False

        self.select_port_names = []
        self.port_names = ["无可用端口"]
        self.test_data_table = None
        self.check_box_list = []
        self.script_loaded = False
        self.script_path = None

        # ===== UI 必须先加载 =====
        base = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base, "rohand_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(base, "ui", "rohand_test.ui")
        loadUi(ui_path, self)

        flags = self.windowFlags()
        flags &= ~Qt.WindowMaximizeButtonHint
        flags |= Qt.WindowSystemMenuHint | Qt.WindowTitleHint
        self.setWindowFlags(flags)

        # ===== 统一初始化 =====
        self.init_all()

    # ------------------------------------------------------------------
    # 初始化入口
    # ------------------------------------------------------------------
    def init_all(self):
        self._get_manager(refresh=True)
        self._init_ui_widgets()
        cache_default_qss(self)
        self.bind_all_events()
        # 设置日志显示组件
        global rohand_logger
        rohand_logger.set_log_text_edit(self.log_text_edit)
        self._init_port_refresh_timers()
        self._init_test_thread_placeholder()

    # ------------------------------------------------------------------
    # 端口刷新
    # ------------------------------------------------------------------
    def _init_port_refresh_timers(self):
        self._port_refresh_thread = None
        self._port_refresh_dialog = None
        self._port_refresh_timeout_timer = QTimer(self)
        self._port_refresh_timeout_timer.setSingleShot(True)
        self._port_refresh_timeout_timer.timeout.connect(
            self._on_port_refresh_timeout
        )

    # ------------------------------------------------------------------
    # 测试线程占位
    # ------------------------------------------------------------------
    def _init_test_thread_placeholder(self):
        self.test_thread = TestThread(
            TestRunParams(
                ports=[],
                manager=self._get_manager(),
                script=None,
                aging="0.5小时",
            ),
            parent=self,
        )
        self.bind_thread_signals()

    # ------------------------------------------------------------------
    # 日志统一入口（✅ 大幅精简）
    # ------------------------------------------------------------------
    def log(self, msg: str, level='INFO'):
        global rohand_logger
        rohand_logger.custom_logger(level=level, message=msg)

    # ------------------------------------------------------------------
    # UI 初始化
    # ------------------------------------------------------------------
    def _init_ui_widgets(self):
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 10))

        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.test_data_table.setRowCount(100)
        self.test_data_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.aging_time_combo.clear()
        self.aging_time_combo.addItems(DEFAULT_AGING_OPTIONS)

        pl = self._port_list_layout()
        if pl is not None:
            pl.setContentsMargins(12, 8, 18, 8)

        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)

        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")



        self.log(MSG_REFRESH_PORT)
        self.status_bar.showMessage(MSG_REFRESH_PORT)

    # ------------------------------------------------------------------
    # 事件绑定
    # ------------------------------------------------------------------
    def bind_all_events(self):
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.refresh_btn.clicked.connect(self.start_port_refresh)
        self.select_all_check.stateChanged.connect(self.on_select_all)
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)

        # 添加日志级别选择按钮事件
        if hasattr(self, 'log_level_btn'):
            self.log_level_btn.clicked.connect(self.on_log_level_clicked)

        self.action_loadScript.triggered.connect(self.on_load_script)
        self.action_exportReport.triggered.connect(self.on_export_report)
        self.action_exit.triggered.connect(self.close)
        self.action_viewConfigFile.triggered.connect(self.on_view_config)
        self.action_editConfigFile.triggered.connect(self.on_edit_config)
        self.action_blackTheme.triggered.connect(self.on_theme_black)
        self.action_greenTheme.triggered.connect(self.on_theme_green)
        self.action_defaultTheme.triggered.connect(self.on_theme_default)
        self.action_about.triggered.connect(self.on_about)

    # ------------------------------------------------------------------
    # 线程信号绑定
    # ------------------------------------------------------------------
    def bind_thread_signals(self):
        t = self.test_thread
        for sig_name, widget_name, method in self._TEST_THREAD_BINDINGS:
            sig = getattr(t, sig_name)
            target = getattr(self, widget_name) if widget_name else self
            sig.connect(getattr(target, method))

    # ------------------------------------------------------------------
    # 其余方法
    # ------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        if self._did_schedule_refresh_prompt:
            return
        self._did_schedule_refresh_prompt = True
        QTimer.singleShot(REFRESH_PROMPT_DELAY_MS, self._prompt_refresh_ports)

    def _port_list_layout(self):
        # 尝试获取 scroll_content_widget 的布局
        w = getattr(self, "scroll_content_widget", None)
        if w is not None:
            layout = w.layout()
            # PyQt5: QLayout 的 __bool__ 恒为 False，必须用 is None 判断
            if layout is not None:
                return layout
        # 尝试直接获取 port_list_Layout
        lay = getattr(self, "port_list_Layout", None)
        if lay is not None:
            return lay
        return None

    def _prompt_refresh_ports(self):
        box = QMessageBox(self)
        box.setWindowTitle(MSG_HINT)
        box.setIcon(QMessageBox.Information)
        box.setText(MSG_REFRESH_PORT)
        refresh_btn = box.addButton(BTN_REFRESH, QMessageBox.AcceptRole)
        box.addButton(BTN_LATER, QMessageBox.RejectRole)
        box.exec_()
        if box.clickedButton() == refresh_btn:
            self.start_port_refresh()

    def on_copy_log(self):
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()
        self.log("日志已拷贝到剪贴板")

    def on_clear_log(self):
        self.log_text_edit.clear()
        self.log("日志已清空")

    def on_save_log(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "保存日志",
            f"灵巧手测试日志_{RohanManager._ts().replace(':', '-')}.txt",
            "文本文件 (*.txt)",
        )
        if fn:
            with open(fn, "w", encoding="utf-8") as f:
                f.write(self.log_text_edit.toPlainText())
            self.log(f"日志已保存：{os.path.basename(fn)}")

    def on_port_cbx_clicked(self, checked, checkbox):
        try:
            port = checkbox.text()
            if port == LABEL_SELECT_ALL:
                self.select_port_names = self.port_names.copy() if checked else []
                for cbx in self.check_box_list:
                    if cbx.text() != LABEL_SELECT_ALL:
                        cbx.setChecked(checked)
                        self.update_test_data_table(cbx.text(), checked)
            else:
                if checked and port not in self.select_port_names:
                    self.select_port_names.append(port)
                elif not checked and port in self.select_port_names:
                    self.select_port_names.remove(port)
                self.update_test_data_table(port, checked)

            self.log(f"端口 {port} {'选中' if checked else '取消选中'}，已选：{self.select_port_names}")
        except Exception as e:
            self.log(f"复选框操作失败：{str(e)}")

    def on_refresh(self):
        try:
            port_layout = self._port_list_layout()
            if port_layout is None:
                self.log("错误：端口列表布局未找到")
                return

            self.check_box_list.clear()
            self.select_port_names.clear()
            self.remove_all_widgets_from_layout(port_layout)

            if not self.port_names:
                self.port_names = ["无可用端口"]
            if self.port_names[0] == "无可用端口":
                self.log("无可用端口")
                # 创建一个禁用的复选框，显示"无可用端口"
                cbx = QCheckBox("无可用端口")
                cbx.setObjectName("port_checkbox")
                cbx.setEnabled(False)
                self.check_box_list.append(cbx)
                port_layout.addWidget(cbx)
                return

            max_per_col, max_col = 8, 4
            vertical_layouts = []

            for idx, port in enumerate(self.port_names):
                cbx = QCheckBox(port)
                cbx.setObjectName("port_checkbox")
                self.check_box_list.append(cbx)

                col = idx // max_per_col
                if col >= max_col:
                    self.log(f"端口过多，仅显示前{max_col * max_per_col}个")
                    break

                if col >= len(vertical_layouts):
                    vl = QVBoxLayout()
                    vl.setAlignment(Qt.AlignTop)
                    vl.setSpacing(8)
                    port_layout.addLayout(vl)
                    vertical_layouts.append(vl)

                vertical_layouts[col].addWidget(cbx)
                cbx.clicked.connect(
                    lambda checked, cb=cbx: self.on_port_cbx_clicked(checked, cb)
                )

            port_layout.setContentsMargins(12, 8, 18, 8)
            port_layout.setSpacing(10)
            self.log(f"端口刷新完成，共{len(self.check_box_list)}个端口")
        except Exception as e:
            self.log(f"刷新端口崩溃：{str(e)}")
            self.log(f"错误详情：{traceback.format_exc()}")

    def start_port_refresh(self):
        if self._port_refresh_thread and self._port_refresh_thread.isRunning():
            return

        mgr = self._get_manager(refresh=True)
        simulate_timeout = bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)

        self._port_refresh_timed_out = False
        self.status_bar.showMessage(MSG_REFRESHING_PORTS)
        self.log("开始刷新端口..." + ("（Shift模拟超时）" if simulate_timeout else ""))

        if not self._port_refresh_dialog:
            self._port_refresh_dialog = PortRefreshingDialog(
                self, tip=DIALOG_REFRESH_TIP, timeout_seconds=60
            )
        self._port_refresh_dialog.start()

        self._port_refresh_timeout_timer.start(60_000)

        delay_ms = 65_000 if simulate_timeout else 0
        self._port_refresh_thread = PortRefreshThread(
            protocol_type=mgr.protocol_type,
            simulate_delay_ms=delay_ms,
            parent=self,
        )
        self._port_refresh_thread.finished_with_ports.connect(
            self._on_port_refresh_finished
        )
        self._port_refresh_thread.start()

    def _on_port_refresh_timeout(self):
        self._port_refresh_timed_out = True
        if self._port_refresh_dialog:
            self._port_refresh_dialog.stop()
        self.status_bar.showMessage("刷新已超时")
        self.log("刷新已超时")
        QMessageBox.warning(self, "提示", "刷新已超时")

    def _on_port_refresh_finished(self, ports, error_message):
        if self._port_refresh_timeout_timer.isActive():
            self._port_refresh_timeout_timer.stop()
        if self._port_refresh_dialog:
            self._port_refresh_dialog.stop()
        if self._port_refresh_timed_out:
            return

        if error_message:
            self.status_bar.showMessage("端口刷新失败")
            self.log(f"端口刷新失败：{error_message}")
            QMessageBox.warning(self, "提示", f"端口刷新失败：{error_message}")
            return

        self.port_names = ports or ["无可用端口"]
        global rohand_logger
        rohand_logger.log(f"检测到端口：{self.port_names}")
        self.on_refresh()

        if self.port_names and self.port_names[0] != "无可用端口":
            self.status_bar.showMessage("端口刷新完成")
        else:
            self.status_bar.showMessage("无可用端口")

    def remove_all_widgets_from_layout(self, layout):
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

            elif item.layout():
                self.remove_all_widgets_from_layout(item.layout())

    def on_select_all(self, state):
        try:
            checked = state == Qt.Checked
            self.select_port_names = self.port_names.copy() if checked else []
            for cbx in self.check_box_list:
                cbx.setChecked(checked)
                self.update_test_data_table(cbx.text(), checked)
            self.log(f"全选状态：{'选中' if checked else '取消'}，已选：{self.select_port_names}")
        except Exception as e:
            self.log(f"全选操作失败：{str(e)}")

    def on_start_test(self):
        if not self.test_thread.isRunning():
            if not self.script_loaded:
                QMessageBox.warning(self, "提示", "请先加载脚本")
                self.log("测试启动失败：请先加载脚本")
                return

            aging_time = self.aging_time_combo.currentText()
            rohan_manager = self._get_manager(refresh=True)

            cfg = TestRunParams(
                ports=self.select_port_names,
                manager=rohan_manager,
                script=self.script_path,
                aging=aging_time,
            )
            self.test_thread = TestThread(cfg, parent=self)
            self.bind_thread_signals()

            self.test_thread.is_running = True
            self.test_thread.is_paused = False
            self.pause_test_btn.setText("暂停测试")
            self.test_status_label.setText(STATUS_TESTING)
            self.test_thread.start()
        else:
            self.log("测试已在运行中")

    def on_pause_test(self):
        if self.test_thread.isRunning():
            if self.test_thread.is_paused:
                self.test_thread.resume()
                self.pause_test_btn.setText("暂停测试")
                self.test_status_label.setText(STATUS_TESTING)
            else:
                self.test_thread.pause()
                self.pause_test_btn.setText("恢复测试")
                self.test_status_label.setText(STATUS_PAUSED)
        else:
            self.log("测试未运行")

    def on_stop_test(self):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_status_label.setText(STATUS_WAIT_TEST)
        else:
            self.log("测试未运行")

    def on_load_script(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "加载脚本", "", "Python文件 (*.py);;所有文件 (*.*)"
        )
        if fn:
            # 验证脚本是否可以正常导入
            try:
                spec = importlib.util.spec_from_file_location("test_script", fn)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.script_loaded = True
                self.script_path = fn
                self.log(f"加载脚本：{os.path.basename(fn)}")
                QMessageBox.information(self, "成功", f"脚本加载成功：{os.path.basename(fn)}")
            except Exception as e:
                self.script_loaded = False
                self.script_path = None
                error_msg = f"脚本加载失败：{str(e)}"
                self.log(error_msg)
                QMessageBox.warning(self, "错误", error_msg)

    def on_export_report(self):
        report_dir = os.path.join(os.path.dirname(__file__), "report")
        try:
            os.makedirs(report_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"创建report文件夹失败：{str(e)}")
            return

        default_path = os.path.join(
            report_dir, f"测试报告_{RohanManager._ts().replace(':', '-')}.txt"
        )
        fn, _ = QFileDialog.getSaveFileName(
            self, "导出报告", default_path, "文本文件 (*.txt)"
        )
        if not fn:
            self.log("用户取消导出报告")
            return

        try:
            d = os.path.dirname(fn)
            if d and not os.path.exists(d):
                os.makedirs(d)

            body = (
                "灵巧手测试报告\n"
                f"生成时间：{RohanManager._ts()}\n"
                "=" * 60 + "\n\n"
                "测试结果：\n"
                f"总用例：{self.total_case_value.text()}\n"
                f"成功用例：{self.success_case_value.text()}\n"
                f"失败用例：{self.fail_case_value.text()}\n"
                f"跳过用例：{self.skip_case_value.text()}\n\n"
                "测试日志：\n"
                + "-" * 60
                + "\n"
                + self.log_text_edit.toPlainText()
                + "\n"
                + "-" * 60
                + "\n"
            )

            with open(fn, "w", encoding="utf-8") as f:
                f.write(body)

            size = os.path.getsize(fn)
            self.log(f"报告文件创建成功，大小：{size} 字节")
            QMessageBox.information(
                self, "成功", f"报告已成功导出到：\n{fn}\n文件大小：{size} 字节"
            )
        except Exception as e:
            self.log(f"导出报告失败：{str(e)}")
            QMessageBox.warning(self, "错误", f"导出报告失败：{str(e)}")

    def on_view_config(self):
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                content = f.read(1000)
            QMessageBox.information(self, "配置内容", f"仅显示前1000字符：\n{content}")
            self.log(f"查看配置：{os.path.basename(self._config_path)}")
        except Exception as e:
            self.log(f"查看配置失败：{str(e)}")

    def on_edit_config(self):
        try:
            if not os.path.exists(self._config_path):
                self.log("配置文件不存在")
                QMessageBox.warning(self, "错误", "配置文件不存在")
                return

            if not os.access(self._config_path, os.W_OK):
                self.log("配置文件不可写")
                QMessageBox.warning(self, "错误", "配置文件不可写")
                return

            if sys.platform == "win32":
                os.startfile(self._config_path)
            else:
                subprocess.run(["xdg-open", self._config_path])

            self.log(f"打开配置：{os.path.basename(self._config_path)}")
            QMessageBox.information(
                self,
                MSG_HINT,
                "已打开配置文件。\n仅 [protocol_type] 中 protocol=0/1 会切换 Modbus/CAN；\n"
                "保存后窗口将自动重启以应用新协议。",
            )
            QTimer.singleShot(0, self._restart_application)
        except Exception as e:
            self.log(f"打开配置文件失败：{str(e)}")

    def on_theme_black(self):
        apply_black_qss(self)
        self.log("切换为黑色主题")

    def on_theme_green(self):
        apply_green_qss(self)
        self.log("切换为绿色主题")

    def on_theme_default(self):
        apply_default_qss(self)
        self.log("切换为默认主题")

    def on_about(self):
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0\n基于PyQt5开发")
        self.log("查看关于信息")

    def on_log_level_clicked(self):
        """
        点击日志级别按钮后显示选择复选框
        """
        from PyQt5.QtWidgets import QMenu, QAction
        from PyQt5.QtCore import QPoint
        
        # 创建下拉菜单
        menu = QMenu(self)
        
        # 日志级别选项
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        # 获取当前日志级别
        global rohand_logger
        current_level = getattr(rohand_logger, 'log_level', 'INFO')
        
        # 添加菜单项
        for level in log_levels:
            action = QAction(level, self)
            if level == current_level:
                action.setCheckable(True)
                action.setChecked(True)
            action.triggered.connect(lambda checked, l=level: self.on_log_level_selected(l))
            menu.addAction(action)
        
        # 在按钮下方显示菜单
        button_pos = self.log_level_btn.mapToGlobal(QPoint(0, self.log_level_btn.height()))
        menu.exec_(button_pos)
    
    def on_log_level_selected(self, level):
        """
        选择日志级别后的处理
        :param level: 选择的日志级别
        """
        global rohand_logger
        try:
            rohand_logger.set_log_level(level)
            rohand_logger.log(f"日志级别已设置为：{level}")
        except Exception as e:
            rohand_logger.log(f"设置日志级别失败：{str(e)}")

    def update_test_table(self, row, case_id, case_name, status, res):
        self.test_data_table.setItem(row, 0, QTableWidgetItem(case_id))
        self.test_data_table.setItem(row, 3, QTableWidgetItem(STATUS_CONNECTED_UI))
        item = QTableWidgetItem(res)
        if res == RESULT_PASS:
            item.setForeground(QColor(0, 180, 0))
        elif res == RESULT_FAIL:
            item.setForeground(QColor(255, 0, 0))
        else:
            item.setForeground(QColor(200, 160, 0))
        self.test_data_table.setItem(row, 4, item)

    def update_test_result(self, total, success, fail, skip):
        self.total_case_value.setText(f"{total}条")
        self.success_case_value.setText(f"{success}条")
        self.fail_case_value.setText(f"{fail}条")
        self.skip_case_value.setText(f"{skip}条")

    def _query_port_device_fields(self, port):
        try:
            mgr = self._get_manager()
            return mgr.query_port_device_fields(port)
        except Exception as e:
            self.log(f"读取设备信息失败：{str(e)}")
            return "-", "-", STATUS_READ_FAIL

    def _write_test_data_row(self, row, values):
        for col, text in enumerate(values):
            self.test_data_table.setItem(row, col, QTableWidgetItem(text))

    def update_test_data_table(self, port, checked):
        try:
            row = -1
            for i in range(self.test_data_table.rowCount()):
                item = self.test_data_table.item(i, 0)
                if item and item.text() == port:
                    row = i
                    break
            if row == -1:
                for i in range(self.test_data_table.rowCount()):
                    item = self.test_data_table.item(i, 0)
                    if not item or not item.text():
                        row = i
                        break
            if row == -1:
                return

            if checked:
                # 使用后台线程查询设备信息，避免UI卡死
                from PyQt5.QtCore import QThread, pyqtSignal
                
                class DeviceInfoThread(QThread):
                    result_ready = pyqtSignal(str, str, str, int)
                    
                    def __init__(self, port, row, parent=None):
                        super().__init__(parent)
                        self.port = port
                        self.row = row
                        self.parent = parent
                    
                    def run(self):
                        try:
                            sw, did, cst = self.parent._query_port_device_fields(self.port)
                            self.result_ready.emit(sw, did, cst, self.row)
                        except Exception as e:
                            self.parent.log(f"查询设备信息失败：{str(e)}")
                            self.result_ready.emit("-", "-", "读取失败", self.row)
                
                thread = DeviceInfoThread(port, row, self)
                thread.result_ready.connect(lambda sw, did, cst, r: self._write_test_data_row(r, (port, sw, did, cst, DEFAULT_TEST_RESULT)))
                thread.start()
            else:
                self._write_test_data_row(row, ("", "", "", "", ""))
        except Exception as e:
            self.log(f"更新测试数据表格失败：{str(e)}")

    def _get_manager(self, refresh=False):
        if refresh:
            self.protocol_type = RohanManager.read_protocol_type_from_config(
                self._config_path
            )
            self.log(
                f"从配置文件读取协议类型：{self.protocol_type}（0=Modbus，1=CAN）"
            )
        return RohanManager.ensure_global(self.protocol_type)



    def closeEvent(self, event):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        RohanManager.release_global()
        event.accept()

    def _restart_application(self):
        try:
            python = sys.executable or "python"
            script = os.path.abspath(sys.argv[0])
            subprocess.Popen([python, script])
        except Exception as e:
            self.log(f"重启应用失败：{e}")
        finally:
            QApplication.instance().quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RoHandTestWindow()
    win.setWindowTitle("灵巧手自动化测试界面")
    win.show()
    sys.exit(app.exec_())