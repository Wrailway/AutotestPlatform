#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试平台
适配UI：rohand.ui
核心功能：测试控制、日志输出（拷贝/清屏/保存）、结果统计、脚本加载/报告导出、主题配置
"""

import sys
import os
import random
from datetime import datetime
from PyQt5.QtGui import QIcon, QColor, QClipboard  # 修复：QClipboard 从 QtGui 导入
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QAction, QMenu,
    QTextEdit, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
)
from PyQt5 import uic

# ==============================
# 常量配置
# ==============================
UI_FILE_PATH = "rohand_test.ui"
APP_TITLE = "灵巧手测试界面"
ICON_FILE = "icon/logo.png"  # 可选：无则忽略

# 测试相关常量
TEST_CASE_TOTAL = 100
TEST_STATUS_INIT = "等待测试。。。。"
TEST_STATUS_RUNNING = "测试中。。。。"
TEST_STATUS_STOPPED = "测试已停止"
TEST_STATUS_FINISHED = "测试完成"

# 动画配置
BUTTON_ANIM_DURATION = 150
BUTTON_ANIM_SCALE = 0.95

# ==============================
# 测试线程（避免主线程卡顿）
# ==============================
class TestThread(QThread):
    progress_update = pyqtSignal(int)       # 进度更新
    log_update = pyqtSignal(str)           # 日志更新
    table_update = pyqtSignal(int, str, str, str, str, str)  # 表格更新：行号、端口、设备ID、版本、连接状态、测试结果
    result_update = pyqtSignal(int, int, int, int)  # 结果更新：成功、失败、跳过、总数
    status_update = pyqtSignal(str)        # 状态更新

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.is_paused = False

    def run(self):
        """模拟测试执行逻辑"""
        success = 0
        fail = 0
        skip = 0
        total = TEST_CASE_TOTAL

        # 模拟测试设备列表
        test_devices = [
            ("COM1", "DEV001", "V1.0.0", "已连接"),
            ("COM2", "DEV002", "V1.0.1", "已连接"),
            ("COM3", "DEV003", "V1.0.0", "未连接"),
            ("COM4", "DEV004", "V1.0.2", "已连接"),
            ("COM5", "DEV005", "V1.0.1", "已连接")
        ]

        self.status_update.emit(TEST_STATUS_RUNNING)
        self.log_update.emit(f"[{self.get_time()}] 开始测试，共{total}条用例")

        # 模拟测试过程
        for idx, (port, dev_id, version, conn_status) in enumerate(test_devices):
            if not self.is_running:
                break
            if self.is_paused:
                self.status_update.emit("测试已暂停")
                while self.is_paused and self.is_running:
                    self.msleep(100)
                if not self.is_running:
                    break
                self.status_update.emit(TEST_STATUS_RUNNING)

            # 更新表格：执行中
            self.table_update.emit(idx, port, dev_id, version, conn_status, "执行中")
            self.log_update.emit(f"[{self.get_time()}] 测试设备 {dev_id}（端口{port}）")
            self.msleep(800)  # 模拟测试耗时

            # 模拟测试结果
            if conn_status == "未连接":
                res = "跳过"
                skip += 1
            else:
                res = random.choice(["通过", "失败"])
                if res == "通过":
                    success += 1
                else:
                    fail += 1

            # 更新进度和表格
            progress = int((idx + 1) / len(test_devices) * 100)
            self.progress_update.emit(progress)
            self.table_update.emit(idx, port, dev_id, version, conn_status, res)
            self.result_update.emit(success, fail, skip, total)

        # 测试结束
        if self.is_running:
            self.status_update.emit(TEST_STATUS_FINISHED)
            self.log_update.emit(f"[{self.get_time()}] 测试完成！")
        else:
            self.status_update.emit(TEST_STATUS_STOPPED)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_running = False

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==============================
# 主窗口类
# ==============================
class AutoTestMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 加载UI
        self.load_ui()
        # 初始化UI元素
        self.init_ui()
        # 绑定事件
        self.bind_events()
        # 窗口配置
        self.setup_window()

        # 测试线程初始化
        self.test_thread = None

    def load_ui(self):
        """加载UI文件"""
        try:
            uic.loadUi(UI_FILE_PATH, self)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载UI失败：{str(e)}")
            sys.exit(1)

    def init_ui(self):
        """初始化UI元素（复用UI里的按钮，不再重复创建）"""
        # 1. 日志文本框：调整到按钮下方，复用UI里的 log_text_edit
        self.log_text_edit.setGeometry(10, 70, 271, 540)  # 按钮在上方，文本框在下方
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet("background-color: #f8f8f8; font-size: 12px; font-family: Consolas;")

        # 2. 测试数据表格（列：端口号、设备ID、软件版本、连接状态、测试结果）
        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 641, 581)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels([
            "端口号", "设备ID", "软件版本", "连接状态", "测试结果"
        ])
        self.test_data_table.setRowCount(10)  # 初始化10行（可根据实际调整）
        self.test_data_table.horizontalHeader().setStretchLastSection(True)

        # 3. 初始化下拉框
        self.aging_time_combo.addItems(["1小时", "2小时", "4小时", "8小时"])
        self.port_list_combo.addItems(["COM1", "COM2", "COM3", "COM4", "COM5"])

        # 4. 初始化测试结果显示
        self.total_case_value.setText(f"{TEST_CASE_TOTAL}条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")
        self.test_status_label.setText(TEST_STATUS_INIT)

        # 5. 初始化进度条
        self.test_progress_bar.setValue(0)

    def bind_events(self):
        """绑定所有控件事件（复用UI里的日志按钮）"""
        # 功能选项区域
        self.refresh_btn.clicked.connect(self.on_refresh_click)
        self.select_all_check.stateChanged.connect(self.on_select_all_click)

        # 执行控制区域
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)

        # 日志功能按钮（复用UI里已有的按钮，不再重复创建）
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)

        # 菜单栏
        self.load_script_action.triggered.connect(self.on_load_script)
        self.export_report_action.triggered.connect(self.on_export_report)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self.on_show_about)

        # 配置文件/主题菜单（预留逻辑）
        self.config_menu.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 配置文件菜单点击"))
        self.theme_menu.triggered.connect(lambda: self.log_text_edit.append(f"[{self.get_time()}] 主题菜单点击"))

    def setup_window(self):
        """窗口基础配置"""
        self.setWindowTitle(APP_TITLE)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # 禁用最大化

        # 窗口居中
        screen_geo = QApplication.primaryScreen().availableGeometry()
        window_geo = self.frameGeometry()
        window_geo.moveCenter(screen_geo.center())
        self.move(window_geo.topLeft())

        # 加载图标（可选）
        try:
            if os.path.exists(ICON_FILE):
                self.setWindowIcon(QIcon(ICON_FILE))
        except:
            pass

    def play_button_anim(self, btn):
        """按钮点击动画"""
        if not btn:
            return
        orig_w, orig_h = btn.width(), btn.height()

        # 宽度动画
        anim_w = QPropertyAnimation(btn, b"minimumWidth")
        anim_w.setDuration(BUTTON_ANIM_DURATION)
        anim_w.setStartValue(orig_w)
        anim_w.setEndValue(int(orig_w * BUTTON_ANIM_SCALE))
        anim_w.setEasingCurve(QEasingCurve.OutBounce)

        # 高度动画
        anim_h = QPropertyAnimation(btn, b"minimumHeight")
        anim_h.setDuration(BUTTON_ANIM_DURATION)
        anim_h.setStartValue(orig_h)
        anim_h.setEndValue(int(orig_h * BUTTON_ANIM_SCALE))
        anim_h.setEasingCurve(QEasingCurve.OutBounce)

        # 恢复尺寸
        def reset_size():
            btn.setMinimumWidth(orig_w)
            btn.setMinimumHeight(orig_h)

        anim_h.finished.connect(reset_size)
        anim_w.start()
        anim_h.start()

    # ==============================
    # 日志功能核心函数（复用UI按钮）
    # ==============================
    def on_copy_log(self):
        """拷贝日志到剪贴板"""
        self.play_button_anim(self.log_copy_btn)
        log_content = self.log_text_edit.toPlainText()
        if not log_content:
            QMessageBox.information(self, "提示", "暂无日志可拷贝！")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(log_content, QClipboard.Clipboard)
        self.log_text_edit.append(f"[{self.get_time()}] 日志已拷贝到剪贴板")

    def on_clear_log(self):
        """清空日志"""
        self.play_button_anim(self.log_clear_btn)
        self.log_text_edit.clear()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已清空")

    def on_save_log(self):
        """保存日志到本地文件"""
        self.play_button_anim(self.log_save_btn)
        log_content = self.log_text_edit.toPlainText()
        if not log_content:
            QMessageBox.information(self, "提示", "暂无日志可保存！")
            return
        
        # 弹出保存对话框
        default_filename = f"测试日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志文件", default_filename,
            "日志文件 (*.log *.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                self.log_text_edit.append(f"[{self.get_time()}] 日志已保存至：{os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", f"日志保存出错：{str(e)}")

    # ==============================
    # 原有事件处理函数
    # ==============================
    def on_refresh_click(self):
        """刷新端口列表"""
        self.play_button_anim(self.refresh_btn)
        self.log_text_edit.append(f"[{self.get_time()}] 刷新端口列表...")
        self.port_list_combo.clear()
        self.port_list_combo.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"])
        self.log_text_edit.append(f"[{self.get_time()}] 端口列表刷新完成")

    def on_select_all_click(self, state):
        """全选复选框"""
        status = "选中" if state == Qt.Checked else "取消选中"
        self.log_text_edit.append(f"[{self.get_time()}] 全选状态：{status}")

    def on_start_test(self):
        """开始测试"""
        self.play_button_anim(self.start_test_btn)
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.information(self, "提示", "测试已在运行中！")
            return

        # 重置状态
        self.test_progress_bar.setValue(0)
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")
        self.log_text_edit.clear()

        # 启动测试线程
        self.test_thread = TestThread(self)
        self.test_thread.progress_update.connect(self.test_progress_bar.setValue)
        self.test_thread.log_update.connect(self.log_text_edit.append)
        self.test_thread.table_update.connect(self.update_test_table)
        self.test_thread.result_update.connect(self.update_test_result)
        self.test_thread.status_update.connect(self.update_test_status)
        self.test_thread.start()

        # 日志记录
        aging_time = self.aging_time_combo.currentText()
        port = self.port_list_combo.currentText()
        self.log_text_edit.append(f"[{self.get_time()}] 启动测试（老化时间：{aging_time}，端口：{port}）")

    def on_stop_test(self):
        """停止测试"""
        self.play_button_anim(self.stop_test_btn)
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.stop()
            self.log_text_edit.append(f"[{self.get_time()}] 测试已停止")

    def on_pause_test(self):
        """暂停/恢复测试"""
        self.play_button_anim(self.pause_test_btn)
        if not self.test_thread or not self.test_thread.isRunning():
            QMessageBox.information(self, "提示", "暂无运行中的测试！")
            return

        if self.test_thread.is_paused:
            self.test_thread.resume()
            self.log_text_edit.append(f"[{self.get_time()}] 测试已恢复")
        else:
            self.test_thread.pause()
            self.log_text_edit.append(f"[{self.get_time()}] 测试已暂停")

    def on_load_script(self):
        """加载测试脚本"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择测试脚本", "", "Python脚本 (*.py);;所有文件 (*.*)"
        )
        if file_path:
            self.log_text_edit.append(f"[{self.get_time()}] 加载脚本：{os.path.basename(file_path)}")

    def on_export_report(self):
        """导出测试报告"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出测试报告", "", "Excel文件 (*.xlsx);;PDF文件 (*.pdf);;所有文件 (*.*)"
        )
        if file_path:
            self.log_text_edit.append(f"[{self.get_time()}] 报告导出至：{file_path}")

    def on_show_about(self):
        """显示关于弹窗"""
        QMessageBox.about(
            self, "关于",
            f"{APP_TITLE} v1.0.0\n© 2025 自动化测试平台\n适配UI：rohand.ui\n核心功能：测试控制、日志管理、结果统计"
        )

    # ==============================
    # 辅助更新函数
    # ==============================
    def update_test_table(self, row, port, dev_id, version, conn_status, result):
        """更新测试数据表格，结果颜色区分"""
        self.test_data_table.setItem(row, 0, QTableWidgetItem(port))
        self.test_data_table.setItem(row, 1, QTableWidgetItem(dev_id))
        self.test_data_table.setItem(row, 2, QTableWidgetItem(version))
        self.test_data_table.setItem(row, 3, QTableWidgetItem(conn_status))
        self.test_data_table.setItem(row, 4, QTableWidgetItem(result))

        # 连接状态颜色
        if conn_status == "已连接":
            self.test_data_table.item(row, 3).setForeground(QColor(0, 128, 0))
        else:
            self.test_data_table.item(row, 3).setForeground(QColor(255, 0, 0))

        # 测试结果颜色
        if result == "通过":
            self.test_data_table.item(row, 4).setForeground(QColor(0, 128, 0))
        elif result == "失败":
            self.test_data_table.item(row, 4).setForeground(QColor(255, 0, 0))
        elif result == "跳过":
            self.test_data_table.item(row, 4).setForeground(QColor(128, 128, 128))

    def update_test_result(self, success, fail, skip, total):
        """更新测试结果统计"""
        self.total_case_value.setText(f"{total}条")
        self.success_case_value.setText(f"{success}条")
        self.fail_case_value.setText(f"{fail}条")
        self.skip_case_value.setText(f"{skip}条")

    def update_test_status(self, status):
        """更新测试状态"""
        self.test_status_label.setText(status)
        if status == TEST_STATUS_FINISHED:
            self.test_status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status == TEST_STATUS_RUNNING:
            self.test_status_label.setStyleSheet("color: blue;")
        elif status == TEST_STATUS_STOPPED:
            self.test_status_label.setStyleSheet("color: red;")
        else:
            self.test_status_label.setStyleSheet("")

    def get_time(self):
        """获取格式化时间"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==============================
# 程序入口
# ==============================
if __name__ == "__main__":
    # 高DPI适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建应用
    app = QApplication(sys.argv)
    window = AutoTestMainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec_())