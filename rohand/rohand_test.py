#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, PatternFill, Side
from openpyxl.styles.fonts import Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import RowDimension

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QCheckBox,
    QDialog, QLabel, QProgressBar, QPushButton, QHBoxLayout
)

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QPoint

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.uic import loadUi

from rohand.rohand_logger import RoHandLogger
from rohand.rohand_manager import RohanManager
from theme_qss import cache_default_qss, apply_black_qss, apply_green_qss, apply_default_qss


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

class RoHandTestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ===== 全局变量 =====
        self.protocol_type = 0
        self.select_port_names = []
        self.port_names = ['无可用端口']
        self.selected_aging_hours = 0.001
        self.unit_duration = 6.16
        self.test_data_table = None
        self.check_box_list = []
        self.script_loaded = False
        self.script_path = None
        self.protocol_type = None
        self.rohand_manager = None
        self.roHandLogger = None
        self.client = None
        self.total_test_seconds = 0
        self.device_info_list = []
        self.script_name = None
        self.report_title = None
        self.raw_test_data = None

        # 加载UI xml文件
        base = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base, "rohand_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(base, "ui", "rohand_test.ui")
        loadUi(ui_path, self)

        # 设置窗口属性
        flags = self.windowFlags()
        flags &= ~Qt.WindowMaximizeButtonHint
        flags |= Qt.WindowSystemMenuHint | Qt.WindowTitleHint
        self.setWindowFlags(flags)

        #初始化组件并绑定响应函数
        self._init_ui_widgets()
        self._bind_all_events()

        self._init_manager()

    # ------------------------------------------------------------------
    # UI 组件初始化
    # ------------------------------------------------------------------
    def setMenuItemStyle(self, menu: QMenu):
        menu.setStyleSheet("""
            # QMenu {
            #     width: 250px;            /* 菜单整体宽度 */
            # }
            QMenu::item {
                height: 20px;            /* 子项高度（建议不要太小，15px会挤）*/
                width: 200px;            /* 子项宽度 */
                margin: 0px 0px;         /* 子项上下间隔 */
                font-size: 16px;         /* ✅ 字体大小（你要的） */
            }
        """)

    def _init_ui_widgets(self):
        self.setMenuItemStyle(self.menu_file)
        self.setMenuItemStyle(self.menu_config)
        self.setMenuItemStyle(self.menu_theme)
        self.setMenuItemStyle(self.menu_help)
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 10))

        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.test_data_table.setRowCount(0)
        self.test_data_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.aging_time_combo.clear()
        self.aging_time_combo.addItems(DEFAULT_AGING_OPTIONS)

        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)

        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")

        self.status_bar.showMessage(MSG_REFRESH_PORT)

    # ------------------------------------------------------------------
    # 组件事件绑定
    # ------------------------------------------------------------------
    def _bind_all_events(self):
        self.aging_time_combo.currentTextChanged.connect(self.on_aging_time_selected)
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.refresh_btn.clicked.connect(self.start_port_refresh)
        self.select_all_check.stateChanged.connect(self.on_select_all)
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)
        self.log_level_btn.clicked.connect(self.on_log_level_clicked)
        # self.select_all_check.clicked.connect(
        #     lambda checked: self.on_port_cbx_checked(checked, self.select_all_check)
        # )

        #文件菜单
        self.action_loadScript.triggered.connect(self.on_load_script)
        self.action_exportReport.triggered.connect(self.on_export_report)
        self.action_exit.triggered.connect(self.close)

        # 配置文件
        self.action_viewConfigFile.triggered.connect(self.on_view_config)
        self.action_editConfigFile.triggered.connect(self.on_edit_config)

        # 主题
        self.action_blackTheme.triggered.connect(self.on_theme_black)
        self.action_greenTheme.triggered.connect(self.on_theme_green)
        self.action_defaultTheme.triggered.connect(self.on_theme_default)

        # 帮助
        self.action_about.triggered.connect(self.on_about)

    # ------------------------------------------------------------------
    # 初始化外部各种公共接口管理器
    # ------------------------------------------------------------------
    def _init_manager(self):
        print(f'_init_manager')
        self.rologger = RoHandLogger(self.log_text_edit)
        self.protocol_type = RohanManager.read_config_value(section="protocol_type", key="protocol", default=0)
        self.rohand_manager = RohanManager(self.protocol_type)

        #延迟初始化
        # self.client = self.rohand_manager.get_instance().create_client()

    # ------------------------------------------------------------------
    # 控件响应函数
    # ------------------------------------------------------------------
    def on_aging_time_selected(self, text):
        try:
            hour_value = float(text.replace("小时", ""))
            self.rologger.log(f"已选择老化时间：{text} → 提取数字：{hour_value} 小时")
            self.selected_aging_hours = hour_value
        except Exception as e:
            self.rologger.log(f"选择时间异常：{e}")

    def on_copy_log(self):
        self.rologger.log('on_copy_log')
        self.log_text_edit.selectAll()
        self.log_text_edit.copy()

    def on_clear_log(self):
        self.rologger.log('on_clear_log')
        self.log_text_edit.clear()

    def on_save_log(self):
        self.rologger.log("开始保存日志文件")
        # 弹出保存对话框
        fn, _ = QFileDialog.getSaveFileName(
            self, "保存日志",
            f"灵巧手测试日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt)"
        )

        # 如果用户选择了路径
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
        button_pos = self.log_level_btn.mapToGlobal(QPoint(0, self.log_level_btn.height()))
        menu.exec_(button_pos)

    def on_log_level_selected(self, level):
        try:
            self.rologger.set_log_level(level)
            self.rologger.log(f"日志级别已设置为：{level}")
        except Exception as e:
            self.rologger.log(f"设置日志级别失败：{str(e)}")

    def remove_all_widgets_from_layout(self, layout):
        """清空并删除布局内的所有控件和子布局"""
        if layout is None:
            return

        # 循环取出布局里的所有项
        while layout.count() > 0:
            item = layout.takeAt(0)

            # 如果是控件，删除
            if item.widget():
                item.widget().deleteLater()

            # 如果是子布局，递归清空
            elif item.layout():
                self.remove_all_widgets_from_layout(item.layout())

    def update_port_info(self):
        self.rologger.log('update_port_info')
        max_per_col, max_col = 8, 4
        vertical_layouts = []

        # ===================== 关键修复 =====================
        # 1. 获取布局并清空所有旧控件（必须放在最前面）
        port_layout = self.scroll_content_widget.layout()
        self.remove_all_widgets_from_layout(port_layout)  # 清空旧端口
        # ====================================================
        self.select_port_names.clear()
        self.check_box_list.clear()

        # 重新添加新端口复选框
        for idx, port in enumerate(self.port_names):
            cbx = QCheckBox(port)
            cbx.setObjectName("port_checkbox")
            self.check_box_list.append(cbx)

            col = idx // max_per_col
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

    def on_port_cbx_clicked(self, checked, checkbox):
        self.rologger.log('on_port_cbx_clicked')
        try:
            port = checkbox.text()
            # self.select_port_names = self.port_names.copy() if checked else []
            if checked and port not in self.select_port_names:
                self.select_port_names.append(port)
            elif not checked and port in self.select_port_names:
                self.select_port_names.remove(port)
            self.update_test_datas_table([port], checked)
            self.rologger.log(f"端口 {port} {'选中' if checked else '取消选中'}，已选：{self.select_port_names}")
        except Exception as e:
            self.rologger.log(f"复选框操作失败：{str(e)}")

    # def update_test_data_table(self, port, checked):
    #     self.rologger.log('update_test_data_table')
    #     self.deviceInfoWorker = DeviceInfoWorker(port)
    #     self.deviceInfoWorker.result_ready.connect(
    #         lambda device_info: self._on_device_info_update(device_info, checked)
    #     )
    #     self.deviceInfoWorker.finished.connect(self.deviceInfoWorker.deleteLater)
    #     self.deviceInfoWorker.start()

    def update_test_datas_table(self, ports, checked):
        self.rologger.log('update_test_datas_table')
        self.deviceInfoWorker = DeviceInfoWorker(ports)
        self.deviceInfoWorker.result_ready.connect(
            lambda device_info_list: self._on_device_info_update(device_info_list, checked)
        )
        self.deviceInfoWorker.finished.connect(self.deviceInfoWorker.deleteLater)
        self.deviceInfoWorker.start()


    def get_row_by_port(self, port):
        """根据端口查找表格行号"""
        for row in range(self.test_data_table.rowCount()):
            item = self.test_data_table.item(row, 0)
            if item and item.text() == port:
                return row
        return -1

    def _update_local_device_list(self, device_info_list,checked):
        self.rologger.log('_update_local_device_list')
        if not device_info_list:
            return

        try:
            if checked:
                # ---------------
                # 新增：追加进去（不重复）
                # ---------------
                for new_dev in device_info_list:
                    port = new_dev.get(COL_PORT)
                    # 已存在就跳过，不重复添加
                    exist = any(d.get(COL_PORT) == port for d in self.device_info_list)
                    if not exist:
                        self.device_info_list.append(new_dev)
                        self.rologger.log(f"新增设备: {port}")
            else:
                # ---------------
                # 移除：删除对应端口
                # ---------------
                for del_dev in device_info_list:
                    port = del_dev.get(COL_PORT)
                    # 过滤掉要删除的
                    self.device_info_list = [
                        d for d in self.device_info_list
                        if d.get(COL_PORT) != port
                    ]
                    self.rologger.log(f"移除设备: {port}")

            self.rologger.log(f"更新后本地设备列表: {self.device_info_list}")

        except Exception as e:
            self.rologger.log(f"更新设备列表异常: {str(e)}")
            return

    def _on_device_info_update(self, device_info_list, checked):
        self.rologger.log('_on_device_info_update')
        self.rologger.log(f'设备信息列表: {device_info_list}')
        self.rologger.log(f'勾选状态: {checked}')
        if  not device_info_list:
            return

        # self.device_info_list.clear()
        self._update_local_device_list(device_info_list, checked)

        # 遍历所有设备信息（批量处理）
        for device_info in device_info_list:
            port = device_info.get(COL_PORT)
            if not port:
                continue

            # ==============================================
            # 根据 checked 状态：勾选=添加/更新，取消=删除行
            # ==============================================
            if checked:
                row = self.get_row_by_port(port)
                if row < 0:
                    self.rologger.log(f'端口 {port} 不存在 → 新增行')
                    row = self.test_data_table.rowCount()
                    self.test_data_table.insertRow(row)

                # 填充真实数据
                self.test_data_table.setItem(row, 0, QTableWidgetItem(port))
                self.test_data_table.setItem(row, 1, QTableWidgetItem(device_info.get(COL_SOFTWARE_VERSION, "")))
                self.test_data_table.setItem(row, 2, QTableWidgetItem(str(device_info.get(COL_DEVICE_ID, ""))))
                self.test_data_table.setItem(row, 3, QTableWidgetItem(device_info.get(COL_CONNECT_STATUS, "")))
                self.test_data_table.setItem(row, 4, QTableWidgetItem(device_info.get(COL_TEST_RESULT, "待测试")))

            else:
                self.rologger.log(f'删除端口 {port} 所在行')
                row = self.get_row_by_port(port)
                if row >= 0:
                    self.test_data_table.removeRow(row)
                    self.rologger.log(f"已删除端口 {port} 的表格行")

    def update_table_column_by_port(self, port, column_index, value):
        row = self.get_row_by_port(port)
        if row >= 0:
            # 更新指定单元格
            self.test_data_table.setItem(row, column_index, QTableWidgetItem(str(value)))
            self.rologger.log(f"更新表格 → 端口 {port} 第 {column_index} 列为：{value}")
        else:
            self.rologger.log(f"更新失败：端口 {port} 不存在于表格中")

    def _on_port_refresh_finished(self,ports,err):
        self.rologger.log(f'_on_port_refresh_finished, ports = {ports},err = {err}')
        self.port_names = ports
        if self.port_names and self.port_names[0] != "无可用端口":
            self.status_bar.showMessage("端口刷新完成")
            self.update_port_info()
        else:
            self.status_bar.showMessage("无可用端口")
        self.set_controls_enabled(True)

    def set_controls_enabled(self, enabled):
        controls = [
            self.refresh_btn,
            self.aging_time_combo,
            self.select_all_check,
            self.start_test_btn,
            self.pause_test_btn,
            self.stop_test_btn
        ]
        for control in controls:
            control.setEnabled(enabled)

    def start_port_refresh(self):
        self.rologger.log(f'start_port_refresh')
        self.set_controls_enabled(False)
        self.port_names.clear()
        self.port_refresh_worker  = PortRefreshWorker()
        self.port_refresh_worker.finished_with_ports.connect(self._on_port_refresh_finished)
        self.port_refresh_worker.start()
        self.status_bar.showMessage(f"端口刷新中，请耐心等待...")

    def on_select_all(self, state):
        self.rologger.log(f'on_select_all')
        checked = (state == 2)
        if self.port_names[0] != '无可用端口':
            self.select_port_names = self.port_names.copy() if checked else []
            for cbx in self.check_box_list:
                if cbx.text() == LABEL_SELECT_ALL:
                    continue
                cbx.blockSignals(True)
                cbx.setChecked(checked)
                cbx.blockSignals(False)
            if checked:
                self.select_port_names = self.port_names.copy()
            else:
                self.select_port_names = []
            self.update_test_datas_table(self.port_names, checked)

    def get_device_ids(self, device_info_list):
        device_ids = []
        if not device_info_list:
            return device_ids

        for info in device_info_list:
            dev_id = info.get(COL_DEVICE_ID)
            if dev_id is not None and dev_id != "":
                # 严格按列表顺序添加
                device_ids.append(int(dev_id))

        return device_ids

    def get_offset_duration(self):
        self.rologger.log(f'get_offset_duration')
        value = float(RohanManager.read_config_value(
            section="aging_parameter",
            key="unit_duration",
            default=0
        ))
        self.unit_duration = float(str(value).strip())

        if  self.unit_duration <= 0:
            return 0.0

        # 计算总周期数
        total_seconds = float(self.selected_aging_hours) * 3600
        total_cycles = total_seconds /  self.unit_duration

        # 计算补时时长（补齐到整数周期）
        decimal_part = total_cycles - int(total_cycles)
        offset_seconds = round((1 - decimal_part) * self.unit_duration, 2)
        self.rologger.log(f'offset_seconds = {offset_seconds}')

        return offset_seconds

    def on_start_test(self):
        self.rologger.log('on_start_test')
        self.rologger.log(f"script_name = {self.script_name}")
        if not self.select_port_names:
            self.status_bar.showMessage(f"请选择要测试的端口")
            return
        if not self.script_name:
            self.status_bar.showMessage(f"请选择测试脚本")
            return

        # 1. 读取老化时间
        self.total_test_seconds = self.selected_aging_hours * 3600 + self.get_offset_duration()

        # 2. 启动脚本执行线程
        self.selected_device_ids  = self.get_device_ids(self.device_info_list)
        self.executeScriptWorker = ExecuteScriptWorker(self.select_port_names, self.selected_device_ids, self.selected_aging_hours, self.script_name)
        self.executeScriptWorker.finished_with_script_result.connect(self._on_script_finished_result)
        self.executeScriptWorker.start()

        # 3. 进度条初始化
        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)
        self.test_progress_bar.setStyleSheet("QProgressBar { color: #000000; font-weight: bold; }")

        # 4. 创建并启动进度条线程
        self.progressbar_worker = ProgressBarWorker(duration=self.total_test_seconds)
        self.progressbar_worker.progress_update.connect(self._on_progress_result)
        self.progressbar_worker.finished_signal.connect(self.on_test_finished_auto)
        self.progressbar_worker.start()  # <--- 这里必须是 start()

        self.status_bar.showMessage("开始测试...")

    def _on_progress_result(self, value):
        """更新UI进度条"""
        self.test_progress_bar.setValue(value)

    def on_test_finished_auto(self):
        self.status_bar.showMessage("测试已完成")
        self.rologger.log("老化测试时间到，自动结束")

    def _on_script_finished_result(self, titles, result):
        self.rologger.log(f'_on_script_finished_result')
        self.rologger.log(f'titles = {titles},result = {result}')
        self.report_title = titles
        self.raw_test_data = result
        # 1. 解析所有数据
        port_data_dict = self.parse_test_result(result)

        # 2. 遍历每个端口 → 判断最终结果 → 只更新一行
        for port, table_rows in port_data_dict.items():
            # 默认：全部通过
            final_result = "通过"

            # 轮询查找：只要有一条不通过，整体就是不通过
            for row_data in table_rows:
                test_result = row_data[2] #当前返回数据第三个数据为测试结果
                if test_result != "通过":
                    final_result = "不通过"
                    break  # 找到就立刻退出，不用继续查

            # 3. 只更新【该端口对应的那一行】，行号固定 0
            self.update_table_column_by_port(port, 4, final_result)

            # 日志
            self.rologger.log(f"端口 {port} 最终测试结果：{final_result}")

        self._update_test_result(self.raw_test_data)

    def _update_test_result(self, raw_test_data):
        self.rologger.log(f'_update_test_result')

        # 1. 先把原始数据转成你熟悉的 port_data_dict 结构（不去重）
        port_data_dict = {}
        for item in raw_test_data:
            port = item['port']
            if port not in port_data_dict:
                port_data_dict[port] = []
            for gesture in item['gestures']:
                # 组装成 row_data 结构：timestamp, content, result, comment
                row_data = (
                    gesture['timestamp'],
                    gesture['content'],
                    gesture['result'],
                    gesture['comment']
                )
                port_data_dict[port].append(row_data)

        # 2. 统计总数、成功数、失败数（完全按你的遍历方式）
        total_count = 0
        success_count = 0
        failed_count = 0

        # 3. 遍历每个端口 → 判断最终结果
        for port, table_rows in port_data_dict.items():
            # 默认：全部通过
            final_result = "通过"

            # 轮询查找：只要有一条不通过，整体就是不通过
            for row_data in table_rows:
                test_result = row_data[2]  # 当前返回数据第三个数据为测试结果
                total_count += 1
                if test_result == "通过":
                    success_count += 1
                else:
                    failed_count += 1
                    final_result = "不通过"
                    # 找到就立刻退出，不用继续查

        # 4. 赋值给界面变量
        self.rologger.log(f'total_count={total_count},success_count={success_count},failed_count={failed_count}')
        self.total_case_value.setText(str(total_count))
        self.success_case_value.setText(str(success_count))
        self.fail_case_value.setText(str(failed_count))
        # 5. 最终测试状态
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
        self.rologger.log('开始解析测试结果数据，用于表格刷新')

        # 最终返回的按端口分组的字典
        port_data_dict = {}

        # 遍历原始测试结果的每一项（修正变量名：result = 原 overall_result）
        for item in result:
            port = item['port']
            # 如果端口不在字典中，初始化空列表
            if port not in port_data_dict:
                port_data_dict[port] = []
            # 遍历当前端口下的所有手势/测试项
            for gesture in item['gestures']:
                # 组装表格需要的元组数据
                table_row = (
                    gesture['timestamp'],  # 时间戳
                    gesture['content'],  # 内容
                    gesture['result'],  # 测试结果
                    gesture['comment']  # 备注
                )
                port_data_dict[port].append(table_row)
        # 打印日志，方便调试
        self.rologger.log(f'测试结果解析完成，共解析到端口：{list(port_data_dict.keys())}')
        return port_data_dict

    def on_pause_test(self):
        self.rologger.log(f'on_pause_test')

    def on_stop_test(self):
        self.rologger.log(f'on_stop_test')

    def on_load_script(self):
        self.rologger.log(f'on_load_script')
        # 弹出文件选择对话框，默认打开 scripts 文件夹
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择要执行的脚本',
            'scripts',
            'Python files (*.py)'
        )
        if file_path:
            # 获取文件名（包含扩展名）
            file_name = os.path.basename(file_path)
            # 获取 scripts 目录绝对路径，并自动创建（防止目录不存在）
            scripts_dir = os.path.abspath('scripts')
            if not os.path.exists(scripts_dir):
                os.makedirs(scripts_dir)
            # 拼接最终脚本路径
            self.script_name = os.path.join(scripts_dir, file_name)
            # # 读取文件内容（你原来的代码只打开没读取，我帮你补上）
            # with open(file_path, 'r', encoding='utf-8') as f:
            #     self.script_content = f.read()
            self.rologger.log(f'成功加载脚本：{self.script_name}')
            self.rologger.log(f'请点击【开始测试】按钮执行脚本\n')

    def on_export_report(self):
        self.rologger.log(f'on_export_report')
        if self.raw_test_data is None or len(self.raw_test_data) == 0:
            self.rologger.log("导出失败：无测试数据")
            self.status_bar.showMessage(f"尚未进行测试，无数据可导出")
            return

        if self.report_title is None or self.report_title.strip() == "":
            self.rologger.log("导出失败：报告标题为空")
            self.status_bar.showMessage(f"请设置报告标题")
            return
        headers = ["用例编号", "时间戳", "内容", "测试结果", "备注", "端口号"]
        column_widths = [10, 25, 35, 12, 15, 18]
        default_row_height = 35

        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                             top=Side(style='thin'), bottom=Side(style='thin'))
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

        # 基础信息
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

        # ===================== 【唯一核心】安全写入数据 =====================
        row_index = 7
        for item in raw_result:
            try:
                port = item["port"]
                gestures = item["gestures"]

                for g in gestures:
                    # 🔥 最安全的取值方式，绝不闪退
                    ts = g.get("timestamp", "")
                    content = str(g.get("content", ""))  # 转字符串 = 防崩关键
                    res = g.get("result", "")
                    comment = g.get("comment", "")

                    ws.append([
                        row_index - 6,
                        ts,
                        content,
                        res,
                        comment,
                        port
                    ])
                    row_index += 1

            except Exception as e:
                self.rologger.log(f"数据处理异常: {e}")

        # ===================== 收尾 =====================
        for i, w in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = alignment
                cell.border = thin_border

        # 保存
        os.makedirs("report", exist_ok=True)
        name = os.path.splitext(os.path.basename(self.script_name))[0]
        filename = f"{name}_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = os.path.join("report", filename)

        wb.save(filepath)
        QMessageBox.information(self, "成功", f"报告已保存：\n{filepath}")

    # def on_export_report(self):
    #     self.rologger.log(f'on_export_report')

    def on_view_config(self):
        self.rologger.log(f'on_view_config')

    def on_edit_config(self):
        self.rologger.log(f'on_edit_config')

    def on_theme_black(self):
        self.rologger.log("on_theme_black")
        apply_black_qss(self)

    def on_theme_green(self):
        self.rologger.log("on_theme_green")
        apply_green_qss(self)

    def on_theme_default(self):
        self.rologger.log(f"on_theme_default")
        apply_default_qss(self)

    def on_about(self):
        self.rologger.log(f"on_about")
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0\n基于PyQt5开发")

