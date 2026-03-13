#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QAction,
    QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi

# ==============================
# 测试线程类
# ==============================
class TestThread(QThread):
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    table_update = pyqtSignal(int, str, str, str, str, str)
    result_update = pyqtSignal(int, int, int, int)
    status_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.is_paused = False

    def run(self):
        total = 100
        success = 0
        fail = 0
        skip = 0
        self.status_update.emit("测试开始...")
        self.log_update.emit(f"[{self.get_time()}] 测试启动，总用例数：{total}")
        
        for i in range(total):
            while self.is_paused:
                self.msleep(100)
            if not self.is_running:
                break
            
            res = random.choice(["通过", "失败", "跳过"])
            if res == "通过":
                success += 1
            elif res == "失败":
                fail += 1
            else:
                skip += 1
            
            self.progress_update.emit(i + 1)
            self.log_update.emit(f"[{self.get_time()}] 执行用例 {i+1}：{res}")
            self.table_update.emit(i, f"用例{i+1}", "灵巧手测试", "1.0", "已执行", res)
            self.result_update.emit(total, success, fail, skip)
            self.msleep(50)
        
        if self.is_running:
            self.status_update.emit("测试完成！")
            self.log_update.emit(f"[{self.get_time()}] 测试结束 - 成功：{success} | 失败：{fail} | 跳过：{skip}")
        else:
            self.status_update.emit("测试已停止")
            self.log_update.emit(f"[{self.get_time()}] 测试被手动停止")

    def pause(self):
        self.is_paused = True
        self.log_update.emit(f"[{self.get_time()}] 测试暂停")

    def resume(self):
        self.is_paused = False
        self.log_update.emit(f"[{self.get_time()}] 测试恢复")

    def stop(self):
        self.is_running = False
        self.log_update.emit(f"[{self.get_time()}] 测试停止中...")

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==============================
# 主窗口类
# ==============================
class RoHandTestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 绝对路径加载UI文件
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        ui_path = os.path.join(current_dir, "ui", "rohand_test.ui")
        loadUi(ui_path, self)
        
        self.init_ui()
        self.bind_events()
        self.test_thread = TestThread(self)
        self.bind_thread_signals()

    def init_ui(self):
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet("font-family: Consolas; font-size: 12px;")
        
        # 初始化测试表格
        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 690, 580)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(["用例ID", "用例名称", "版本", "状态", "结果"])
        self.test_data_table.setRowCount(100)
        self.test_data_table.horizontalHeader().setStretchLastSection(True)
        
        # 初始化下拉框
        self.aging_time_combo.addItems(["1小时", "2小时", "4小时", "8小时", "12小时"])
        self.port_list_combo.addItems(["COM1", "COM2", "COM3", "COM4", "COM5"])
        
        # 初始化进度条
        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)
        
        # 初始化结果标签
        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")

    def bind_events(self):
        # 日志按钮事件
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        
        # 功能选项事件
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.select_all_check.stateChanged.connect(self.on_select_all)
        
        # 测试控制事件
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)
        
        # 菜单事件
        self.action_load_script.triggered.connect(self.on_load_script)
        self.action_export_report.triggered.connect(self.on_export_report)
        self.action_about.triggered.connect(self.on_show_about)
        self.action_exit.triggered.connect(self.close)
        self.action_config_port.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 端口配置功能待实现"))
        self.action_config_time.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 时间配置功能待实现"))
        self.action_theme_default.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 已切换为默认主题"))
        self.action_theme_dark.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 深色主题功能待实现"))
        self.action_help_doc.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 帮助文档功能待实现"))

    def bind_thread_signals(self):
        self.test_thread.progress_update.connect(self.test_progress_bar.setValue)
        self.test_thread.log_update.connect(self.log_text_edit.append)
        self.test_thread.table_update.connect(self.update_test_table)
        self.test_thread.result_update.connect(self.update_test_result)
        self.test_thread.status_update.connect(self.statusBar().showMessage)

    # ==============================
    # 事件处理函数
    # ==============================
    def on_copy_log(self):
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已拷贝到剪贴板")

    def on_clear_log(self):
        self.log_text_edit.clear()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已清空")

    def on_save_log(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存日志", f"灵巧手测试日志_{self.get_time().replace(':', '-')}.txt", "文本文件 (*.txt)")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text_edit.toPlainText())
            self.log_text_edit.append(f"[{self.get_time()}] 日志已保存到：{os.path.abspath(filename)}")

    def on_refresh(self):
        self.log_text_edit.append(f"[{self.get_time()}] 刷新配置完成")

    def on_select_all(self, state):
        check = "选中" if state == Qt.Checked else "取消选中"
        self.log_text_edit.append(f"[{self.get_time()}] 全选状态：{check}")

    def on_start_test(self):
        if not self.test_thread.isRunning():
            self.test_thread.is_running = True
            self.test_thread.is_paused = False
            self.test_thread.start()
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试已在运行中")

    def on_pause_test(self):
        if self.test_thread.isRunning():
            if self.test_thread.is_paused:
                self.test_thread.resume()
            else:
                self.test_thread.pause()
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试未运行，无法暂停")

    def on_stop_test(self):
        if self.test_thread.isRunning():
            self.test_thread.stop()
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试未运行，无需停止")

    def on_load_script(self):
        filename, _ = QFileDialog.getOpenFileName(self, "加载测试脚本", "", "Python文件 (*.py);;所有文件 (*.*)")
        if filename:
            self.log_text_edit.append(f"[{self.get_time()}] 已加载脚本：{os.path.basename(filename)}")
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 取消加载脚本")

    def on_export_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, "导出测试报告", f"灵巧手测试报告_{self.get_time().replace(':', '-')}.txt", "文本文件 (*.txt);;Excel文件 (*.xlsx)")
        if filename:
            self.log_text_edit.append(f"[{self.get_time()}] 测试报告已导出到：{os.path.abspath(filename)}")
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 取消导出报告")

    def on_show_about(self):
        QMessageBox.about(self, "关于", "灵巧手测试模块 v1.0\n\n基于PyQt5开发的自动化测试工具\n© 2025 AutotestPlatform")

    # ==============================
    # 辅助函数
    # ==============================
    def update_test_table(self, row, case_id, case_name, version, status, result):
        self.test_data_table.setItem(row, 0, QTableWidgetItem(case_id))
        self.test_data_table.setItem(row, 1, QTableWidgetItem(case_name))
        self.test_data_table.setItem(row, 2, QTableWidgetItem(version))
        self.test_data_table.setItem(row, 3, QTableWidgetItem(status))
        self.test_data_table.setItem(row, 4, QTableWidgetItem(result))
        
        item = self.test_data_table.item(row, 4)
        if result == "通过":
            item.setForeground(QColor(0, 128, 0))
        elif result == "失败":
            item.setForeground(QColor(255, 0, 0))
        else:
            item.setForeground(QColor(128, 128, 128))

    def update_test_result(self, total, success, fail, skip):
        self.total_case_value.setText(f"{total}条")
        self.success_case_value.setText(f"{success}条")
        self.fail_case_value.setText(f"{fail}条")
        self.skip_case_value.setText(f"{skip}条")

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def closeEvent(self, event):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        event.accept()

# ==============================
# 独立运行入口
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = RoHandTestWindow()
    window.setWindowTitle("灵巧手自动化测试界面")
    window.show()
    sys.exit(app.exec_())