#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵巧手自动化测试工具主界面
基于 PyQt5 开发，实现端口扫描、设备测试、报告导出等功能
"""
import subprocess
import sys
import os
import time
import importlib
from datetime import datetime
from typing import Dict, List, Optional

import pytest
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side
from openpyxl.styles.fonts import Font
from openpyxl.utils import get_column_letter

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QCheckBox,
    QDialog, QLabel, QStyledItemDelegate, QTextEdit, QDialogButtonBox
)
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.uic import loadUi

from app.app_common import TABLE_HEADERS, DEFAULT_EXECUTE_TIMES_OPTIONS, DEFAULT_OPERATE_INTERVAL_OPTIONS
from app.app_logger import APPHandLogger
from app.app_manager import APPManager
from app.app_theme import apply_black_style, apply_green_style, apply_default_style

# ---------------------------------------------------------------------------
# ====================== 【稳定版】pytest 自动化测试引擎 ======================
# ---------------------------------------------------------------------------

# 用例收集插件
class PytestCollectPlugin:
    def __init__(self):
        self.collected_items = []

    def pytest_collection_modifyitems(self, session, config, items):
        for item in items:
            doc = item.obj.__doc__.strip() if item.obj.__doc__ else item.name
            self.collected_items.append({"nodeid": item.nodeid, "name": doc})

# 用例收集线程
class TestCollectorThread(QThread):
    sig_collected = pyqtSignal(list)
    sig_error = pyqtSignal(str)

    def __init__(self, script_path, parent=None):
        super().__init__(parent)
        self.script_path = script_path

    def run(self):
        try:
            plugin = PytestCollectPlugin()
            pytest.main([
                "--collect-only",
                "-q",
                "-p", "no:logging",
                "-p", "no:faulthandler",
                self.script_path
            ], plugins=[plugin])
            self.sig_collected.emit(plugin.collected_items)
        except Exception as e:
            self.sig_error.emit(str(e))

# 执行插件
class PytestRunnerPlugin:
    def __init__(self, log_signal, status_signal, node_mapping):
        self.log_signal = log_signal
        self.status_signal = status_signal
        self.node_mapping = node_mapping

    @pytest.fixture
    def logger(self):
        return lambda msg: self.log_signal.emit({"level": "info", "msg": str(msg)})

    def pytest_runtest_setup(self, item):
        row = self.node_mapping.get(item.nodeid)
        if row is not None:
            self.log_signal.emit({"level": "sys", "msg": f"开始执行: {item.name}"})
            self.status_signal.emit(row, "RUNNING")

    def pytest_runtest_logreport(self, report):
        row = self.node_mapping.get(report.nodeid)
        if not row:
            return

        if report.skipped:
            self.status_signal.emit(row, "SKIP")
            msg = report.longreprtext.splitlines()[-1] if report.longreprtext else "条件跳过"
            self.log_signal.emit({"level": "skip", "msg": f"用例跳过: {report.nodeid} [{msg}]"})
            return

        if report.when == "call":
            if report.passed:
                self.status_signal.emit(row, "PASS")
                self.log_signal.emit({"level": "success", "msg": f"用例通过: {report.nodeid}"})
            elif report.failed:
                err = report.longreprtext.splitlines()[-1] if report.longreprtext else "未知错误"
                self.status_signal.emit(row, "FAIL")
                self.log_signal.emit({"level": "error", "msg": f"用例失败: {err}"})

# 执行线程
class TestRunnerThread(QThread):
    sig_log = pyqtSignal(dict)
    sig_status = pyqtSignal(int, str)
    sig_finished = pyqtSignal()

    def __init__(self, script_path, node_mapping, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.node_mapping = node_mapping

    def run(self):
        try:
            plugin = PytestRunnerPlugin(self.sig_log, self.sig_status, self.node_mapping)
            pytest.main([
                "-q",
                "-p", "no:logging",
                "-p", "no:faulthandler",
                "-p", "no:cacheprovider",
                self.script_path
            ], plugins=[plugin])
        except Exception:
            pass
        finally:
            self.sig_finished.emit()

# ---------------------------------------------------------------------------
# ====================== 原有主窗口（已集成稳定引擎） ======================
# ---------------------------------------------------------------------------

class APPTestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_operate_interval = 1
        self.selected_execute_times = 1
        self.test_data_table = None
        self.script_loaded = False
        self.script_path = None
        self.script_name = None
        self.report_title = None
        self.raw_test_data = None
        self.stop_test = False
        self.pause_test = False

        # 新增：pytest 引擎变量
        self.current_script_path = None
        self.case_node_mapping = {}
        self.executed_cases_count = 0
        self.collector_thread = None
        self.runner_thread = None

        base = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base, "app_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(base, "ui", "app_test.ui")
        loadUi(ui_path, self)

        flags = self.windowFlags()
        flags &= ~Qt.WindowMaximizeButtonHint
        flags |= Qt.WindowSystemMenuHint | Qt.WindowTitleHint
        self.setWindowFlags(flags)

        self._init_ui_widgets()
        self._bind_all_events()
        self._init_manager()
        self.closeEvent = self.close_event_handler

    # ------------------------------------------------------------------
    # 加载脚本
    # ------------------------------------------------------------------
    def on_load_script(self):
        self.rologger.log(f"正在选择测试脚本...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(base_dir, "scripts")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)

        file_path, _ = QFileDialog.getOpenFileName(self, "选择测试脚本", scripts_dir, "Python files (*.py)")
        if not file_path:
            return

        self.current_script_path = file_path
        self.script_path = file_path
        self.script_name = file_path
        self.test_data_table.setRowCount(0)
        self.case_node_mapping.clear()

        self.rologger.log(f"正在解析脚本：{file_path}")
        self.start_test_btn.setEnabled(False)

        self.collector_thread = TestCollectorThread(file_path)
        self.collector_thread.sig_collected.connect(self.render_cases_to_table)
        self.collector_thread.sig_error.connect(lambda e: self.rologger.log(f"解析失败：{e}", level="ERROR"))
        self.collector_thread.start()

    def render_cases_to_table(self, cases):
        self.rologger.log(f'render_cases_to_table')
        cnt = len(cases)
        if cnt == 0:
            self.rologger.log("未发现测试用例！", level="ERROR")
            self.start_test_btn.setEnabled(True)
            return

        for row, item in enumerate(cases):
            self.test_data_table.insertRow(row)
            self.case_node_mapping[item["nodeid"]] = row

            id_item = QTableWidgetItem(str(row+1))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.test_data_table.setItem(row, 0, id_item)

            name_item = QTableWidgetItem(item["name"])
            name_item.setToolTip(item["nodeid"])
            self.test_data_table.setItem(row, 1, name_item)

            status_item = QTableWidgetItem("待执行")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QBrush(QColor("#909399")))
            self.test_data_table.setItem(row, 2, status_item)

        self.total_case_value.setText(f"{cnt}条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")
        self.test_progress_bar.setValue(0)
        self.start_test_btn.setEnabled(True)
        self.rologger.log(f"脚本加载完成，共 {cnt} 条用例")

    # ------------------------------------------------------------------
    # 开始测试
    # ------------------------------------------------------------------
    def on_start_test(self):
        if not self.current_script_path or self.test_data_table.rowCount() == 0:
            QMessageBox.warning(self, "提示", "请先加载测试脚本！")
            return

        self.start_test_btn.setEnabled(False)
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")
        self.test_progress_bar.setValue(0)
        self.executed_cases_count = 0

        self.rologger.log("=" * 50)
        self.rologger.log("开始执行自动化测试...")

        self.runner_thread = TestRunnerThread(self.current_script_path, self.case_node_mapping)
        # self.runner_thread.sig_log.connect(self.log_from_engine)
        self.runner_thread.sig_status.connect(self.update_case_status)
        self.runner_thread.sig_finished.connect(self.on_test_all_finished)
        self.runner_thread.start()

    def log_from_engine(self, log):
        level = log.get("level", "info")
        msg = log.get("msg")
        self.rologger.log(msg, level=level.upper())

    def update_case_status(self, row, status):
        item = self.test_data_table.item(row, 2)
        total = self.test_data_table.rowCount()

        if status == "RUNNING":
            item.setText("执行中")
            item.setForeground(QBrush(QColor("#E6A23C")))
        elif status == "PASS":
            item.setText("通过")
            item.setForeground(QBrush(QColor("#67C23A")))
            v = self.success_case_value.text().replace("条", "")
            self.success_case_value.setText(f"{int(v)+1}条")
        elif status == "FAIL":
            item.setText("失败")
            item.setForeground(QBrush(QColor("#F56C6C")))
            v = self.fail_case_value.text().replace("条", "")
            self.fail_case_value.setText(f"{int(v)+1}条")
        elif status == "SKIP":
            item.setText("跳过")
            item.setForeground(QBrush(QColor("#E6A23C")))
            v = self.skip_case_value.text().replace("条", "")
            self.skip_case_value.setText(f"{int(v)+1}条")

        if status in ["PASS", "FAIL", "SKIP"]:
            self.executed_cases_count += 1
            progress = int((self.executed_cases_count / total) * 100)
            self.test_progress_bar.setValue(progress)

    def on_test_all_finished(self):
        self.test_progress_bar.setValue(100)
        self.start_test_btn.setEnabled(True)
        self.rologger.log("✅ 所有用例执行完毕！")

    # ------------------------------------------------------------------
    # 原有代码不变
    # ------------------------------------------------------------------

    def close_event_handler(self, event):
        event.accept()

    def setMenuItemStyle(self, menu: QMenu):
        menu.setStyleSheet("""
            QMenu::item {
                height: 20px;
                width: 200px;
                margin: 0px 0px;
                font-size: 16px;
            }
        """)

    class CenterAlignDelegate(QStyledItemDelegate):
        def initStyleOption(self, option, index):
            super().initStyleOption(option, index)
            option.displayAlignment = Qt.AlignCenter

    def _init_ui_widgets(self):
        self.setMenuItemStyle(self.menu_file)
        self.setMenuItemStyle(self.menu_config)
        self.setMenuItemStyle(self.menu_theme)
        self.setMenuItemStyle(self.menu_help)

        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 10))

        self.execute_times_combo.clear()
        self.execute_times_combo.addItems(DEFAULT_EXECUTE_TIMES_OPTIONS)

        self.operate_interval_combo.clear()
        self.operate_interval_combo.addItems(DEFAULT_OPERATE_INTERVAL_OPTIONS)

        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(3)
        self.test_data_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.test_data_table.setRowCount(0)
        self.test_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_data_table.setItemDelegate(self.CenterAlignDelegate())

        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)
        self.test_progress_bar.setStyleSheet("QProgressBar { color: #000000; font-weight: bold; }")

        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")

    def _bind_all_events(self):
        self.execute_times_combo.currentTextChanged.connect(self.on_execute_times_selected)
        self.operate_interval_combo.currentTextChanged.connect(self.on_operate_interval_selected)
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)
        self.log_level_btn.clicked.connect(self.on_log_level_clicked)

        self.funtion_radio_button.toggled.connect(self.on_test_type_changed)
        self.monkey_radio_button.toggled.connect(self.on_test_type_changed)

        self.action_loadScript.triggered.connect(self.on_load_script)
        self.action_exportReport.triggered.connect(self.on_export_report)
        self.action_exit.triggered.connect(self.close)

        self.action_viewConfigFile.triggered.connect(self.on_view_config)
        self.action_editConfigFile.triggered.connect(self.on_edit_config)

        self.action_blackTheme.triggered.connect(self.on_theme_black)
        self.action_greenTheme.triggered.connect(self.on_theme_green)
        self.action_defaultTheme.triggered.connect(self.on_theme_default)
        self.action_about.triggered.connect(self.on_about)

    def _init_manager(self):
        print('_init_manager')
        self.rologger = APPHandLogger(self.log_text_edit)

    def on_test_type_changed(self, checked):
        if not checked:
            return
        if self.funtion_radio_button.isChecked():
            self.rologger.log("当前选中：基本功能测试")
        elif self.monkey_radio_button.isChecked():
            self.rologger.log("当前选中：Monkey 测试")

    def on_execute_times_selected(self, text):
        self.rologger.log('on_execute_times_selected')
        try:
            times_value = float(text.replace("次", ""))
            self.rologger.log(f"已选择 执行次数：{text}")
            self.selected_execute_times = times_value
        except Exception as e:
            self.rologger.log(f"选择执行次数异常：{e}")

    def on_operate_interval_selected(self, text):
        self.rologger.log('on_operate_interval_selected')
        try:
            interval_value = float(text.replace("秒", ""))
            self.rologger.log(f"已选择 操作间隔：{text}")
            self.selected_operate_interval = interval_value
        except Exception as e:
            self.rologger.log(f"选择执行次数异常：{e}")

    def on_copy_log(self):
        self.rologger.log('on_copy_log')
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()

    def on_clear_log(self):
        self.rologger.log('on_clear_log')
        self.log_text_edit.clear()

    def on_save_log(self):
        self.rologger.log("开始保存日志文件")
        filename = f"APP测试日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        fn, _ = QFileDialog.getSaveFileName(self, "保存日志", filename, "文本文件 (*.txt)")
        if fn:
            try:
                with open(fn, "w", encoding="utf-8") as f:
                    f.write(self.log_text_edit.toPlainText())
                self.rologger.log(f"日志保存成功：{os.path.basename(fn)}")
            except Exception as e:
                self.rologger.log(f"日志保存失败：{str(e)}", level="ERROR")

    def on_log_level_clicked(self):
        self.rologger.log(f"on_log_level_clicked")
        menu = QMenu(self)
        self.setMenuItemStyle(menu)
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        current_level = getattr(self.rologger, 'log_level', 'INFO')
        for level in log_levels:
            action = QAction(level, self)
            if level == current_level:
                action.setCheckable(True)
                action.setChecked(True)
            action.triggered.connect(lambda checked, l=level: self.on_log_level_selected(l))
            menu.addAction(action)
        pos = self.log_level_btn.mapToGlobal(QPoint(0, self.log_level_btn.height()))
        menu.exec_(pos)

    def on_log_level_selected(self, level):
        try:
            self.rologger.set_log_level(level)
            self.rologger.log(f"日志级别已设置为：{level}")
        except Exception as e:
            self.rologger.log(f"设置日志级别失败：{str(e)}")

    def update_test_datas_table(self):
        self.rologger.log('update_test_datas_table')

    def get_row_by_port(self, port):
        for row in range(self.test_data_table.rowCount()):
            item = self.test_data_table.item(row, 0)
            if item and item.text() == port:
                return row
        return -1

    def _on_device_info_update(self, device_info_test):
        self.rologger.log('_on_device_info_update')

    def update_table_column_by_port(self, port, column_index, value):
        self.rologger.log('update_table_column_by_port')

    def set_controls_enabled(self, enabled):
        controls = [self.start_test_btn, self.pause_test_btn, self.stop_test_btn]
        for control in controls:
            control.setEnabled(enabled)

    def on_pause_test(self):
        self.rologger.log('on_pause_test')

    def on_stop_test(self):
        self.rologger.log(f'on_stop_test')

    def on_export_report(self):
        self.rologger.log(f'on_export_report')

    def on_view_config(self):
        self.rologger.log(f'on_view_config')
        config_path = APPManager.get_configfile_path()
        if not os.path.exists(config_path):
            QMessageBox.warning(self, "警告", f"配置文件不存在：{config_path}")
            self.rologger.log(f"配置文件不存在：{config_path}")
            return
        try:
            with open(config_path, 'r', encoding='UTF-8') as f:
                content = f.read()
            dialog = QDialog(self)
            dialog.setWindowTitle("查看配置文件")
            dialog.setMinimumSize(600, 800)
            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setFont(QFont("Consolas", 10))
            text_edit.setPlainText(content)
            text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    color: #333333;
                    border: 2px solid #d1d5db;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(text_edit)
            layout.addWidget(button_box)
            dialog.setLayout(layout)
            dialog.exec_()
            self.rologger.log(f"成功查看配置文件：{config_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取配置文件失败：{str(e)}")
            self.rologger.log(f"读取配置文件失败：{str(e)}")

    def on_edit_config(self):
        self.rologger.log(f'on_edit_config')
        config_path = APPManager.get_configfile_path()
        if not os.path.exists(config_path):
            QMessageBox.warning(self, "警告", f"配置文件不存在：{config_path}")
            self.rologger.log(f"配置文件不存在：{config_path}")
            return
        try:
            with open(config_path, 'r', encoding='UTF-8') as f:
                content = f.read()
            dialog = QDialog(self)
            dialog.setWindowTitle("修改配置文件")
            dialog.setMinimumSize(600, 800)
            layout = QVBoxLayout()
            hint_label = QLabel("提示：修改后需要重启应用程序才能生效")
            hint_label.setStyleSheet("color: #f59e0b; font-weight: bold; padding: 5px;")
            layout.addWidget(hint_label)
            text_edit = QTextEdit()
            text_edit.setFont(QFont("Consolas", 10))
            text_edit.setPlainText(content)
            text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    color: #333333;
                    border: 2px solid #d1d5db;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
            button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            save_btn = button_box.button(QDialogButtonBox.Save)
            save_btn.setText("保存")
            save_btn.clicked.connect(lambda: self._save_config_and_restart(config_path, text_edit.toPlainText(), dialog))
            cancel_btn = button_box.button(QDialogButtonBox.Cancel)
            cancel_btn.setText("取消")
            cancel_btn.clicked.connect(dialog.reject)
            layout.addWidget(text_edit)
            layout.addWidget(button_box)
            dialog.setLayout(layout)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"编辑配置文件失败：{str(e)}")
            self.rologger.log(f"编辑配置文件失败：{str(e)}")

    def _save_config_and_restart(self, config_path, content, dialog):
        try:
            with open(config_path, 'w', encoding='UTF-8') as f:
                f.write(content)
            self.rologger.log(f"配置文件已保存：{config_path}")
            QMessageBox.information(self, "成功", "配置文件已保存，应用程序将自动重启...")
            dialog.accept()
            script_path = os.path.abspath(sys.argv[0])
            subprocess.Popen([sys.executable, script_path], start_new_session=True, creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0)
            time.sleep(0.5)
            QApplication.quit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
            self.rologger.log(f"保存配置文件失败：{str(e)}")

    def on_theme_black(self):
        self.rologger.log("on_theme_black")
        apply_black_style(self)

    def on_theme_green(self):
        self.rologger.log("on_theme_green")
        apply_green_style(self)

    def on_theme_default(self):
        self.rologger.log(f"on_theme_default")
        apply_default_style(self)

    def on_about(self):
        self.rologger.log(f"on_about")
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0\n基于PyQt5开发")

# ---------------------------------------------------------------------------
# 线程类
# ---------------------------------------------------------------------------

class DeviceInfosWorker(QThread):
    finished_with_device_infos = pyqtSignal(list)
    def run(self): print(f'run')

class ExecuteScriptWorker(QThread):
    finished_with_script_result = pyqtSignal(str, list)
    def __init__(self, ports: list, device_ids: list, aging_duration: float, script_path: str, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self._is_stopped = False
    def run(self): print(f'run')
    def stop_task(self): self._is_stopped = True

class ProgressBarWorker(QThread):
    progress_update = pyqtSignal(int)
    finished_signal = pyqtSignal()
    def __init__(self, duration, parent=None):
        super().__init__(parent)
        self.total_test_seconds = max(duration, 1)
        self.is_running = True
        self.is_paused = False
        self.delay = 0.0
    def run(self): pass
    def pause(self): self.is_paused = True
    def resume(self): self.is_paused = False
    def stop(self): self.is_running = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = APPTestWindow()
    win.setWindowTitle("应用自动化测试界面")
    win.show()
    sys.exit(app.exec_())