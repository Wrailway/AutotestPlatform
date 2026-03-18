#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import random
from datetime import datetime

import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi

from rohand.can_client import CanClient
from rohand.modbus_client import ModbusClient
from rohand.rohand_manager import RohanManager

# 如果你的 rohand_manager 有问题，这里先注释掉模拟运行
# from rohand.rohand_manager import RohanManager


# ==============================
# 变量定义
# ==============================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ==============================
# 测试线程类
# ==============================
class TestThread(QThread):
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    table_update = pyqtSignal(int, str, str, str, str)
    result_update = pyqtSignal(int, int, int, int)
    status_update = pyqtSignal(str)
    test_one_port = pyqtSignal(str)  # 通知UI：正在测试某个端口

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.is_paused = False
        self.test_ports = []

    def run(self):
        total = len(self.test_ports)
        success = fail = skip = 0
        self.status_update.emit("测试开始...")
        self.log_update.emit(f"[{self.get_time()}] 测试启动，端口列表：{self.test_ports}")

        for i, port in enumerate(self.test_ports):
            if not self.is_running:
                break
            while self.is_paused:
                self.msleep(100)

            # 通知主界面更新当前测试端口（你可以用来高亮、刷新状态等）
            self.test_one_port.emit(port)

            # ======================
            # 这里替换成你的真实测试逻辑
            # ======================
            res = random.choice(["通过", "失败", "跳过"])
            success += 1 if res == "通过" else 0
            fail += 1 if res == "失败" else 0
            skip += 1 if res == "跳过" else 0

            self.progress_update.emit(int((i + 1) / total * 100))
            self.log_update.emit(f"[{self.get_time()}] {port} 结果：{res}")
            self.result_update.emit(total, success, fail, skip)
            self.msleep(300)

        if self.is_running:
            self.status_update.emit("测试完成！")
            self.log_update.emit(f"[{self.get_time()}] 测试结束 - 成功：{success} 失败：{fail} 跳过：{skip}")
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
# 主窗口类
# ==============================
class RoHandTestWindow(QMainWindow):
    STR_PORT = '端口号'
    STR_SOFTWARE_VERSION = '软件版本'
    STR_DEVICE_ID = '设备ID'
    STR_CONNECT_STATUS = '连接状态'
    STR_TEST_RESULT = '测试结果'

    HEADS = [
        STR_PORT,
        STR_SOFTWARE_VERSION,
        STR_DEVICE_ID,
        STR_CONNECT_STATUS,
        STR_TEST_RESULT
    ]

    aging_duration_options = ['0.5小时', '1小时', '1.5小时', '3小时', '8小时', '12小时', '24小时']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.select_port_names = []
        self.port_names = ['无可用端口']
        self.test_data_table = None
        self.check_box_list = []
        self.port_row_map = {}  # 端口号 -> 行号 映射（核心）

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "rohand_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(current_dir, "ui", "rohand_test.ui")
        loadUi(ui_path, self)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.init_ui()
        self.bind_all_events()
        self.test_thread = TestThread(self)
        self.bind_thread_signals()

    def init_ui(self):
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setStyleSheet("font-family: Consolas; font-size: 14px;")

        # 测试表格
        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(self.HEADS)
        self.test_data_table.setRowCount(0)
        header = self.test_data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.aging_time_combo.addItems(self.aging_duration_options)
        self.port_list_Layout.setContentsMargins(8, 8, 8, 8)

        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)

        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")

    # ==============================
    # 表格核心：增删行（按端口）
    # ==============================
    def add_port_row(self, port):
        if port in self.port_row_map:
            return
        row = self.test_data_table.rowCount()
        self.test_data_table.insertRow(row)
        self.port_row_map[port] = row

        # ======================
        # 这里填你从客户端读的真实信息
        # ======================
        version = self.get_device_version(port)
        dev_id = self.get_device_id(port)
        connect_status = self.get_connect_status(port)

        self.test_data_table.setItem(row, 0, QTableWidgetItem(port))
        self.test_data_table.setItem(row, 1, QTableWidgetItem(version))
        self.test_data_table.setItem(row, 2, QTableWidgetItem(dev_id))
        self.test_data_table.setItem(row, 3, QTableWidgetItem(connect_status))
        self.test_data_table.setItem(row, 4, QTableWidgetItem("待测试"))

    def remove_port_row(self, port):
        if port not in self.port_row_map:
            return
        row = self.port_row_map[port]
        self.test_data_table.removeRow(row)
        del self.port_row_map[port]

        # 重新映射行号
        new_map = {}
        for p, r in self.port_row_map.items():
            if r > row:
                new_map[p] = r - 1
            else:
                new_map[p] = r
        self.port_row_map = new_map

    # ==============================
    # 【预留接口】你自己实现
    # ==============================
    def get_device_version(self, port):
        # 从你的客户端获取版本
        return "V1.0.0"

    def get_device_id(self, port):
        # 从你的客户端获取设备ID
        return "DEV_" + port

    def get_connect_status(self, port):
        # 从你的客户端获取连接状态
        return "已连接"

    def get_test_result(self, port):
        # 测试完成后从接口拿结果
        return "通过"

    # ==============================
    # 复选框逻辑（选中/取消 增删行）
    # ==============================
    def on_port_cbx_clicked(self, checked, checkbox):
        port = checkbox.text()
        if checked:
            if port not in self.select_port_names:
                self.select_port_names.append(port)
                self.add_port_row(port)
        else:
            if port in self.select_port_names:
                self.select_port_names.remove(port)
                self.remove_port_row(port)
        self.log_text_edit.append(f"[{self.get_time()}] {port} {'选中' if checked else '取消'}")

    def get_device_list(self):
        protocol_type = 1 # 先指定为can协议，后续从配置文件去读取
        client = None

        rohan = RohanManager(protocol_type)
        port_names = rohan.read_port_info() or ['无可用端口']

        if not port_names or port_names[0] == '无可用端口':
            return None
        for port in port_names:
            if protocol_type == 0:
                client = ModbusClient(port=port)
            else:
                client = CanClient(port=port)
            client.connect()
            client.disconnect()

    def on_refresh(self):
        try:
            self.check_box_list.clear()
            self.select_port_names.clear()
            self.port_row_map.clear()
            self.test_data_table.setRowCount(0)
            self.remove_all_widgets_from_layout(self.port_list_Layout)

            # 模拟端口，正式版替换成 RohanManager
            rohan = RohanManager(1)
            self.port_names = rohan.read_port_info() or ['无可用端口']
            # self.port_names = [f"COM{i}" for i in range(1, 16)]  # 模拟15个端口

            if not self.port_names or self.port_names[0] == '无可用端口':
                self.log_text_edit.append(f"[{self.get_time()}] 无可用端口")
                return

            max_per_col = 8
            vertical_layouts = []

            for idx, port in enumerate(self.port_names):
                check_box = QCheckBox(port)
                check_box.setStyleSheet("""
                    QCheckBox {
                        font-size:14px; padding:6px 10px; margin:4px 0;
                        border:1px solid #ccc; border-radius:4px; background:white;
                    }
                    QCheckBox:hover { background:#f5f5f5; border-color:#999; }
                    QCheckBox:checked { background:#e0f0ff; border-color:#66b1ff; }
                """)
                self.check_box_list.append(check_box)

                col = idx // max_per_col
                if col >= len(vertical_layouts):
                    vl = QVBoxLayout()
                    vl.setAlignment(Qt.AlignTop)
                    vl.setSpacing(6)
                    self.port_list_Layout.addLayout(vl)
                    vertical_layouts.append(vl)

                vertical_layouts[col].addWidget(check_box)
                check_box.clicked.connect(lambda checked, cb=check_box: self.on_port_cbx_clicked(checked, cb))

            self.log_text_edit.append(f"[{self.get_time()}] 端口刷新完成：{len(self.check_box_list)}个")
        except Exception as e:
            self.log_text_edit.append(f"刷新错误：{str(e)}")

    def on_select_all(self, state):
        checked = state == Qt.Checked
        for cbx in self.check_box_list:
            cbx.setChecked(checked)

    def remove_all_widgets_from_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            sub = item.layout()
            if sub:
                self.remove_all_widgets_from_layout(sub)

    # ==============================
    # 测试控制
    # ==============================
    def on_start_test(self):
        if not self.select_port_names:
            self.log_text_edit.append(f"[{self.get_time()}] 请先选择端口！")
            return
        if self.test_thread.isRunning():
            return
        self.test_thread.test_ports = self.select_port_names.copy()
        self.test_thread.is_running = True
        self.test_thread.is_paused = False
        self.test_thread.start()

    def on_pause_test(self):
        if self.test_thread.isRunning():
            if self.test_thread.is_paused:
                self.test_thread.resume()
            else:
                self.test_thread.pause()

    def on_stop_test(self):
        if self.test_thread.isRunning():
            self.test_thread.stop()

    # ==============================
    # 线程信号绑定
    # ==============================
    def bind_thread_signals(self):
        self.test_thread.progress_update.connect(self.test_progress_bar.setValue)
        self.test_thread.log_update.connect(self.log_text_edit.append)
        self.test_thread.result_update.connect(self.update_test_result)
        self.test_thread.status_update.connect(self.status_bar.showMessage)
        self.test_thread.test_one_port.connect(self.update_test_result_for_port)

    def update_test_result_for_port(self, port):
        """测试完一个端口，更新结果列"""
        if port not in self.port_row_map:
            return
        row = self.port_row_map[port]
        res = self.get_test_result(port)
        item = QTableWidgetItem(res)
        if res == "通过":
            item.setForeground(QColor(0, 180, 0))
        elif res == "失败":
            item.setForeground(QColor(255, 0, 0))
        else:
            item.setForeground(QColor(200, 160, 0))
        self.test_data_table.setItem(row, 4, item)

    def update_test_result(self, total, success, fail, skip):
        self.total_case_value.setText(f"{total}条")
        self.success_case_value.setText(f"{success}条")
        self.fail_case_value.setText(f"{fail}条")
        self.skip_case_value.setText(f"{skip}条")

    # ==============================
    # 下面是你原来的日志、菜单、主题等，完全保留
    # ==============================
    def bind_all_events(self):
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.select_all_check.stateChanged.connect(self.on_select_all)
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)

        self.action_loadScript.triggered.connect(self.on_load_script)
        self.action_exportReport.triggered.connect(self.on_export_report)
        self.action_exit.triggered.connect(self.close)
        self.action_viewConfigFile.triggered.connect(self.on_view_config)
        self.action_editConfigFile.triggered.connect(self.on_edit_config)
        self.action_blackTheme.triggered.connect(self.on_theme_black)
        self.action_greenTheme.triggered.connect(self.on_theme_green)
        self.action_defaultTheme.triggered.connect(self.on_theme_default)
        self.action_about.triggered.connect(self.on_about)

    def on_copy_log(self):
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已拷贝")

    def on_clear_log(self):
        self.log_text_edit.clear()
        self.log_text_edit.append(f"[{self.get_time()}] 日志已清空")

    def on_save_log(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存日志", f"日志_{self.get_time()}.txt".replace(":", "-"), "*.txt")
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text_edit.toPlainText())
            self.log_text_edit.append(f"[{self.get_time()}] 日志已保存")

    def on_load_script(self):
        fn, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "*.py;;*.*")
        if fn:
            self.log_text_edit.append(f"[{self.get_time()}] 加载脚本：{os.path.basename(fn)}")

    def on_export_report(self):
        fn, _ = QFileDialog.getSaveFileName(self, "导出报告", f"报告_{self.get_time()}.txt".replace(":", "-"), "*.txt")
        if fn:
            self.log_text_edit.append(f"[{self.get_time()}] 报告已导出")

    def on_view_config(self):
        fn, _ = QFileDialog.getOpenFileName(self, "查看配置", "", "*.ini *.json *.conf")
        if fn:
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    content = f.read()[:1000]
                QMessageBox.information(self, "配置内容", content)
                self.log_text_edit.append(f"[{self.get_time()}] 查看配置：{os.path.basename(fn)}")
            except:
                pass

    def on_edit_config(self):
        fn, _ = QFileDialog.getOpenFileName(self, "编辑配置", "", "*.ini *.json *.conf")
        if fn and sys.platform == "win32":
            os.startfile(fn)

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

    def on_theme_green(self):
        style = """
        QMainWindow { background-color: #eafaf1; }
        QGroupBox { border: 2px solid #27ae60; }
        QGroupBox::title { color: #219653; }
        QPushButton { background-color: #27ae60; color: white; }
        QProgressBar::chunk { background-color: #27ae60; }
        """
        self.setStyleSheet(style)

    def on_theme_default(self):
        self.setStyleSheet("")

    def on_about(self):
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0")

    @staticmethod
    def get_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def closeEvent(self, event):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        event.accept()


# ==============================
# 入口
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RoHandTestWindow()
    win.setWindowTitle("灵巧手自动化测试界面")
    win.show()
    sys.exit(app.exec_())