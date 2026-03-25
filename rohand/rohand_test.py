#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time
from datetime import datetime

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
        self.port_names = []
        self.test_data_table = None
        self.check_box_list = []
        self.script_loaded = False
        self.script_path = None
        self.protocol_type = None
        self.rohand_manager = None
        self.roHandLogger = None
        self.client = None

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
        self.test_data_table.setRowCount(100)
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
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.refresh_btn.clicked.connect(self.start_port_refresh)
        self.select_all_check.stateChanged.connect(self.on_select_all)
        self.start_test_btn.clicked.connect(self.on_start_test)
        self.pause_test_btn.clicked.connect(self.on_pause_test)
        self.stop_test_btn.clicked.connect(self.on_stop_test)
        self.log_level_btn.clicked.connect(self.on_log_level_clicked)

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

            # self.rologger.log(f"端口 {port} {'选中' if checked else '取消选中'}，已选：{self.select_port_names}")
        except Exception as e:
            self.rologger.log(f"复选框操作失败：{str(e)}")

    def update_test_data_table(self, port, checked):
        self.rologger.log('update_test_data_table')
        self.deviceInfoWorker = DeviceInfoWorker(port)
        self.deviceInfoWorker.result_ready.connect(self._on_device_info_update)
        self.deviceInfoWorker.finished.connect(self.deviceInfoWorker.deleteLater)
        self.deviceInfoWorker.start()

    def _on_device_info_update(self,device_info):
        self.rologger.log('_on_device_info_update')
        self.rologger.log(f'device_info = {device_info}')


    def _on_port_refresh_finished(self,ports,err):
        self.rologger.log(f'_on_port_refresh_finished, ports = {ports},err = {err}')
        self.port_names = ports
        if self.port_names and self.port_names[0] != "无可用端口":
            self.status_bar.showMessage("端口刷新完成")
            self.update_port_info()
        else:
            self.status_bar.showMessage("无可用端口")

    def start_port_refresh(self):
        self.rologger.log(f'start_port_refresh')
        self.port_refresh_worker  = PortRefreshWorker()
        self.port_refresh_worker.finished_with_ports.connect(self._on_port_refresh_finished)
        self.port_refresh_worker.start()
        self.status_bar.showMessage(f"端口刷新中，请耐心等待...")

    def on_select_all(self, state):
        self.rologger.log(f'on_select_all')

    def on_start_test(self):
        self.rologger.log(f'on_start_test')

    def on_pause_test(self):
        self.rologger.log(f'on_pause_test')

    def on_stop_test(self):
        self.rologger.log(f'on_stop_test')

    def on_load_script(self):
        self.rologger.log(f'on_load_script')

    def on_export_report(self):
        self.rologger.log(f'on_export_report')

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
     result_ready = pyqtSignal(dict)

     def __init__(self, port, parent=None):
         super().__init__(parent)
         self.port = port

     def run(self):
         try:
             DEFAULT_TEST_RESULT = 0
             protocol_type = RohanManager.read_config_value(section="protocol_type", key="protocol", default=0)
             device_info = RohanManager(protocol_type).get_device_info(self.port)
             self.result_ready.emit(device_info)
         except Exception as e:
             self.result_ready.emit(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RoHandTestWindow()
    win.setWindowTitle("灵巧手自动化测试界面")
    win.show()
    sys.exit(app.exec_())