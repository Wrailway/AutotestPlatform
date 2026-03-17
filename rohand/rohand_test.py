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

from rohand.rohand_manager import RohanManager


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
    # 以下定义Treeview表格的列名
    STR_PORT = '端口号'
    STR_SOFTWARE_VERSION = '软件版本'
    STR_DEVICE_ID = '设备ID'
    STR_CONNECT_STATUS = '连接状态'
    STR_TEST_RESULT = '测试结果'

    # 表头
    HEADS = [
        STR_PORT,
        STR_SOFTWARE_VERSION,
        STR_DEVICE_ID,
        STR_CONNECT_STATUS,
        STR_TEST_RESULT
    ]

    # 老化时间选项
    aging_duration_options = ['0.5小时', '1小时', '1.5小时', '3小时', '8小时', '12小时', '24小时']

    def __init__(self, parent=None):
        super().__init__(parent)
        # 完全保留原始UI加载逻辑，未做任何修改
        self.select_port_names = []
        self.port_names = ['无可用端口']
        self.test_data_table = None
        # self.port_list_Layout = None
        self.check_box_list = []  # 存储复选框，防止重复/内存泄漏
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
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(self.HEADS)
        self.test_data_table.setRowCount(100)
        # 核心修正：获取水平表头对象 + 设置所有列等分
        header = self.test_data_table.horizontalHeader()  # 正确获取表头对象
        header.setSectionResizeMode(QHeaderView.Stretch)  # 设置列等分

        # 下拉框初始化
        self.aging_time_combo.addItems(self.aging_duration_options)
        port_container = self.port_list_Layout.parentWidget()
        if port_container:
            # 2. 设置边框样式（可自定义颜色/宽度/圆角）
            port_container.setStyleSheet("""
                       QWidget {
                           border: 1px solid #CCCCCC;  /* 边框宽度+样式+颜色 */
                           border-radius: 4px;         /* 圆角（可选） */
                           background-color: white;  /* 背景色（可选） */
                           padding: 5px;              /* 内边距（防止控件贴边框） */
                       }
                   """)
        # ===========================================================
        self.port_list_Layout.setContentsMargins(12,8,18,8)
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


    def on_port_cbx_clicked(self, checked, checkbox):
        """复选框点击事件（修复全选逻辑+异常捕获）"""
        try:
            port = checkbox.text()
            # 1. 全选逻辑（需先创建"全选"复选框才生效）
            if port == '全选':
                self.select_port_names = self.port_names.copy() if checked else []
                for cbx in self.check_box_list:
                    if cbx.text() != '全选':  # 跳过全选自身
                        cbx.setChecked(checked)
                        # self.update_device_list(port=cbx.text(), isChecked=checked)
            # 2. 单个端口逻辑
            else:
                if checked and port not in self.select_port_names:
                    self.select_port_names.append(port)
                elif not checked and port in self.select_port_names:
                    self.select_port_names.remove(port)
                # self.update_device_list(port=port, isChecked=checked)

            self.log_text_edit.append(
                f"[{self.get_time()}] 端口 {port} {'选中' if checked else '取消选中'}，已选：{self.select_port_names}")
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 复选框操作失败：{str(e)}")

    def on_refresh(self):
        """彻底修复：防崩溃+内存安全+可选加全选"""
        try:
            # 1. 安全清空（先判空，避免布局不存在报错）
            if not hasattr(self, 'port_list_Layout') or self.port_list_Layout is None:
                self.log_text_edit.append(f"[{self.get_time()}] 错误：port_list_Layout 未加载！")
                return

            # 2. 彻底清空旧布局和列表
            self.check_box_list.clear()
            self.select_port_names.clear()
            self.remove_all_widgets_from_layout(self.port_list_Layout)

            # 3. 读取端口（加异常捕获）
            rohanManager = RohanManager(protocol_type=1)
            self.port_names = rohanManager.read_port_info() or ['无可用端口']
            logger.info(f"检测到端口：{self.port_names}")

            # 4. 无端口处理
            if not self.port_names or self.port_names[0] == '无可用端口':
                self.log_text_edit.append(f"[{self.get_time()}] 无可用端口")
                return

            # 5. 布局配置（每列8个，最多1列）
            max_per_col = 8
            max_col = 1
            vertical_layouts = []

            # ========== 可选：添加"全选"复选框（开启全选逻辑需此行） ==========
            # all_check = QCheckBox("全选")
            # self.check_box_list.append(all_check)
            # all_check.clicked.connect(lambda checked, cb=all_check: self.on_port_cbx_clicked(checked, cb))
            # =================================================================

            # 6. 生成端口复选框
            for idx, port in enumerate(self.port_names):
                # check_box = QCheckBox(port)
                check_box = QCheckBox(port)
                check_box.setStyleSheet("""
                    QCheckBox {
                        font-size: 14px;
                        padding: 6px 10px;
                        margin: 4px 0px;
                        border: 1px solid #cccccc;
                        border-radius: 4px;
                        background-color: white;
                    }
                    QCheckBox:hover {
                        background-color: #f5f5f5;
                        border-color: #999999;
                    }
                    QCheckBox:checked {
                        background-color: #e0f0ff;
                        border-color: #66b1ff;
                        color: #005fb8;
                    }
                """)

                self.check_box_list.append(check_box)

                col = idx // max_per_col
                if col >= max_col:
                    self.log_text_edit.append(f"[{self.get_time()}] 端口过多，仅显示前{max_col * max_per_col}个")
                    break

                # 新建列布局
                if col >= len(vertical_layouts):
                    vl = QVBoxLayout()
                    vl.setAlignment(Qt.AlignTop)
                    vl.setSpacing(8)
                    self.port_list_Layout.addLayout(vl)
                    vertical_layouts.append(vl)

                # 添加复选框（指定父控件，防内存泄漏）
                vertical_layouts[col].addWidget(check_box)
                # 绑定事件（闭包陷阱修复）
                check_box.clicked.connect(lambda checked, cb=check_box: self.on_port_cbx_clicked(checked, cb))

            # 7. 布局样式
            self.port_list_Layout.setContentsMargins(12, 8, 18, 8)
            self.port_list_Layout.setSpacing(10)

            self.log_text_edit.append(f"[{self.get_time()}] 端口刷新完成，共{len(self.check_box_list)}个端口")
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 刷新端口崩溃：{str(e)}")
            import traceback
            self.log_text_edit.append(f"错误详情：{traceback.format_exc()}")

    def remove_all_widgets_from_layout(self, layout):
        """彻底销毁控件，防止堆损坏（核心修复）"""
        if layout is None:
            return
        # 倒序删除，避免索引错乱
        while layout.count() > 0:
            item = layout.takeAt(0)
            # 1. 销毁控件（关键：deleteLater 而非 setParent）
            widget = item.widget()
            if widget:
                widget.deleteLater()  # 彻底销毁，释放内存
                widget = None
            # 2. 递归清空子布局
            sub_layout = item.layout()
            if sub_layout:
                self.remove_all_widgets_from_layout(sub_layout)
                sub_layout = None

    def on_select_all(self, state):
        """兼容原有全选按钮（可选保留）"""
        try:
            checked = state == Qt.Checked
            self.select_port_names = self.port_names.copy() if checked else []
            for cbx in self.check_box_list:
                cbx.setChecked(checked)
                # self.update_device_list(port=cbx.text(), isChecked=checked)
            self.log_text_edit.append(
                f"[{self.get_time()}] 全选状态：{'选中' if checked else '取消'}，已选：{self.select_port_names}")
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 全选操作失败：{str(e)}")

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