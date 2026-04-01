#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    QDialog, QLabel,QStyledItemDelegate,QTextEdit, QDialogButtonBox
)

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QPoint

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi

from rohand.rohand_logger import RoHandLogger
from rohand.rohand_manager import RohanManager

from rohand_theme import apply_black_style, apply_green_style, apply_default_style


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

from rohand_common import OperateSharedData

class RoHandTestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ===== 全局变量 =====
        self.is_refresh_port = False
        self.protocol_type = 0
        self.port_names_all = ['无可用端口'] # 获取的所有接测试设备的端口列表
        self.device_info_all = []  # 存在从端口获取的所有设备信息
        self.port_names_selected = [] # 被选中测定端口列表
        self.selected_device_ids = []
        self.device_infos_test = []  # 和表格里面设备信息列表一致
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

        self.script_name = None
        self.report_title = None
        self.raw_test_data = None
        self.stop_test = False
        self.pause_test = False
        self.executeScriptWorker = None
        # self.port_refresh_worker = None
        self.deviceInfosWorker = None
        self.progressbar_worker = None

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
        OperateSharedData.write(False,False)
        self.closeEvent = self.close_event_handler

    def close_event_handler(self, event):
        OperateSharedData.delete_shared_data_file()
        event.accept()

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
    # 表格内容居中，解决qproperty-alignment: AlignCenter 在部分 PyQt5 版本里就是不生效的bug
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

        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.test_data_table.setRowCount(0)
        self.test_data_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.test_data_table.setItemDelegate(self.CenterAlignDelegate())

        self.aging_time_combo.clear()
        self.aging_time_combo.addItems(DEFAULT_AGING_OPTIONS)

        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)
        self.test_progress_bar.setStyleSheet("QProgressBar { color: #000000; font-weight: bold; }")


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
        self.protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
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
        # self.select_port_names.clear()
        self.check_box_list.clear()


        # 重新添加新端口复选框
        for idx, port in enumerate(self.port_names_all):
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
            if checked and port not in self.port_names_selected:
                self.port_names_selected.append(port)
            elif not checked and port in self.port_names_selected:
                self.port_names_selected.remove(port)
            self.update_test_datas_table()
            self.rologger.log(f"端口 {port} {'选中' if checked else '取消选中'}，已选：{self.port_names_selected}")
        except Exception as e:
            self.rologger.log(f"复选框操作失败：{str(e)}")

    # ----------------------
    # 更新表格（先清空 + 正确筛选）
    # ----------------------
    def update_test_datas_table(self):
        self.rologger.log('update_test_datas_table')

        # 清空
        self.device_infos_test.clear()
        self.test_data_table.setRowCount(0)

        if not self.port_names_selected or not self.device_info_all:
            return

        # 根据选中端口筛选设备
        for port in self.port_names_selected:
            for dev in self.device_info_all:
                if dev.get(COL_PORT) == port:
                    self.device_infos_test.append(dev)
                    break

        # 渲染表格
        self._on_device_info_update(self.device_infos_test)


    def get_row_by_port(self, port):
        """根据端口查找表格行号"""
        for row in range(self.test_data_table.rowCount()):
            item = self.test_data_table.item(row, 0)
            if item and item.text() == port:
                return row
        return -1

    def _on_device_info_update(self, device_info_test):
        self.rologger.log('_on_device_info_update')

        # ===================== 绘制前 先清空表格 =====================
        self.test_data_table.setRowCount(0)
        # self.device_info_list.clear()  # 同时清空本地缓存列表
        # ===========================================================

        if not device_info_test:
            self.rologger.log("无设备信息需要展示")
            return

        # 遍历所有设备信息，完整重新绘制列表
        for device_info in device_info_test:
            port = device_info.get(COL_PORT)
            if not port:
                continue

            # 新增行
            row = self.test_data_table.rowCount()
            self.test_data_table.insertRow(row)

            # 填充数据
            self.test_data_table.setItem(row, 0, QTableWidgetItem(port))
            self.test_data_table.setItem(row, 1, QTableWidgetItem(device_info.get(COL_SOFTWARE_VERSION, "")))
            self.test_data_table.setItem(row, 2, QTableWidgetItem(str(device_info.get(COL_DEVICE_ID, ""))))
            self.test_data_table.setItem(row, 3, QTableWidgetItem(device_info.get(COL_CONNECT_STATUS, "")))
            self.test_data_table.setItem(row, 4, QTableWidgetItem(device_info.get(COL_TEST_RESULT, "待测试")))

            # 添加到本地设备列表
            # self.device_info_list.append(device_info)
            self.rologger.log(f'已添加设备到表格：{port}')

    def update_table_column_by_port(self, port, column_index, value):
        row = self.get_row_by_port(port)
        if row >= 0:
            # 更新指定单元格
            self.test_data_table.setItem(row, column_index, QTableWidgetItem(str(value)))
            self.rologger.log(f"更新表格 → 端口 {port} 第 {column_index} 列为：{value}")
        else:
            self.rologger.log(f"更新失败：端口 {port} 不存在于表格中")

    # ----------------------
    # 1. 刷新端口完成后（修复端口字段 + 清空）
    # ----------------------
    def _on_port_refresh_finished(self, device_infos):
        self.rologger.log(f'_on_port_refresh_finished, device_infos = {device_infos}')

        # 清空所有旧数据
        self.port_names_all.clear()
        self.port_names_selected.clear()
        self.device_info_all.clear()
        self.device_infos_test.clear()
        self.test_data_table.setRowCount(0)

        # 从设备信息提取端口（用你常量 COL_PORT）
        if device_infos:
            self.port_names_all = [dev.get(COL_PORT, "") for dev in device_infos if dev.get(COL_PORT)]
        else:
            self.port_names_all = ["无可用端口"]

        self.device_info_all = device_infos
        self.rologger.log(f'端口列表：{self.port_names_all}')

        if self.port_names_all and self.port_names_all[0] != "无可用端口":
            self.status_bar.showMessage("端口刷新完成")
            self.update_port_info()
        else:
            self.status_bar.showMessage("无可用端口")
        self.set_controls_enabled(True)
        self.is_refresh_port = False

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
        if self.is_refresh_port:
            return
        self.is_refresh_port = True
        self.set_controls_enabled(False)
        # 清空旧数据
        self.port_names_all.clear()
        self.port_names_selected.clear()
        self.device_info_all.clear()
        self.device_infos_test.clear()
        self.test_data_table.setRowCount(0)

        self.deviceInfosWorker  = DeviceInfosWorker()
        self.deviceInfosWorker.finished_with_device_infos.connect(self._on_port_refresh_finished)
        self.deviceInfosWorker.start()
        self.status_bar.showMessage(f"端口刷新中，请耐心等待...")

    # ----------------------
    # 全选/取消全选（修复变量名错误）
    # ----------------------
    def on_select_all(self, state):
        self.rologger.log(f'on_select_all')
        checked = (state == 2)
        if self.port_names_all[0] == '无可用端口':
            return

        # 清空表格
        if not checked:
            self.test_data_table.setRowCount(0)
            self.port_names_selected.clear()

        # 勾选/取消所有复选框
        for cbx in self.check_box_list:
            cbx.blockSignals(True)
            cbx.setChecked(checked)
            cbx.blockSignals(False)

        # 赋值选中列表
        if checked:
            self.port_names_selected = self.port_names_all.copy()
        else:
            self.port_names_selected.clear()

        # 更新表格
        self.update_test_datas_table()

    def get_device_ids(self, device_infos_test):
        device_ids = []
        if not device_infos_test:
            return device_ids

        for info in device_infos_test:
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

    # ----------------------
    # 开始测试
    # ----------------------
    def on_start_test(self):
        self.rologger.log('on_start_test')
        self.rologger.log(f"script_name = {self.script_name}")

        # 修复：用正确的选中端口
        if not self.port_names_selected:
            self.status_bar.showMessage(f"请选择要测试的端口")
            return

        if not self.script_name:
            self.status_bar.showMessage(f"请选择测试脚本")
            return

        if self.executeScriptWorker is not None and self.executeScriptWorker.isRunning():
            return

        self.pause_test = False
        self.stop_test = False
        OperateSharedData.write(False, False)

        # 1. 读取老化时间
        self.total_test_seconds = self.selected_aging_hours * 3600 + self.get_offset_duration()

        # 2. 启动脚本执行线程（修复：device_infos_test）
        self.selected_device_ids = self.get_device_ids(self.device_infos_test)

        self.executeScriptWorker = ExecuteScriptWorker(
            self.port_names_selected,
            self.selected_device_ids,
            self.selected_aging_hours,
            self.script_name
        )
        self.executeScriptWorker.finished_with_script_result.connect(self._on_script_finished_result)
        self.executeScriptWorker.start()

        # 3. 进度条
        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)

        self.progressbar_worker = ProgressBarWorker(duration=self.total_test_seconds)
        self.progressbar_worker.progress_update.connect(self._on_progress_result)
        self.progressbar_worker.finished_signal.connect(self.on_test_finished_auto)
        self.progressbar_worker.start()

        self.status_bar.showMessage("开始测试...")

    def _on_progress_result(self, value):
        """更新UI进度条"""
        self.test_progress_bar.setValue(value)

    def on_test_finished_auto(self):
        # OperateSharedData.write(False, False)
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
        """暂停/恢复测试"""
        self.rologger.log('on_pause_test')

        # 先判断：没有运行中的任务 → 直接返回
        if not hasattr(self, 'executeScriptWorker') or not self.executeScriptWorker.isRunning():
            self.status_bar.showMessage('当前没有在执行的任务')
            return

        # 已停止 → 不能暂停
        if self.stop_test:
            self.status_bar.showMessage('当前无测试脚本在运行')
            return

        # 核心：切换暂停状态 ← 你原本的逻辑
        self.pause_test = not self.pause_test
        OperateSharedData.write(stop_test=False, pause_test=self.pause_test)

        # 状态提示和按钮文本切换
        if self.pause_test:
            # 暂停测试
            self.progressbar_worker.pause()
            self.pause_test_btn.setText("继续测试")
            self.status_bar.showMessage('当前任务已暂停，点击继续执行')
            self.rologger.log("测试已暂停")
        else:
            # 恢复测试
            self.progressbar_worker.resume()
            self.pause_test_btn.setText("暂停测试")
            self.status_bar.showMessage('当前任务已恢复执行')
            self.rologger.log("测试已恢复")

    def on_stop_test(self):
        self.rologger.log(f'on_stop_test')

        # 没有运行中的任务
        if not hasattr(self, 'executeScriptWorker') or not self.executeScriptWorker.isRunning():
            self.status_bar.showMessage('当前没有在执行的任务')
            return

        # 1. 设置状态
        self.stop_test = True
        self.pause_test = True
        OperateSharedData.write(stop_test=True, pause_test=True)

        self.status_bar.showMessage("正在停止任务...")
        self.progressbar_worker.stop()

        # 2. 线程结束后自动回调（不阻塞、不闪退）
        def _on_task_finished(title, result):
            self.on_test_finished_auto()
            self.status_bar.showMessage("当前任务已停止")
            self.stop_test = False
            self.pause_test = False
            # 用完断开信号，避免重复触发
            self.executeScriptWorker.finished_with_script_result.disconnect(_on_task_finished)

        # 3. 绑定信号 + 触发停止
        self.executeScriptWorker.finished_with_script_result.connect(_on_task_finished)
        self.executeScriptWorker.stop_task()

    # def on_load_script(self):
    #     self.rologger.log(f'on_load_script')
    #     # 弹出文件选择对话框，默认打开 scripts 文件夹
    #     file_path, _ = QFileDialog.getOpenFileName(
    #         self,
    #         '选择要执行的脚本',
    #         'scripts',
    #         'Python files (*.py)'
    #     )
    #     if file_path:
    #         # 获取文件名（包含扩展名）
    #         file_name = os.path.basename(file_path)
    #         # 获取 scripts 目录绝对路径，并自动创建（防止目录不存在）
    #         scripts_dir = os.path.abspath('scripts')
    #         if not os.path.exists(scripts_dir):
    #             os.makedirs(scripts_dir)
    #         # 拼接最终脚本路径
    #         self.script_name = os.path.join(scripts_dir, file_name)
    #         # # 读取文件内容（你原来的代码只打开没读取，我帮你补上）
    #         # with open(file_path, 'r', encoding='utf-8') as f:
    #         #     self.script_content = f.read()
    #         self.rologger.log(f'成功加载脚本：{self.script_name}')
    #         self.rologger.log(f'请点击【开始测试】按钮执行脚本\n')
    def on_load_script(self):
        self.rologger.log(f'on_load_script')

        # ===================== 固定正确路径 =====================
        # 获取当前 .py 文件所在目录（rohand 文件夹）
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 拼接正确的 scripts 路径
        scripts_dir = os.path.join(base_dir, "scripts")

        # 自动创建目录
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)

        # 打开对话框，默认定位到正确的 scripts 目录
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择要执行的脚本',
            scripts_dir,  # 这里用正确路径
            'Python files (*.py)'
        )

        if file_path:
            # 直接使用选择到的路径（不再乱拼接）
            self.script_name = file_path

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
        for item in self.raw_test_data:
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

    # ========== 查看配置文件功能 ==========
    def on_view_config(self):
        """
        查看配置文件内容
        功能：读取配置文件并以只读方式显示
        """
        self.rologger.log(f'on_view_config')
        
        #  获取配置文件的完整路径
        config_path = RohanManager.get_configfile_path()
        
        #  检查配置文件是否存在
        if not os.path.exists(config_path):
            QMessageBox.warning(self, "警告", f"配置文件不存在：{config_path}")
            self.rologger.log(f"配置文件不存在：{config_path}")
            return
        
        # 读取配置文件内容
        try:
            with open(config_path, 'r', encoding='UTF-8') as f:
                config_content = f.read()  # 读取全部文本内容
            
            # 创建一个对话框窗口
            dialog = QDialog(self)
            dialog.setWindowTitle("查看配置文件")  # 设置窗口标题
            dialog.setMinimumSize(600, 800)  # 设置最小尺寸：宽 600，高 800
            
            #  创建垂直布局（控件从上到下排列）
            layout = QVBoxLayout()
            
            # 创建文本显示框（只读模式）
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)  # 设置为只读，不能编辑
            text_edit.setFont(QFont("Consolas", 10))  # 设置等宽字体，方便查看
            text_edit.setPlainText(config_content)  # 填入配置文件内容

            # 设置文本框样式：白色背景，黑色文字，清晰可读
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
            #  创建按钮框（只有一个"OK"按钮）
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)  # 点击确定后关闭对话框
            
            #  将控件添加到布局中
            layout.addWidget(text_edit)  # 添加文本框
            layout.addWidget(button_box)  # 添加按钮
            
            #  设置对话框的布局
            dialog.setLayout(layout)
            
            # 显示对话框（模态窗口，等待用户关闭）
            dialog.exec_()
            
            self.rologger.log(f"成功查看配置文件：{config_path}")
            
        except Exception as e:
            # 如果读取失败，显示错误提示
            QMessageBox.critical(self, "错误", f"读取配置文件失败：{str(e)}")
            self.rologger.log(f"读取配置文件失败：{str(e)}")

    # ========== 修改配置文件功能 ==========
    def on_edit_config(self):
        """
        修改配置文件内容
        功能：读取配置文件并允许用户编辑，保存后自动重启应用
        """
        self.rologger.log(f'on_edit_config')

        # 获取配置文件的完整路径
        config_path = RohanManager.get_configfile_path()

        # 检查配置文件是否存在
        if not os.path.exists(config_path):
            QMessageBox.warning(self, "警告", f"配置文件不存在：{config_path}")
            self.rologger.log(f"配置文件不存在：{config_path}")
            return

        # 读取配置文件内容
        try:
            with open(config_path, 'r', encoding='UTF-8') as f:
                config_content = f.read()

            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("修改配置文件")
            dialog.setMinimumSize(600, 800)

            # 创建布局
            layout = QVBoxLayout()

            # 创建提示标签
            hint_label = QLabel("提示：修改后需要重启应用程序才能生效")
            hint_label.setStyleSheet("color: #f59e0b; font-weight: bold; padding: 5px;")
            layout.addWidget(hint_label)

            # 创建文本编辑框
            text_edit = QTextEdit()
            text_edit.setFont(QFont("Consolas", 10))
            text_edit.setPlainText(config_content)

            # 设置文本框样式：白色背景，黑色文字，清晰可读
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

            # 创建按钮框
            button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

            # 绑定保存按钮
            save_button = button_box.button(QDialogButtonBox.Save)
            save_button.setText("保存")
            save_button.clicked.connect(
                lambda: self._save_config_and_restart(config_path, text_edit.toPlainText(), dialog)
            )

            # 绑定取消按钮
            cancel_button = button_box.button(QDialogButtonBox.Cancel)
            cancel_button.setText("取消")
            cancel_button.clicked.connect(dialog.reject)

            # 添加控件到布局
            layout.addWidget(text_edit)
            layout.addWidget(button_box)
            dialog.setLayout(layout)

            # 显示对话框
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"编辑配置文件失败：{str(e)}")
            self.rologger.log(f"编辑配置文件失败：{str(e)}")

    # ========== 保存配置并重启 ==========
    def _save_config_and_restart(self, config_path, content, dialog):
        """
        保存配置文件并重启应用程序

        参数:
            config_path: 配置文件路径
            content: 配置文件内容
            dialog: 当前对话框窗口
        """
        try:
            #  保存配置文件
            with open(config_path, 'w', encoding='UTF-8') as f:
                f.write(content)

            self.rologger.log(f"配置文件已保存：{config_path}")

            #  显示成功提示
            QMessageBox.information(self, "成功", "配置文件已保存，应用程序将自动重启...")

            #  关闭对话框
            dialog.accept()

            #  重启应用程序
            script_path = os.path.abspath(sys.argv[0])

            # 启动新进程（使用 start_new_session 确保独立运行）
            subprocess.Popen(
                [sys.executable, script_path],
                start_new_session=True,
                creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0
            )

            self.rologger.log("应用程序重启中...")

            #  等待 500ms：给新进程足够的时间启动
            import time
            time.sleep(0.5)

            #  关闭当前应用
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


