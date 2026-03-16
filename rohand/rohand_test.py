#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem
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
    table_update = pyqtSignal(int, str, str, str, str)
    result_update = pyqtSignal(int, int, int, int)
    status_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.is_paused = False

    def run(self):
        total = 100
        success = fail = skip = 0
        self.status_update.emit("测试开始...")
        self.log_update.emit(f"[{self.get_time()}] 测试启动，总用例数：{total}")

        for i in range(total):
            if not self.is_running:
                break
            while self.is_paused:
                self.msleep(100)

            res = random.choice(["通过", "失败", "跳过"])
            success += 1 if res == "通过" else 0
            fail += 1 if res == "失败" else 0
            skip += 1 if res == "跳过" else 0

            self.progress_update.emit(i + 1)
            self.log_update.emit(f"[{self.get_time()}] 执行用例 {i + 1}：{res}")
            self.table_update.emit(i, f"用例{i + 1}", "灵巧手测试", "已执行", res)
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

    @staticmethod
    def get_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==============================
# 主窗口类（完全保留原UI加载逻辑）
# ==============================
class RoHandTestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 完全保留原始UI加载逻辑，未做任何修改
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "rohand_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(current_dir, "ui", "rohand_test.ui")
        loadUi(ui_path, self)

        # 保留原始窗口标志设置
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        # 初始化UI和绑定
        self.init_ui()
        self.bind_all_events()
        self.test_thread = TestThread(self)
        self.bind_thread_signals()

    def init_ui(self):
        # 日志框配置
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet("font-family: Consolas; font-size: 14px;")

        # 测试数据表格
        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(4)
        self.test_data_table.setHorizontalHeaderLabels(["用例ID", "用例名称", "状态", "结果"])
        self.test_data_table.setRowCount(100)
        self.test_data_table.horizontalHeader().setStretchLastSection(True)

        # 下拉框初始化
        self.aging_time_combo.addItems(["1小时", "2小时", "4小时", "8小时", "12小时"])
        self.port_list_combo.addItems(["COM1", "COM2", "COM3", "COM4", "COM5"])

        # 进度条初始化
        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)

        # 结果标签初始化
        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")

    def bind_all_events(self):
        # 按钮绑定
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.select_all_check.stateChanged.connect(self.on_select_all)
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)

        # 菜单Action绑定（适配XML命名）
        self.action_loadScript.triggered.connect(self.on_load_script)
        self.action_exportReport.triggered.connect(self.on_export_report)
        self.action_exit.triggered.connect(self.close)
        self.action_viewConfigFile.triggered.connect(self.on_view_config)
        self.action_editConfigFile.triggered.connect(self.on_edit_config)
        self.action_blackTheme.triggered.connect(self.on_theme_black)
        self.action_greenTheme.triggered.connect(self.on_theme_green)
        self.action_defaultTheme.triggered.connect(self.on_theme_default)
        self.action_about.triggered.connect(self.on_about)

    def bind_thread_signals(self):
        self.test_thread.progress_update.connect(self.test_progress_bar.setValue)
        self.test_thread.log_update.connect(self.log_text_edit.append)
        self.test_thread.table_update.connect(self.update_test_table)
        self.test_thread.result_update.connect(self.update_test_result)
        self.test_thread.status_update.connect(self.status_bar.showMessage)

    # ==============================
    # 核心槽函数
    # ==============================
    def on_copy_log(self):
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已拷贝到剪贴板")

    def on_clear_log(self):
        self.log_text_edit.clear()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已清空")

    def on_save_log(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存日志", f"灵巧手测试日志_{self.get_time().replace(':', '-')}.txt", "文本文件 (*.txt)"
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text_edit.toPlainText())
            self.log_text_edit.append(f"[{self.get_time()}] 日志已保存：{os.path.basename(filename)}")

    def on_refresh(self):
        self.log_text_edit.append(f"[{self.get_time()}] 端口/配置已刷新")

    def on_select_all(self, state):
        self.log_text_edit.append(f"[{self.get_time()}] 全选状态：{'选中' if state == Qt.Checked else '取消'}")

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
            self.log_text_edit.append(f"[{self.get_time()}] 测试未运行")

    def on_stop_test(self):
        if self.test_thread.isRunning():
            self.test_thread.stop()
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试未运行")

    def on_load_script(self):
        fn, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python文件 (*.py);;所有文件 (*.*)")
        if fn:
            self.log_text_edit.append(f"[{self.get_time()}] 加载脚本：{os.path.basename(fn)}")

    def on_export_report(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "导出报告", f"测试报告_{self.get_time().replace(':', '-')}.txt", "文本文件 (*.txt)"
        )
        if fn:
            self.log_text_edit.append(f"[{self.get_time()}] 报告已导出：{os.path.basename(fn)}")

    def on_view_config(self):
        fn, _ = QFileDialog.getOpenFileName(self, "查看配置", "", "配置文件 (*.ini *.json *.conf)")
        if fn:
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    content = f.read()[:1000]
                QMessageBox.information(self, "配置内容", f"仅显示前1000字符：\n{content}")
                self.log_text_edit.append(f"[{self.get_time()}] 查看配置：{os.path.basename(fn)}")
            except Exception as e:
                self.log_text_edit.append(f"[{self.get_time()}] 查看配置失败：{str(e)}")

    def on_edit_config(self):
        fn, _ = QFileDialog.getOpenFileName(self, "编辑配置", "", "配置文件 (*.ini *.json *.conf)")
        if fn and sys.platform == "win32":
            os.startfile(fn)
            self.log_text_edit.append(f"[{self.get_time()}] 打开配置：{os.path.basename(fn)}")

    def on_theme_black(self):
        style = """
        QMainWindow { background-color: #1e1e2e; color: #cdd6f4; }
        QGroupBox { border: 2px solid #313244; background-color: #181825; color: #cdd6f4; }
        QGroupBox::title { color: #89b4fa; }
        QPushButton { background-color: #414560; color: white; border: 1px solid #585b70; }
        QPushButton:hover { background-color: #585b70; }
        QTableWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; }
        QTableWidget::item:selected { background-color: #313244; }
        QTextEdit { background-color: #11111b; color: #a6adc8; }
        QProgressBar::chunk { background-color: #89b4fa; }
        QMenuBar { background-color: #282838; color: #cdd6f4; }
        QMenuBar::item:selected { background-color: #313244; }
        QMenu { background-color: #181825; color: #cdd6f4; }
        QMenu::item:selected { background-color: #313244; }
        """
        self.setStyleSheet(style)
        self.log_text_edit.append(f"[{self.get_time()}] 切换为黑色主题")

    def on_theme_green(self):
        style = """
        QMainWindow { background-color: #eafaf1; }
        QGroupBox { border: 2px solid #27ae60; }
        QGroupBox::title { color: #219653; }
        QPushButton { background-color: #27ae60; color: white; }
        QProgressBar::chunk { background-color: #27ae60; }
        """
        self.setStyleSheet(style)
        self.log_text_edit.append(f"[{self.get_time()}] 切换为绿色主题")

    def on_theme_default(self):
        self.setStyleSheet("")
        self.log_text_edit.append(f"[{self.get_time()}] 恢复默认主题")

    def on_about(self):
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0\n基于PyQt5开发")
        self.log_text_edit.append(f"[{self.get_time()}] 查看关于信息")

    def update_test_table(self, row, case_id, case_name, status, res):
        self.test_data_table.setItem(row, 0, QTableWidgetItem(case_id))
        self.test_data_table.setItem(row, 1, QTableWidgetItem(case_name))
        self.test_data_table.setItem(row, 2, QTableWidgetItem(status))
        item = QTableWidgetItem(res)
        if res == "通过":
            item.setForeground(QColor(0, 180, 0))
        elif res == "失败":
            item.setForeground(QColor(255, 0, 0))
        else:
            item.setForeground(QColor(200, 160, 0))
        self.test_data_table.setItem(row, 3, item)

    def update_test_result(self, total, success, fail, skip):
        self.total_case_value.setText(f"{total}条")
        self.success_case_value.setText(f"{success}条")
        self.fail_case_value.setText(f"{fail}条")
        self.skip_case_value.setText(f"{skip}条")

    @staticmethod
    def get_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def closeEvent(self, event):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        event.accept()


# ==============================
# 程序入口
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RoHandTestWindow()
    win.setWindowTitle("灵巧手自动化测试界面")
    win.show()
    sys.exit(app.exec_())