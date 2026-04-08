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
from datetime import datetime

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
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi

from app.app_common import TABLE_HEADERS, DEFAULT_EXECUTE_TIMES_OPTIONS, DEFAULT_OPERATE_INTERVAL_OPTIONS
from app.app_logger import APPHandLogger
from app.app_manager import APPManager
from app_theme import apply_black_style, apply_green_style, apply_default_style

# ---------------------------------------------------------------------------
# 公共模块导入：常量、工具函数、共享数据操作
# ---------------------------------------------------------------------------


class APPTestWindow(QMainWindow):
    """主窗口类：集成UI显示、设备管理、测试控制、报告导出"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ===================== 全局变量初始化 =====================

        # UI组件
        self.selected_operate_interval = 1
        self.selected_execute_times = 1
        self.test_data_table = None
        self.check_box_list = []
        self.script_loaded = False
        self.script_path = None



        # 脚本与报告
        self.script_name = None
        self.report_title = None
        self.raw_test_data = None

        # 测试状态
        self.stop_test = False
        self.pause_test = False

        # 工作线程
        self.executeScriptWorker = None
        self.deviceInfosWorker = None
        self.progressbar_worker = None

        # ===================== 加载UI文件 =====================
        base = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base, "app_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(base, "ui", "app_test.ui")
        loadUi(ui_path, self)

        # ===================== 窗口属性设置 =====================
        flags = self.windowFlags()
        flags &= ~Qt.WindowMaximizeButtonHint
        flags |= Qt.WindowSystemMenuHint | Qt.WindowTitleHint
        self.setWindowFlags(flags)

        # ===================== 初始化与绑定 =====================
        self._init_ui_widgets()
        self._bind_all_events()

        self._init_manager()
        self.closeEvent = self.close_event_handler

    def close_event_handler(self, event):
        """窗口关闭事件：清理共享数据文件"""
        event.accept()

    # ------------------------------------------------------------------
    # UI 组件初始化
    # ------------------------------------------------------------------
    def setMenuItemStyle(self, menu: QMenu):
        """设置菜单样式：统一高度、宽度、字体大小"""
        menu.setStyleSheet("""
            QMenu::item {
                height: 20px;
                width: 200px;
                margin: 0px 0px;
                font-size: 16px;
            }
        """)

    class CenterAlignDelegate(QStyledItemDelegate):
        """表格内容居中代理：修复PyQt5对齐不生效问题"""
        def initStyleOption(self, option, index):
            super().initStyleOption(option, index)
            option.displayAlignment = Qt.AlignCenter

    def _init_ui_widgets(self):
        """初始化所有UI组件样式与默认值"""
        self.setMenuItemStyle(self.menu_file)
        self.setMenuItemStyle(self.menu_config)
        self.setMenuItemStyle(self.menu_theme)
        self.setMenuItemStyle(self.menu_help)

        # 日志框
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 10))

        self.execute_times_combo.clear()
        self.execute_times_combo.addItems(DEFAULT_EXECUTE_TIMES_OPTIONS)

        self.operate_interval_combo.clear()
        self.operate_interval_combo.addItems(DEFAULT_OPERATE_INTERVAL_OPTIONS)

        # 测试数据表格
        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(3)
        self.test_data_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.test_data_table.setRowCount(0)
        self.test_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.test_data_table.setItemDelegate(self.CenterAlignDelegate())


        # 进度条
        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)
        self.test_progress_bar.setStyleSheet("QProgressBar { color: #000000; font-weight: bold; }")

        # 统计数据初始化
        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")


    # ------------------------------------------------------------------
    # 组件事件绑定
    # ------------------------------------------------------------------
    def _bind_all_events(self):
        """绑定所有按钮、菜单、组件的信号与槽函数"""
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

        # 文件菜单
        self.action_loadScript.triggered.connect(self.on_load_script)
        self.action_exportReport.triggered.connect(self.on_export_report)
        self.action_exit.triggered.connect(self.close)

        # 配置菜单
        self.action_viewConfigFile.triggered.connect(self.on_view_config)
        self.action_editConfigFile.triggered.connect(self.on_edit_config)

        # 主题菜单
        self.action_blackTheme.triggered.connect(self.on_theme_black)
        self.action_greenTheme.triggered.connect(self.on_theme_green)
        self.action_defaultTheme.triggered.connect(self.on_theme_default)

        # 帮助菜单
        self.action_about.triggered.connect(self.on_about)

    # ------------------------------------------------------------------
    # 业务管理器初始化
    # ------------------------------------------------------------------
    def _init_manager(self):
        """初始化日志、协议、设备管理对象"""
        print('_init_manager')
        self.rologger = APPHandLogger(self.log_text_edit)


    # ------------------------------------------------------------------
    # 控件响应函数
    # ------------------------------------------------------------------

    def on_test_type_changed(self, checked):
        """ 测试类型切换时自动调用 """
        if not checked:
            return  # 只处理“选中”的事件，避免重复触发

        # 判断当前选中哪个
        if self.funtion_radio_button.isChecked():
            self.rologger.log("当前选中：基本功能测试")
            # 在这里写 基本功能 的逻辑

        elif self.monkey_radio_button.isChecked():
            self.rologger.log("当前选中：Monkey 测试")
            # 在这里写 Monkey 的逻辑

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
        """复制日志内容到剪贴板"""
        self.rologger.log('on_copy_log')
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()

    def on_clear_log(self):
        """清空日志显示框"""
        self.rologger.log('on_clear_log')
        self.log_text_edit.clear()

    def on_save_log(self):
        """保存日志到本地文件"""
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
        """日志级别按钮：弹出级别选择菜单"""
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
        """设置日志输出级别"""
        try:
            self.rologger.set_log_level(level)
            self.rologger.log(f"日志级别已设置为：{level}")
        except Exception as e:
            self.rologger.log(f"设置日志级别失败：{str(e)}")

    def update_test_datas_table(self):
        """根据选中端口更新测试设备表格"""
        self.rologger.log('update_test_datas_table')

    def get_row_by_port(self, port):
        """根据端口号查找表格行号，未找到返回-1"""
        for row in range(self.test_data_table.rowCount()):
            item = self.test_data_table.item(row, 0)
            if item and item.text() == port:
                return row
        return -1

    def _on_device_info_update(self, device_info_test):
        """设备信息更新：刷新表格显示"""
        self.rologger.log('_on_device_info_update')

    def update_table_column_by_port(self, port, column_index, value):
        """根据端口号更新表格指定列的值"""
        self.rologger.log('update_table_column_by_port')


    def set_controls_enabled(self, enabled):
        """批量设置控制按钮启用/禁用状态"""
        controls = [
            self.start_test_btn,
            self.pause_test_btn,
            self.stop_test_btn
        ]
        for control in controls:
            control.setEnabled(enabled)

    # ------------------------------------------------------------------
    # 测试控制：开始 / 暂停 / 停止
    # ------------------------------------------------------------------
    def on_start_test(self):
        """开始测试按钮点击事件"""
        self.rologger.log('on_start_test')
        # self.rologger.log(f"script_name = {self.script_name}")
        #
        # if not self.script_name:
        #     self.status_bar.showMessage(f"请选择测试脚本")
        #     return
        #
        # if self.executeScriptWorker is not None and self.executeScriptWorker.isRunning():
        #     return
        #
        # # 重置测试状态
        # self.pause_test = False
        # self.stop_test = False
        #
        # # # 计算总测试时长
        # # self.total_test_seconds = self.selected_execute_times * 3600
        # #
        #
        # # 启动脚本执行线程
        # self.executeScriptWorker = ExecuteScriptWorker(
        #     self.port_names_selected,
        #     self.selected_cases_ids,
        #     self.selected_aging_hours,
        #     self.script_name
        # )
        # self.executeScriptWorker.finished_with_script_result.connect(self._on_script_finished_result)
        # self.executeScriptWorker.start()
        #
        # # 启动进度条线程
        # self.test_progress_bar.setRange(0, 100)
        # self.test_progress_bar.setValue(0)
        # self.progressbar_worker = ProgressBarWorker(duration=self.total_test_seconds)
        # self.progressbar_worker.progress_update.connect(self._on_progress_result)
        # self.progressbar_worker.finished_signal.connect(self.on_test_finished_auto)
        # self.progressbar_worker.start()

        self.status_bar.showMessage("开始测试...")

    def _on_progress_result(self, value):
        """更新进度条显示"""
        self.test_progress_bar.setValue(value)

    def on_test_finished_auto(self):
        """测试时间结束自动完成"""
        self.status_bar.showMessage("测试已完成")
        self.rologger.log("老化测试时间到，自动结束")

    def _on_script_finished_result(self, titles, result):
        """脚本执行完成，解析并更新测试结果"""
        self.rologger.log(f'_on_script_finished_result')
        self.rologger.log(f'titles = {titles},result = {result}')

        self.report_title = titles
        self.raw_test_data = result

        # 按端口分组解析结果
        port_data_dict = self.parse_test_result(result)

        # 更新每个端口的最终测试状态
        for port, table_rows in port_data_dict.items():
            final_result = "通过"
            for row_data in table_rows:
                if row_data[2] != "通过":
                    final_result = "不通过"
                    break
            self.update_table_column_by_port(port, 4, final_result)
            self.rologger.log(f"端口 {port} 最终测试结果：{final_result}")

        self._update_test_result(self.raw_test_data)

    def _update_test_result(self, raw_test_data):
        """更新测试统计数据与状态标签"""
        self.rologger.log(f'_update_test_result')
        port_data_dict = self.parse_test_result(raw_test_data)

        total_count = 0
        success_count = 0
        failed_count = 0

        for port, table_rows in port_data_dict.items():
            for row_data in table_rows:
                test_result = row_data[2]
                total_count += 1
                if test_result == "通过":
                    success_count += 1
                else:
                    failed_count += 1

        # 更新UI统计
        self.rologger.log(f'total_count={total_count},success_count={success_count},failed_count={failed_count}')
        self.total_case_value.setText(str(total_count))
        self.success_case_value.setText(str(success_count))
        self.fail_case_value.setText(str(failed_count))

        # 更新状态标签
        if failed_count == 0 and total_count > 0:
            self.test_status_label.setStyleSheet("color: #2E8B57; font-size:14px; font-weight:bold;")
            self.test_status_label.setText("✅ 测试完成 | 全部用例通过")
        elif total_count == 0:
            self.test_status_label.setStyleSheet("color: #696969; font-size:14px;")
            self.test_status_label.setText("⌛ 等待测试 | 暂无用例执行")
        else:
            self.test_status_label.setStyleSheet("color: #DC143C; font-size:14px; font-weight:bold;")
            self.test_status_label.setText("❌ 测试完成 | 存在失败用例")

    def parse_test_result(self, result):
        """解析测试结果，按端口分组返回表格数据"""
        self.rologger.log('开始解析测试结果数据，用于表格刷新')
        port_data_dict = {}

        for item in result:
            port = item['port']
            if port not in port_data_dict:
                port_data_dict[port] = []

            for gesture in item['gestures']:
                table_row = (
                    gesture['timestamp'],
                    gesture['content'],
                    gesture['result'],
                    gesture['comment']
                )
                port_data_dict[port].append(table_row)

        self.rologger.log(f'测试结果解析完成，共解析到端口：{list(port_data_dict.keys())}')
        return port_data_dict

    def on_pause_test(self):
        """测试暂停/恢复切换"""
        self.rologger.log('on_pause_test')
        #
        # if self.executeScriptWorker is None:
        #     self.status_bar.showMessage('当前没有在执行的任务')
        #     return
        #
        # if self.stop_test:
        #     self.status_bar.showMessage('当前无测试脚本在运行')
        #     return
        #
        # self.pause_test = not self.pause_test
        #
        # if self.pause_test:
        #     self.progressbar_worker.pause()
        #     self.pause_test_btn.setText("继续测试")
        #     self.status_bar.showMessage('当前任务已暂停，点击继续执行')
        #     self.rologger.log("测试已暂停")
        # else:
        #     self.progressbar_worker.resume()
        #     self.pause_test_btn.setText("暂停测试")
        #     self.status_bar.showMessage('当前任务已恢复执行')
        #     self.rologger.log("测试已恢复")

    def on_stop_test(self):
        """停止当前测试任务"""
        self.rologger.log(f'on_stop_test')

        # if self.executeScriptWorker is None:
        #     self.status_bar.showMessage('当前没有在执行的任务')
        #     return
        #
        # self.stop_test = True
        # self.pause_test = True
        #
        # self.status_bar.showMessage("正在停止任务...")
        # self.progressbar_worker.stop()
        #
        # def _on_task_finished(title, result):
        #     self.on_test_finished_auto()
        #     self.status_bar.showMessage("当前任务已停止")
        #     self.stop_test = False
        #     self.pause_test = False
        #     self.executeScriptWorker.finished_with_script_result.disconnect(_on_task_finished)
        #
        # self.executeScriptWorker.finished_with_script_result.connect(_on_task_finished)
        # self.executeScriptWorker.stop_task()

    # ------------------------------------------------------------------
    # 加载脚本与输出报告
    # ------------------------------------------------------------------
    def on_load_script(self):
        """加载测试脚本"""
        self.rologger.log(f'on_load_script')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(base_dir, "scripts")

        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)

        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择要执行的脚本', scripts_dir, 'Python files (*.py)'
        )

        if file_path:
            self.script_name = file_path
            self.rologger.log(f'成功加载脚本：{self.script_name}')
            self.rologger.log(f'请点击【开始测试】按钮执行脚本\n')

    def on_export_report(self):
        """导出测试报告为Excel文件"""
        self.rologger.log(f'on_export_report')
        if not self.raw_test_data:
            self.rologger.log("导出失败：无测试数据")
            self.status_bar.showMessage(f"尚未进行测试，无数据可导出")
            return

        if not self.report_title:
            self.rologger.log("导出失败：报告标题为空")
            self.status_bar.showMessage(f"请设置报告标题")
            return

        # 表格样式定义
        headers = ["用例编号", "时间戳", "内容", "测试结果", "备注", "端口号"]
        column_widths = [10, 25, 35, 12, 15, 18]
        default_row_height = 35
        thin_border = Border(left=Side('thin'), right=Side('thin'), top=Side('thin'), bottom=Side('thin'))
        alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        wb = Workbook()
        ws = wb.active
        ws.title = "测试报告"

        # 标题
        ws.merge_cells('A1:F1')
        ws['A1'] = self.report_title
        ws['A1'].font = Font(bold=True, size=16)
        ws['A1'].alignment = alignment
        ws.row_dimensions[1].height = default_row_height

        # 基础信息行
        ws['A2'] = '产品名称'
        ws['C2'] = '产品型号'
        ws.merge_cells('D2:F2')
        ws['A3'] = '测试地点'
        ws['C3'] = '测试时间'
        ws.merge_cells('D3:F3')
        ws['A4'] = '测试设备'
        ws['C4'] = '设备编号'
        ws.merge_cells('D4:F4')
        ws['A5'] = '温度'
        ws['C5'] = '湿度'
        ws.merge_cells('D5:F5')

        # 表头
        ws.append(headers)
        ws.row_dimensions[6].height = default_row_height

        # 写入数据
        row_index = 7
        for item in self.raw_test_data:
            try:
                port = item["port"]
                for g in item["gestures"]:
                    ts = g.get("timestamp", "")
                    content = str(g.get("content", ""))
                    res = g.get("result", "")
                    comment = g.get("comment", "")

                    ws.append([row_index - 6, ts, content, res, comment, port])
                    row_index += 1
            except Exception as e:
                self.rologger.log(f"数据处理异常: {e}")

        # 设置列宽与样式
        for i, w in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = alignment
                cell.border = thin_border

        # 保存文件
        os.makedirs("report", exist_ok=True)
        name = os.path.splitext(os.path.basename(self.script_name))[0]
        filename = f"{name}_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = os.path.join("report", filename)

        wb.save(filepath)
        QMessageBox.information(self, "成功", f"报告已保存：\n{filepath}")

    # ------------------------------------------------------------------
    # 配置文件操作
    # ------------------------------------------------------------------
    def on_view_config(self):
        """查看配置文件（只读）"""
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
        """编辑配置文件（可写）"""
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
        """保存配置并重启程序"""
        try:
            with open(config_path, 'w', encoding='UTF-8') as f:
                f.write(content)

            self.rologger.log(f"配置文件已保存：{config_path}")
            QMessageBox.information(self, "成功", "配置文件已保存，应用程序将自动重启...")
            dialog.accept()

            script_path = os.path.abspath(sys.argv[0])
            subprocess.Popen(
                [sys.executable, script_path],
                start_new_session=True,
                creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0
            )

            time.sleep(0.5)
            QApplication.quit()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")
            self.rologger.log(f"保存配置文件失败：{str(e)}")

    # ------------------------------------------------------------------
    # 主题切换
    # ------------------------------------------------------------------
    def on_theme_black(self):
        self.rologger.log("on_theme_black")
        apply_black_style(self)

    def on_theme_green(self):
        self.rologger.log("on_theme_green")
        apply_green_style(self)

    def on_theme_default(self):
        self.rologger.log(f"on_theme_default")
        apply_default_style(self)

    # ------------------------------------------------------------------
    # 关于
    # ------------------------------------------------------------------
    def on_about(self):
        self.rologger.log(f"on_about")
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0\n基于PyQt5开发")


# ---------------------------------------------------------------------------
# 工作线程类
# ---------------------------------------------------------------------------
class DeviceInfosWorker(QThread):
    """设备信息扫描线程：获取端口 + 设备信息"""
    finished_with_device_infos = pyqtSignal(list)

    def run(self):
        print(f'run')


class ExecuteScriptWorker(QThread):
    """测试脚本执行线程"""
    finished_with_script_result = pyqtSignal(str, list)

    def __init__(self, ports: list, device_ids: list, aging_duration: float, script_path: str, parent=None):
        super().__init__(parent)
        # self.ports = ports
        # self.device_ids = device_ids
        # self.aging_duration = aging_duration
        self.script_path = script_path
        self._is_stopped = False

    def run(self):
        print(f'run')
        # try:
        #     if self._is_stopped:
        #         self.finished_with_script_result.emit("任务已停止", [])
        #         return
        #
        #     if not os.path.exists(self.script_path):
        #         self.finished_with_script_result.emit("脚本不存在", [])
        #         return
        #
        #     script_dir = os.path.dirname(self.script_path)
        #     if script_dir not in sys.path:
        #         sys.path.append(script_dir)
        #
        #     script_name = os.path.splitext(os.path.basename(self.script_path))[0]
        #     module = __import__(script_name)
        #
        #     report_title, overall_result = module.main(
        #         ports=self.ports,
        #         devices_ids=self.device_ids,
        #         aging_duration=self.aging_duration
        #     )
        #
        #     if self._is_stopped:
        #         self.finished_with_script_result.emit("任务已停止", [])
        #         return
        #
        #     self.finished_with_script_result.emit(report_title, overall_result)
        #
        # except Exception as e:
        #     print(f'ExecuteScriptWorker发生异常{str(e)}')
        #     if self._is_stopped:
        #         self.finished_with_script_result.emit("任务已停止", [])
        #     else:
        #         self.finished_with_script_result.emit(f"执行异常：{str(e)}", [])

    def stop_task(self):
        self._is_stopped = True


class ProgressBarWorker(QThread):
    """进度条计时线程"""
    progress_update = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, duration, parent=None):
        super().__init__(parent)
        self.total_test_seconds = max(duration, 1)
        self.is_running = True
        self.is_paused = False
        self.delay = 0.0

    def run(self):
        start_time = time.time()
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                self.delay += 0.1
                continue

            elapsed = time.time() - start_time - self.delay
            progress = int((elapsed / self.total_test_seconds) * 100)
            progress = max(0, min(100, progress))

            self.progress_update.emit(progress)
            if progress >= 100:
                break

            time.sleep(0.5)

        self.progress_update.emit(100)
        self.finished_signal.emit()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_running = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = APPTestWindow()
    win.setWindowTitle("应用自动化测试界面")
    win.show()
    sys.exit(app.exec_())