# 定义端口刷新任务线程
# class PortRefreshWorker(QThread):
#     finished_with_ports = pyqtSignal(list, str)  # ports, error_message
#     def __init__(self, parent=None):
#         super().__init__(parent)
#     def run(self):
#         try:
#             protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
#             ports = RohanManager(protocol_type).read_port_info()
#             self.finished_with_ports.emit(ports, "")
#         except Exception as e:
#             self.finished_with_ports.emit([], str(e))
#
# # 定义设备信息获取任务线程
# class DeviceInfoWorker(QThread):
#      result_ready = pyqtSignal(list)
#
#      def __init__(self, ports, parent=None):
#          super().__init__(parent)
#          self.ports = ports
#
#      def run(self):
#          try:
#              protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
#              device_infos = RohanManager(protocol_type).get_device_info_list(self.ports)
#              self.result_ready.emit(device_infos)
#          except Exception as e:
#              self.result_ready.emit([])  #修复：永远返回列表

class DeviceInfosWorker(QThread):
    finished_with_device_infos = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            protocol_type = int(RohanManager.read_config_value(section="protocol_type", key="protocol", default=0))
            ports = RohanManager(protocol_type).read_port_info()
            device_infos = RohanManager(protocol_type).get_device_info_list(ports)
            self.finished_with_device_infos.emit(device_infos)
        except Exception as e:
            self.result_ready.emit([])  # 修复：永远返回列表