# 定义端口刷新任务线程
class PortRefreshWorker(QThread):
    finished_with_ports = pyqtSignal(list, str)  # ports, error_message
    def __init__(self, parent=None):
        super().__init__(parent)
    def run(self):
        try:
            protocol_type = RohanManager.read_config_value(section="protocol_type", key="protocol", default=0)
            ports = RohanManager(protocol_type).read_port_info()
            self.finished_with_ports.emit(ports, "")
        except Exception as e:
            self.finished_with_ports.emit([], str(e))

# 定义设备信息获取任务线程
class DeviceInfoWorker(QThread):
     result_ready = pyqtSignal(list)

     def __init__(self, ports, parent=None):
         super().__init__(parent)
         self.ports = ports

     def run(self):
         try:
             DEFAULT_TEST_RESULT = 0
             protocol_type = RohanManager.read_config_value(section="protocol_type", key="protocol", default=0)
             device_infos = RohanManager(protocol_type).get_device_info_list(self.ports)
             self.result_ready.emit(device_infos)
         except Exception as e:
             self.result_ready.emit(str(e))

# 定义执行测试脚本任务线程，执行完成后，脚本会返回测试结果
class ExecuteScriptWorker(QThread):
    # 修正信号：用例描述、结果列表、执行标记（True=成功 False=失败）
    finished_with_script_result = pyqtSignal(str, list)  # 3个参数

    def __init__(self, ports: list, device_ids: list,aging_duration: float, script_path: str, parent=None):
        super().__init__(parent)
        self.ports = ports
        self.device_ids = device_ids
        self.aging_duration = aging_duration
        self.script_path = script_path
        print(f'script_path = {self.script_path}')

    def run(self):
        try:
            # 1. 检查脚本
            if not os.path.exists(self.script_path):
                self.finished_with_script_result.emit("脚本不存在", [])
                return

            if not self.ports:
                return

            # 2. 获取脚本目录，加入环境变量（能 import）
            script_dir = os.path.dirname(self.script_path)
            if script_dir not in sys.path:
                sys.path.append(script_dir)

            # 3. 获取脚本模块名（自动识别）
            script_name = os.path.splitext(os.path.basename(self.script_path))[0]

            # 4. 动态导入脚本
            module = __import__(script_name)

            # 5. 【核心】像你原来一样调用 main 函数
            report_title, overall_result = module.main(
                ports=self.ports,
                devices_ids=self.device_ids,
                aging_duration=self.aging_duration
            )

            # 6. 发射结果（完全匹配你的返回值）
            self.finished_with_script_result.emit(report_title, overall_result)

        except Exception as e:
            self.finished_with_script_result.emit(f"执行异常：{str(e)}", [])


class ProgressBarWorker(QThread):
    progress_update = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, duration, parent=None):
        super().__init__(parent)
        self.total_test_seconds = max(duration, 1)
        self.is_running = True
        self.is_paused = False

    def run(self):
        start_time = time.time()
        while self.is_running:
            if self.is_paused:
                time.sleep(0.1)
                continue

            elapsed = time.time() - start_time

            progress = int((elapsed / self.total_test_seconds) * 100)
            progress = max(0, min(100, progress))  # 限定 0~100

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
    win = RoHandTestWindow()
    win.setWindowTitle("灵巧手自动化测试界面")
    win.show()
    sys.exit(app.exec_())