class ExecuteScriptWorker(QThread):
    finished_with_script_result = pyqtSignal(str, list)

    def __init__(self, ports: list, device_ids: list, aging_duration: float, script_path: str, parent=None):
        super().__init__(parent)
        self.ports = ports
        self.device_ids = device_ids
        self.aging_duration = aging_duration
        self.script_path = script_path

        # 停止标记（安全可控）
        self._is_stopped = False

    def run(self):
        try:
            # 执行前检查：已经停止就直接退出
            if self._is_stopped:
                self.finished_with_script_result.emit("任务已停止", [])
                return

            if not os.path.exists(self.script_path):
                self.finished_with_script_result.emit("脚本不存在", [])
                return

            if not self.ports:
                return

            script_dir = os.path.dirname(self.script_path)
            if script_dir not in sys.path:
                sys.path.append(script_dir)

            script_name = os.path.splitext(os.path.basename(self.script_path))[0]
            module = __import__(script_name)

            # 执行脚本
            report_title, overall_result = module.main(
                ports=self.ports,
                devices_ids=self.device_ids,
                aging_duration=self.aging_duration
            )

            # 如果中途被停止，返回停止信息
            if self._is_stopped:
                self.finished_with_script_result.emit("任务已停止", [])
                return

            self.finished_with_script_result.emit(report_title, overall_result)

        except Exception as e:
            if self._is_stopped:
                self.finished_with_script_result.emit("任务已停止", [])
            else:
                self.finished_with_script_result.emit(f"执行异常：{str(e)}", [])

    # 安全停止方法
    def stop_task(self):
        self._is_stopped = True


class ProgressBarWorker(QThread):
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