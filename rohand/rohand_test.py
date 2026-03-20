#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import logging
import time
import traceback
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QCheckBox,
    QDialog, QLabel, QProgressBar, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.uic import loadUi

from rohand_manager import RohanManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 文件日志：统一写到 ../log/ClientTest_log_日期_时间戳.txt
_log_file_configured = False


def _setup_file_logging_once():
    global _log_file_configured
    if _log_file_configured:
        return
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_folder = os.path.normpath(os.path.join(base_dir, "..", "log"))
    os.makedirs(log_folder, exist_ok=True)

    timestamp = str(int(time.time()))
    current_date = time.strftime("%Y-%m-%d", time.localtime())
    log_file_name = os.path.join(log_folder, f"ClientTest_log_{current_date}_{timestamp}.txt")

    file_handler = logging.FileHandler(log_file_name, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(log_format)
    setattr(file_handler, "_is_client_file_handler", True)

    root_logger = logging.getLogger()
    # 避免重复添加同类 handler
    for h in root_logger.handlers:
        if getattr(h, "_is_client_file_handler", False):
            _log_file_configured = True
            return
    root_logger.addHandler(file_handler)
    _log_file_configured = True


_setup_file_logging_once()

# ---------------------------------------------------------------------------
# 文案与表格列名（集中定义，不放在 class 内；须与 rohand_manager.get_device_info 键一致）
# ---------------------------------------------------------------------------
COL_PORT = "端口号"
COL_SOFTWARE_VERSION = "软件版本"
COL_DEVICE_ID = "设备ID"
COL_CONNECT_STATUS = "连接状态"
COL_TEST_RESULT = "测试结果"

TABLE_HEADERS = [
    COL_PORT,
    COL_SOFTWARE_VERSION,
    COL_DEVICE_ID,
    COL_CONNECT_STATUS,
    COL_TEST_RESULT,
]

RESULT_PASS = "通过"
RESULT_FAIL = "失败"
RESULT_SKIP = "跳过"

STATUS_CONNECTED_UI = "已连接"
STATUS_WAIT_TEST = "等待测试"
STATUS_TESTING = "测试中"
STATUS_PAUSED = "测试暂停"
STATUS_UNKNOWN_DEVICE = "未识别设备"
STATUS_READ_FAIL = "读取失败"
STATUS_NOT_CONNECTED = "未连接"

MSG_HINT = "提示"
MSG_REFRESH_PORT = "请刷新端口"
MSG_REFRESHING_PORTS = "正在刷新端口..."
BTN_REFRESH = "刷新"
BTN_LATER = "稍后"
LABEL_SELECT_ALL = "全选"

DIALOG_REFRESH_TITLE = "正在刷新端口"
DIALOG_REFRESH_TIP = "正在刷新端口..."

DEFAULT_AGING_OPTIONS = [
    "0.01小时", "0.1小时", "0.5小时", "1小时", "1.5小时",
    "3小时", "8小时", "12小时", "24小时",
]

# 主窗口完全显示后再弹出「请刷新端口」的延迟（毫秒），避免与首帧同时阻塞
REFRESH_PROMPT_DELAY_MS = 450


class RoHandGuiLogFilter(logging.Filter):
    """仅把关键信息打到界面日志区。"""

    _INFO_KEYWORDS = (
        "初始化管理器", "开始刷新端口", "检测到", "加载脚本", "测试启动",
        "测试完成", "测试结束", "成功创建", "could not connect", "连接失败",
        "端口", "脚本导入成功", "脚本导入失败", "测试启动失败",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        name = record.name or ""
        if not (name.startswith("rohand") or name.startswith("__main__")):
            return False
        if record.levelno >= logging.WARNING:
            return True
        msg = (record.getMessage() or "").lower()
        return any(k.lower() in msg for k in self._INFO_KEYWORDS)


class GuiLogHandler(logging.Handler):
    """将日志追加到 QTextEdit（线程安全投递到主线程）。"""

    def __init__(self, append_fn):
        super().__init__()
        self.append_fn = append_fn
        self._is_rohand_gui_handler = True

    def emit(self, record):
        try:
            msg = self.format(record)
        except Exception:
            return
        try:
            QTimer.singleShot(0, lambda m=msg: self.append_fn(m))
        except Exception:
            pass

# ==============================
# 自定义日志处理器，用于捕获测试脚本的日志
# ==============================
class ScriptLogHandler(logging.Handler):
    def __init__(self, log_signal):
        super().__init__()
        self.log_signal = log_signal
    
    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_signal.emit(msg)
        except Exception:
            pass

# ==============================
# 测试线程类
# ==============================
class TestThread(QThread):
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    table_update = pyqtSignal(int, str, str, str, str)
    result_update = pyqtSignal(int, int, int, int)
    status_update = pyqtSignal(str)

    def __init__(self, selected_ports, rohan_manager, script_path, aging_time, parent=None):
        super().__init__(parent)
        self.is_running = True
        self.is_paused = False
        self.selected_ports = selected_ports
        self.rohan_manager = rohan_manager
        self.script_path = script_path
        self.aging_time = aging_time
        self.parent = parent
        # 创建脚本日志处理器
        self.script_log_handler = ScriptLogHandler(self.log_update)

    def run(self):
        total = len(self.selected_ports)
        if total == 0:
            self.status_update.emit("没有选中的端口进行测试")
            self.log_update.emit(f"[{self.get_time()}] 测试启动失败：没有选中的端口")
            return
        
        # 解析老化时间
        aging_hours = float(self.aging_time.split('小时')[0])
        aging_seconds = int(aging_hours * 3600)
        
        success = fail = skip = 0
        self.status_update.emit("测试开始...")
        self.log_update.emit(f"[{self.get_time()}] 测试启动，总端口数：{total}，老化时间：{self.aging_time}")

        # 导入脚本模块
        script_module = self.import_script()
        if not script_module:
            self.status_update.emit("测试失败：脚本导入失败")
            self.log_update.emit(f"[{self.get_time()}] 测试失败：脚本导入失败")
            return

        start_time = datetime.now()
        # 计算每个端口的测试时间
        per_port_time = aging_seconds / total if total > 0 else 0
        
        for i, port in enumerate(self.selected_ports):
            if not self.is_running:
                break
            while self.is_paused:
                self.msleep(100)

            # 测试真实端口
            port_start_time = datetime.now()
            
            # 创建一个子线程来执行测试，以便在测试期间更新进度条
            import threading
            test_result = [RESULT_FAIL]
            
            def run_test():
                nonlocal test_result
                test_result[0] = self.test_port(port, script_module)
            
            test_thread = threading.Thread(target=run_test)
            test_thread.daemon = True
            test_thread.start()
            
            # 在测试执行期间更新进度条
            while test_thread.is_alive():
                if not self.is_running:
                    break
                while self.is_paused:
                    self.msleep(100)
                # 实时计算测试进度
                elapsed_time = (datetime.now() - start_time).total_seconds()
                progress = min(int((elapsed_time / aging_seconds) * 100), 100)
                self.progress_update.emit(progress)
                self.msleep(100)  # 每100毫秒更新一次进度
            
            # 获取测试结果
            res = test_result[0]
            success += 1 if res == RESULT_PASS else 0
            fail += 1 if res == RESULT_FAIL else 0
            skip += 1 if res == RESULT_SKIP else 0

            self.log_update.emit(f"[{self.get_time()}] 测试端口 {port}：{res}")
            self.table_update.emit(i, port, "-", "-", res)
            self.result_update.emit(total, success, fail, skip)
            
            # 计算该端口测试所用时间
            port_elapsed_time = (datetime.now() - port_start_time).total_seconds()
            # 根据老化时间调整测试间隔，确保总测试时间接近老化时间
            wait_time = max(0, int((per_port_time - port_elapsed_time) * 1000))
            
            # 等待期间实时更新进度条
            wait_start_time = datetime.now()
            while (datetime.now() - wait_start_time).total_seconds() * 1000 < wait_time:
                if not self.is_running:
                    break
                while self.is_paused:
                    self.msleep(100)
                # 实时计算测试进度
                elapsed_time = (datetime.now() - start_time).total_seconds()
                progress = min(int((elapsed_time / aging_seconds) * 100), 100)
                self.progress_update.emit(progress)
                self.msleep(100)  # 每100毫秒更新一次进度

        # 确保进度条达到100%
        self.progress_update.emit(100)

        if self.is_running:
            self.status_update.emit("测试完成！")
            self.log_update.emit(f"[{self.get_time()}] 测试结束 - 成功：{success} | 失败：{fail} | 跳过：{skip}")
            # 发送信号更新测试状态标签为等待测试
            if self.parent and hasattr(self.parent, 'test_status_label'):
                self.parent.test_status_label.setText(STATUS_WAIT_TEST)
        else:
            self.status_update.emit("测试已停止")
            self.log_update.emit(f"[{self.get_time()}] 测试被手动停止")
            # 发送信号更新测试状态标签为等待测试
            if self.parent and hasattr(self.parent, 'test_status_label'):
                self.parent.test_status_label.setText(STATUS_WAIT_TEST)

    def import_script(self):
        """导入脚本模块"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_script", self.script_path)
            script_module = importlib.util.module_from_spec(spec)
            
            # 为脚本模块添加日志处理器
            script_logger = logging.getLogger("test_script")
            script_logger.setLevel(logging.INFO)
            # 清除现有的处理器，避免重复
            for handler in script_logger.handlers[:]:
                script_logger.removeHandler(handler)
            # 添加我们的自定义处理器
            script_logger.addHandler(self.script_log_handler)
            
            spec.loader.exec_module(script_module)
            self.log_update.emit(f"[{self.get_time()}] 脚本导入成功")
            return script_module
        except Exception as e:
            self.log_update.emit(f"[{self.get_time()}] 脚本导入失败：{str(e)}")
            return None

    def test_port(self, port, script_module=None):
        """测试单个端口"""
        try:
            # 检查是否有脚本模块
            if script_module:
                # 检查脚本是否有test_single_port函数（motor_current_test_v2.py使用这个函数）
                if hasattr(script_module, 'test_single_port'):
                    # 使用motor_current_test_v2.py中的测试逻辑
                    try:
                        # 调用test_single_port函数，传入端口和节点ID
                        port_result, connected_status = script_module.test_single_port(port, 2, False)
                        # 检查测试结果
                        if connected_status:
                            # 检查是否所有手势测试都通过
                            all_passed = True
                            for gesture_result in port_result["gestures"]:
                                if gesture_result["result"] != RESULT_PASS:
                                    all_passed = False
                                    break
                            return RESULT_PASS if all_passed else RESULT_FAIL
                        else:
                            return RESULT_FAIL
                    except Exception as e:
                        self.log_update.emit(f"[{self.get_time()}] 脚本测试失败：{str(e)}")
                        return RESULT_FAIL
                # 保持对原有test_port函数的支持
                elif hasattr(script_module, 'test_port'):
                    # 使用脚本中的测试逻辑
                    try:
                        result = script_module.test_port(port, self.rohan_manager)
                        return RESULT_PASS if result else RESULT_FAIL
                    except Exception as e:
                        self.log_update.emit(f"[{self.get_time()}] 脚本测试失败：{str(e)}")
                        return RESULT_FAIL
                    finally:
                        try:
                            if getattr(self.rohan_manager, "client", None):
                                self.rohan_manager.client.disconnect()
                        except Exception:
                            pass
                else:
                    # 没有脚本，使用默认测试逻辑
                    if self.rohan_manager.create_client(port):
                        try:
                            return RESULT_PASS
                        finally:
                            try:
                                if getattr(self.rohan_manager, "client", None):
                                    self.rohan_manager.client.disconnect()
                            except Exception:
                                pass
                    else:
                        return RESULT_FAIL
            else:
                # 没有脚本模块，使用默认测试逻辑
                if self.rohan_manager.create_client(port):
                    try:
                        return RESULT_PASS
                    finally:
                        try:
                            if getattr(self.rohan_manager, "client", None):
                                self.rohan_manager.client.disconnect()
                        except Exception:
                            pass
                else:
                    return RESULT_FAIL
        except Exception as e:
            self.log_update.emit(f"[{self.get_time()}] 测试端口 {port} 异常：{str(e)}")
            return RESULT_FAIL

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


class PortRefreshThread(QThread):
    finished_with_ports = pyqtSignal(list, str)  # ports, error_message

    def __init__(self, protocol_type: int = 0, simulate_delay_ms: int = 0, parent=None):
        super().__init__(parent)
        self.protocol_type = protocol_type
        self.simulate_delay_ms = max(0, int(simulate_delay_ms or 0))

    def run(self):
        try:
            if self.simulate_delay_ms > 0:
                self.msleep(self.simulate_delay_ms)
            rohan_manager = RohanManager(protocol_type=self.protocol_type)
            ports = rohan_manager.read_port_info() or []
            self.finished_with_ports.emit(ports, "")
        except Exception as e:
            self.finished_with_ports.emit([], str(e))


class PortRefreshingDialog(QDialog):
    def __init__(self, parent=None, title: str = DIALOG_REFRESH_TITLE, tip: str = DIALOG_REFRESH_TIP, timeout_seconds: int = 60):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(300, 140)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.timeout_seconds = timeout_seconds
        self.remaining_time = timeout_seconds

        # 创建倒计时标签
        self.countdown_label = QLabel(f"{self.remaining_time}秒", self)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #3b82f6;")

        # 创建提示标签
        self.tip_label = QLabel(tip, self)
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setFont(QFont("Arial", 12))

        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, self.timeout_seconds)
        self.progress_bar.setValue(self.timeout_seconds)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e5e7eb;
                border-radius: 5px;
                background-color: #f3f4f6;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)

        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加倒计时标签
        layout.addWidget(self.countdown_label)
        
        # 添加提示标签
        layout.addWidget(self.tip_label)
        
        # 添加进度条
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

        # 创建计时器
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 每秒更新一次
        self._timer.timeout.connect(self._tick)

    def start(self):
        self.remaining_time = self.timeout_seconds
        self.countdown_label.setText(f"{self.remaining_time}秒")
        self.progress_bar.setValue(self.remaining_time)
        self._timer.start()
        self.show()

    def stop(self):
        self._timer.stop()
        self.close()

    def _tick(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            self.countdown_label.setText(f"{self.remaining_time}秒")
            self.progress_bar.setValue(self.remaining_time)
        else:
            self._timer.stop()


# ==============================
# 主窗口类
# ==============================
class RoHandTestWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config_path = RohanManager.get_config_path()
        self.protocol_type = 0  # 仅由 config.ini [protocol_type] protocol 决定
        self._did_schedule_refresh_prompt = False
        self.select_port_names = []
        self.port_names = ['无可用端口']
        self.test_data_table = None
        self.check_box_list = []
        self.script_loaded = False
        self.script_path = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "rohand_test.ui")
        if not os.path.exists(ui_path):
            ui_path = os.path.join(current_dir, "ui", "rohand_test.ui")
        loadUi(ui_path, self)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self._load_protocol_from_config_file()
        self.init_ui()
        self._default_qss = self.styleSheet() or ""
        self.bind_all_events()
        self._attach_project_log_handler()
        self.test_thread = TestThread([], self._get_manager(), None, '0.5小时', self)
        self.bind_thread_signals()

        self._port_refresh_thread = None
        self._port_refresh_dialog = None
        self._port_refresh_timeout_timer = QTimer(self)
        self._port_refresh_timeout_timer.setSingleShot(True)
        self._port_refresh_timeout_timer.timeout.connect(self._on_port_refresh_timeout)
        self._port_refresh_timed_out = False

    def showEvent(self, event):
        """主窗口首次完整显示后再弹出「请刷新端口」，避免与首帧同时弹窗卡死。"""
        super().showEvent(event)
        if self._did_schedule_refresh_prompt:
            return
        self._did_schedule_refresh_prompt = True
        QTimer.singleShot(REFRESH_PROMPT_DELAY_MS, self._prompt_refresh_ports)

    def init_ui(self):
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("Consolas", 10))

        self.test_data_table = QTableWidget(self.test_data_group)
        self.test_data_table.setGeometry(10, 30, 800, 580)
        self.test_data_table.setColumnCount(5)
        self.test_data_table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.test_data_table.setRowCount(100)
        header = self.test_data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.aging_time_combo.clear()
        self.aging_time_combo.addItems(DEFAULT_AGING_OPTIONS)
        self.port_list_Layout.setContentsMargins(12, 8, 18, 8)
        self.test_progress_bar.setRange(0, 100)
        self.test_progress_bar.setValue(0)

        self.total_case_value.setText("0条")
        self.success_case_value.setText("0条")
        self.fail_case_value.setText("0条")
        self.skip_case_value.setText("0条")

        self.log_text_edit.append(f"[{self.get_time()}] {MSG_REFRESH_PORT}")
        self.status_bar.showMessage(MSG_REFRESH_PORT)

    def _prompt_refresh_ports(self):
        box = QMessageBox(self)
        box.setWindowTitle(MSG_HINT)
        box.setIcon(QMessageBox.Information)
        box.setText(MSG_REFRESH_PORT)
        refresh_btn = box.addButton(BTN_REFRESH, QMessageBox.AcceptRole)
        box.addButton(BTN_LATER, QMessageBox.RejectRole)
        box.exec_()
        if box.clickedButton() == refresh_btn:
            self.start_port_refresh()

    def bind_all_events(self):
        # 按钮绑定
        self.log_copy_btn.clicked.connect(self.on_copy_log)
        self.log_clear_btn.clicked.connect(self.on_clear_log)
        self.log_save_btn.clicked.connect(self.on_save_log)
        self.refresh_btn.clicked.connect(self.start_port_refresh)
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

        # 快捷键已经在UI文件中定义，无需重复定义

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
            if port == LABEL_SELECT_ALL:
                self.select_port_names = self.port_names.copy() if checked else []
                for cbx in self.check_box_list:
                    if cbx.text() != LABEL_SELECT_ALL:
                        cbx.setChecked(checked)
                        self.update_test_data_table(cbx.text(), checked)
            # 2. 单个端口逻辑
            else:
                if checked and port not in self.select_port_names:
                    self.select_port_names.append(port)
                elif not checked and port in self.select_port_names:
                    self.select_port_names.remove(port)
                self.update_test_data_table(port, checked)

            self.log_text_edit.append(
                f"[{self.get_time()}] 端口 {port} {'选中' if checked else '取消选中'}，已选：{self.select_port_names}")
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 复选框操作失败：{str(e)}")

    def on_refresh(self):
        """旧同步刷新（保留供内部复用：只负责把端口列表渲染到UI）。"""
        try:
            # 1. 安全清空（先判空，避免布局不存在报错）
            if not hasattr(self, 'port_list_Layout') or self.port_list_Layout is None:
                self.log_text_edit.append(f"[{self.get_time()}] 错误：port_list_Layout 未加载！")
                return

            # 2. 彻底清空旧布局和列表
            self.check_box_list.clear()
            self.select_port_names.clear()
            self.remove_all_widgets_from_layout(self.port_list_Layout)

            # 3. 无端口处理（端口扫描由后台线程负责，这里只渲染）
            if not self.port_names:
                self.port_names = ['无可用端口']
            if not self.port_names or self.port_names[0] == '无可用端口':
                self.log_text_edit.append(f"[{self.get_time()}] 无可用端口")
                return

            # 7. 布局配置（每列8个，最多4列）
            max_per_col = 8
            max_col = 4
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
                # 走全局 QSS，避免主题切换时被局部样式“顶掉”
                check_box.setObjectName("port_checkbox")

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
            self.log_text_edit.append(f"错误详情：{traceback.format_exc()}")

    def start_port_refresh(self):
        """点击刷新后：显示动画 + 60秒超时 + 完成后自动停止。"""
        if self._port_refresh_thread and self._port_refresh_thread.isRunning():
            return

        protocol_type = self._get_manager(refresh_protocol=True).protocol_type
        self.log_text_edit.append(f"[{self.get_time()}] 从配置文件读取协议类型：{protocol_type}（0=Modbus，1=CAN）")

        simulate_timeout = bool(QApplication.keyboardModifiers() & Qt.ShiftModifier)

        self._port_refresh_timed_out = False
        self.status_bar.showMessage("正在刷新端口...")
        if simulate_timeout:
            self.log_text_edit.append(f"[{self.get_time()}] 开始刷新端口...（Shift模拟超时）")
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 开始刷新端口...")

        if self._port_refresh_dialog is None:
            self._port_refresh_dialog = PortRefreshingDialog(self, tip=DIALOG_REFRESH_TIP, timeout_seconds=60)
        self._port_refresh_dialog.start()

        self._port_refresh_timeout_timer.start(60_000)

        delay_ms = 65_000 if simulate_timeout else 0
        self._port_refresh_thread = PortRefreshThread(protocol_type=protocol_type, simulate_delay_ms=delay_ms, parent=self)
        self._port_refresh_thread.finished_with_ports.connect(self._on_port_refresh_finished)
        self._port_refresh_thread.start()

    def _on_port_refresh_timeout(self):
        self._port_refresh_timed_out = True
        if self._port_refresh_thread and self._port_refresh_thread.isRunning():
            # 不强杀线程（可能导致不稳定），只提示超时，后续结果忽略
            pass
        if self._port_refresh_dialog:
            self._port_refresh_dialog.stop()
        self.status_bar.showMessage("刷新已超时")
        self.log_text_edit.append(f"[{self.get_time()}] 刷新已超时")
        QMessageBox.warning(self, "提示", "刷新已超时")

    def _on_port_refresh_finished(self, ports: list, error_message: str):
        if self._port_refresh_timeout_timer.isActive():
            self._port_refresh_timeout_timer.stop()

        if self._port_refresh_dialog:
            self._port_refresh_dialog.stop()

        if self._port_refresh_timed_out:
            return

        if error_message:
            self.status_bar.showMessage("端口刷新失败")
            self.log_text_edit.append(f"[{self.get_time()}] 端口刷新失败：{error_message}")
            QMessageBox.warning(self, "提示", f"端口刷新失败：{error_message}")
            return

        self.port_names = ports or ['无可用端口']
        logger.info(f"检测到端口：{self.port_names}")

        # 渲染到UI（复用原逻辑）
        self.on_refresh()

        # 状态栏提示（按你的需求：完成时显示）
        if self.port_names and self.port_names[0] != '无可用端口':
            self.status_bar.showMessage("端口刷新完成，")
        else:
            self.status_bar.showMessage("无可用端口")

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
                self.update_test_data_table(cbx.text(), checked)
            self.log_text_edit.append(
                f"[{self.get_time()}] 全选状态：{'选中' if checked else '取消'}，已选：{self.select_port_names}")
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 全选操作失败：{str(e)}")

    def on_start_test(self):
        if not self.test_thread.isRunning():
            # 检查脚本是否已加载
            if not self.script_loaded:
                QMessageBox.warning(self, "提示", "请先加载脚本")
                self.log_text_edit.append(f"[{self.get_time()}] 测试启动失败：请先加载脚本")
                return
            
            # 获取老化时间
            aging_time = self.aging_time_combo.currentText()
            
            # 创建RohanManager实例
            # 只刷新协议类型配置，避免窗口在开始测试时被“重置”
            rohan_manager = self._get_manager(refresh_protocol=True)
            # 创建新的测试线程，传递选中的端口列表、rohan_manager实例、脚本路径和老化时间
            self.test_thread = TestThread(self.select_port_names, rohan_manager, self.script_path, aging_time, self)
            self.bind_thread_signals()
            self.test_thread.is_running = True
            self.test_thread.is_paused = False
            # 恢复暂停测试按钮的文本
            self.pause_test_btn.setText("暂停测试")
            # 更新测试状态标签
            self.test_status_label.setText(STATUS_TESTING)
            self.test_thread.start()
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试已在运行中")

    def on_pause_test(self):
        if self.test_thread.isRunning():
            if self.test_thread.is_paused:
                self.test_thread.resume()
                self.pause_test_btn.setText("暂停测试")
                # 更新测试状态标签为测试中
                self.test_status_label.setText(STATUS_TESTING)
            else:
                self.test_thread.pause()
                self.pause_test_btn.setText("恢复测试")
                # 更新测试状态标签为测试暂停
                self.test_status_label.setText(STATUS_PAUSED)
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试未运行")

    def on_stop_test(self):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            # 更新测试状态标签为等待测试
            self.test_status_label.setText(STATUS_WAIT_TEST)
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 测试未运行")

    def on_load_script(self):
        fn, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python文件 (*.py);;所有文件 (*.*)")
        if fn:
            self.script_loaded = True  # 标记脚本已加载
            self.script_path = fn  # 保存脚本路径
            self.log_text_edit.append(f"[{self.get_time()}] 加载脚本：{os.path.basename(fn)}")

    def on_export_report(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        report_dir = os.path.join(current_dir, "report")
        try:
            os.makedirs(report_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"创建report文件夹失败：{str(e)}")
            return

        default_filename = f"测试报告_{self.get_time().replace(':', '-')}.txt"
        default_path = os.path.join(report_dir, default_filename)
        fn, _ = QFileDialog.getSaveFileName(
            self, "导出报告", default_path, "文本文件 (*.txt)"
        )

        if fn:
            try:
                file_dir = os.path.dirname(fn)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                
                # 写入文件
                with open(fn, "w", encoding="utf-8") as f:
                    # 写入报告标题和时间
                    f.write(f"灵巧手测试报告\n")
                    f.write(f"生成时间：{self.get_time()}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    # 写入测试结果
                    f.write("测试结果：\n")
                    f.write(f"总用例：{self.total_case_value.text()}\n")
                    f.write(f"成功用例：{self.success_case_value.text()}\n")
                    f.write(f"失败用例：{self.fail_case_value.text()}\n")
                    f.write(f"跳过用例：{self.skip_case_value.text()}\n\n")
                    
                    # 写入日志内容
                    f.write("测试日志：\n")
                    f.write("-" * 60 + "\n")
                    log_content = self.log_text_edit.toPlainText()
                    f.write(log_content)
                    f.write("\n" + "-" * 60 + "\n")
                
                # 验证文件是否存在
                if os.path.exists(fn):
                    file_size = os.path.getsize(fn)
                    self.log_text_edit.append(f"[{self.get_time()}] 报告文件创建成功，大小：{file_size} 字节")
                    QMessageBox.information(self, "成功", f"报告已成功导出到：\n{fn}\n文件大小：{file_size} 字节")
                else:
                    self.log_text_edit.append(f"[{self.get_time()}] 报告文件创建失败，文件不存在")
                    QMessageBox.warning(self, "错误", "报告文件创建失败，文件不存在")
                    
            except Exception as e:
                self.log_text_edit.append(f"[{self.get_time()}] 导出报告失败：{str(e)}")
                QMessageBox.warning(self, "错误", f"导出报告失败：{str(e)}")
        else:
            self.log_text_edit.append(f"[{self.get_time()}] 用户取消导出报告")

    def on_view_config(self):
        fn = self._config_path
        if fn:
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    content = f.read()[:1000]
                QMessageBox.information(self, "配置内容", f"仅显示前1000字符：\n{content}")
                self.log_text_edit.append(f"[{self.get_time()}] 查看配置：{os.path.basename(fn)}")
            except Exception as e:
                self.log_text_edit.append(f"[{self.get_time()}] 查看配置失败：{str(e)}")

    def on_edit_config(self):
        fn = self._config_path
        if fn:
            try:
                # 检查文件是否存在
                if not os.path.exists(fn):
                    self.log_text_edit.append(f"[{self.get_time()}] 配置文件不存在：{fn}")
                    QMessageBox.warning(self, "错误", f"配置文件不存在：{fn}")
                    return
                
                # 检查文件是否可写
                if not os.access(fn, os.W_OK):
                    self.log_text_edit.append(f"[{self.get_time()}] 配置文件不可写：{fn}")
                    QMessageBox.warning(self, "错误", f"配置文件不可写，请检查权限：{fn}")
                    return
                
                if sys.platform == "win32":
                    os.startfile(fn)
                    self.log_text_edit.append(f"[{self.get_time()}] 打开配置：{os.path.basename(fn)}")
                else:
                    # 非Windows系统的处理
                    import subprocess
                    subprocess.run(["xdg-open", fn])
                    self.log_text_edit.append(f"[{self.get_time()}] 打开配置：{os.path.basename(fn)}")

                QMessageBox.information(
                    self,
                    MSG_HINT,
                    "已打开配置文件。\n仅 [protocol_type] 中 protocol=0/1 会切换 Modbus/CAN；\n"
                    "保存后窗口将自动重启以应用新协议。",
                )
                # 使用一个定时器在消息框关闭后重启应用（避免当前事件栈中直接重启）
                QTimer.singleShot(0, self._restart_application)
            except Exception as e:
                self.log_text_edit.append(f"[{self.get_time()}] 打开配置文件失败：{str(e)}")
                QMessageBox.warning(self, "错误", f"打开配置文件失败：{str(e)}")

    def on_theme_black(self):
        self.setStyleSheet(self._qss_black())
        self.log_text_edit.append(f"[{self.get_time()}] 切换为黑色主题")

    def on_theme_green(self):
        self.setStyleSheet(self._qss_green())
        self.log_text_edit.append(f"[{self.get_time()}] 切换为绿色主题")

    def on_theme_default(self):
        # 恢复“刚进入程序时”的主题，而不是清空 QSS
        self.setStyleSheet(getattr(self, "_default_qss", "") or "")
        self.log_text_edit.append(f"[{self.get_time()}] 切换为默认主题")

    @staticmethod
    def _qss_black() -> str:
        # 现代深色主题（统一控件：表格/菜单/滚动条/输入框/按钮/分组框）
        return """
        QMainWindow { background-color: #0b1220; }

        QWidget { color: #e5e7eb; font-size: 15px; }

        QGroupBox {
            background-color: #0f172a;
            border: 2px solid #243047;
            border-radius: 10px;
            margin-top: 12px;
            padding-top: 8px;
            font-weight: 600;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px;
            color: #93c5fd;
            font-size: 17px;
            font-weight: 700;
        }

        QLabel { color: #cbd5e1; }
        QLabel#success_case_label, QLabel#success_case_value { color: #34d399; font-weight: 700; }
        QLabel#fail_case_label, QLabel#fail_case_value { color: #fb7185; font-weight: 700; }
        QLabel#skip_case_label, QLabel#skip_case_value { color: #fbbf24; font-weight: 700; }
        QLabel#total_case_label, QLabel#total_case_value { color: #94a3b8; font-weight: 700; }

        QPushButton {
            background-color: #1f2a44;
            color: #e5e7eb;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #263455;
            border-color: #60a5fa;
        }
        QPushButton:pressed {
            background-color: #16213a;
            border-color: #93c5fd;
            padding-left: 8px;
            padding-top: 8px;
        }
        QPushButton#start_test_btn, QPushButton#pause_test_btn, QPushButton#stop_test_btn {
            font-size: 20px;
            font-weight: 700;
        }

        QComboBox {
            background-color: #0b1220;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 4px 8px;
            min-height: 28px;
            color: #e5e7eb;
        }
        QComboBox:hover { border-color: #60a5fa; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            background-color: #0f172a;
            border: 2px solid #334155;
            border-radius: 8px;
            selection-background-color: #1d4ed8;
            selection-color: #ffffff;
        }

        QCheckBox { color: #cbd5e1; padding: 8px 12px; margin: 4px 0; border-radius: 8px; }
        QCheckBox#port_checkbox { background-color: #0b1220; border: 1px solid #243047; }
        QCheckBox#port_checkbox:hover { background-color: #0f172a; border-color: #334155; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #334155;
            border-radius: 4px;
            background-color: #0b1220;
            margin-right: 8px;
        }
        QCheckBox::indicator:checked { background-color: #60a5fa; border-color: #93c5fd; }

        QTableWidget {
            background-color: #0b1220;
            border: 2px solid #243047;
            border-radius: 10px;
            gridline-color: #1f2a44;
            selection-background-color: #1d4ed8;
        }
        QTableWidget::item { padding: 10px; }
        QTableWidget::item:selected { background-color: #1d4ed8; color: #ffffff; }
        QHeaderView::section {
            background-color: #0f172a;
            border: none;
            border-bottom: 2px solid #243047;
            padding: 8px;
            font-weight: 700;
            color: #93c5fd;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }

        QTextEdit#log_text_edit {
            background-color: #0b1220;
            border: 2px solid #243047;
            border-radius: 10px;
            color: #e5e7eb;
            selection-background-color: #1d4ed8;
            selection-color: #ffffff;
        }

        QProgressBar {
            border: 2px solid #243047;
            border-radius: 10px;
            text-align: center;
            background-color: #0f172a;
            color: #e5e7eb;
            font-weight: 700;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #60a5fa, stop:1 #2563eb);
            border-radius: 8px;
            margin: 1px;
        }

        QMenuBar {
            background-color: #0f172a;
            border-bottom: 2px solid #243047;
            color: #e5e7eb;
            font-weight: 600;
        }
        QMenuBar::item {
            padding: 8px 18px;
            margin: 2px;
            border-radius: 8px;
            background-color: transparent;
            border: 2px solid transparent;
        }
        QMenuBar::item:selected {
            background-color: #1f2a44;
            border-color: #60a5fa;
        }
        QMenu {
            background-color: #0f172a;
            border: 2px solid #243047;
            border-radius: 10px;
            padding: 8px 0;
        }
        QMenu::item {
            padding: 8px 28px;
            margin: 0 4px;
            border-radius: 8px;
            border: 2px solid transparent;
        }
        QMenu::item:selected {
            background-color: #1f2a44;
            border-color: #60a5fa;
        }
        QMenu::separator {
            height: 2px;
            background-color: #243047;
            margin: 6px 10px;
        }

        QScrollArea#port_scroll_area { border: none; background-color: transparent; }
        QScrollArea#port_scroll_area QWidget#scroll_content_widget {
            border: 2px solid #243047;
            border-radius: 10px;
            background-color: #0f172a;
            padding: 10px;
        }
        QScrollBar:vertical {
            width: 8px;
            background-color: #0f172a;
            border-radius: 4px;
            margin: 0 2px;
        }
        QScrollBar::handle:vertical {
            background-color: #334155;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background-color: #60a5fa; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        
        /* 关于对话框样式 */
        QMessageBox { background-color: white; color: #333333; }
        QMessageBox QLabel { color: #333333; font-weight: normal; }
        QMessageBox QPushButton { 
            background-color: #1f2a44; 
            color: #e5e7eb; 
            border: 2px solid #334155; 
            border-radius: 8px; 
            padding: 6px 12px; 
            font-weight: 600; 
        }
        QMessageBox QPushButton:hover { 
            background-color: #263455; 
            border-color: #60a5fa; 
        }
        """

    @staticmethod
    def _qss_green() -> str:
        # 清爽绿色主题（保留“现代白底”体系，用绿色作为主色）
        return """
        QMainWindow { background-color: #f6fbf8; }

        QWidget { color: #0f172a; font-size: 15px; }

        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            color: #0f172a;
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            margin-top: 12px;
            background-color: #ffffff;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px;
            color: #16a34a;
            font-size: 17px;
            font-weight: 800;
        }

        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #22c55e, stop:1 #16a34a);
            color: #ffffff;
            border: 2px solid #16a34a;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 700;
        }
        QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4ade80, stop:1 #22c55e); }
        QPushButton:pressed { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #15803d, stop:1 #166534); padding-left: 8px; padding-top: 8px; }
        QPushButton#start_test_btn, QPushButton#pause_test_btn, QPushButton#stop_test_btn { font-size: 20px; font-weight: 800; }

        QComboBox {
            border: 2px solid #bbf7d0;
            border-radius: 8px;
            padding: 4px 8px;
            background-color: #ffffff;
            min-height: 28px;
        }
        QComboBox:hover { border-color: #22c55e; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            border: 2px solid #22c55e;
            border-radius: 8px;
            background-color: #ffffff;
            selection-background-color: #dcfce7;
            selection-color: #166534;
        }

        QCheckBox { padding: 8px 12px; margin: 4px 0; border-radius: 8px; }
        QCheckBox#port_checkbox { background-color: #ffffff; border: 1px solid #dcfce7; }
        QCheckBox#port_checkbox:hover { background-color: #f0fdf4; border-color: #bbf7d0; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #bbf7d0;
            border-radius: 4px;
            background-color: #ffffff;
            margin-right: 8px;
        }
        QCheckBox::indicator:checked { background-color: #22c55e; border-color: #16a34a; }

        QTableWidget {
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            background-color: #ffffff;
            gridline-color: #dcfce7;
        }
        QTableWidget::item { padding: 10px; }
        QTableWidget::item:selected { background-color: #dcfce7; color: #166534; }
        QHeaderView::section {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ecfdf5, stop:1 #dcfce7);
            border: none;
            border-bottom: 2px solid #bbf7d0;
            padding: 8px;
            font-weight: 800;
            color: #16a34a;
            border-radius: 6px;
        }

        QTextEdit#log_text_edit {
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            background-color: #ffffff;
            color: #0f172a;
            selection-background-color: #dcfce7;
            selection-color: #166534;
        }

        QProgressBar {
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            text-align: center;
            background-color: #ecfdf5;
            font-size: 15px;
            color: #0f172a;
            font-weight: 800;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4ade80, stop:1 #16a34a);
            border-radius: 8px;
            margin: 1px;
        }

        QMenuBar {
            background-color: #f6fbf8;
            border-bottom: 2px solid #dcfce7;
            font-size: 15px;
            font-weight: 600;
            color: #0f172a;
        }
        QMenuBar::item {
            padding: 8px 18px;
            margin: 2px;
            border-radius: 8px;
            background-color: transparent;
            border: 2px solid transparent;
        }
        QMenuBar::item:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4ade80, stop:1 #22c55e);
            color: #ffffff;
            border-color: #22c55e;
        }
        QMenu {
            background-color: #ffffff;
            border: 2px solid #dcfce7;
            border-radius: 10px;
            padding: 8px 0;
            color: #0f172a;
        }
        QMenu::item {
            padding: 8px 28px;
            margin: 0 4px;
            border-radius: 8px;
            border: 2px solid transparent;
        }
        QMenu::item:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4ade80, stop:1 #22c55e);
            color: #ffffff;
            border-color: #22c55e;
        }
        QMenu::separator { height: 2px; background-color: #dcfce7; margin: 6px 10px; }

        QScrollArea#port_scroll_area { border: none; background-color: transparent; }
        QScrollArea#port_scroll_area QWidget#scroll_content_widget {
            border: 2px solid #dcfce7;
            border-radius: 10px;
            background-color: #ffffff;
            padding: 10px;
        }
        QScrollBar:vertical {
            width: 8px;
            background-color: #ecfdf5;
            border-radius: 4px;
            margin: 0 2px;
        }
        QScrollBar::handle:vertical {
            background-color: #bbf7d0;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background-color: #22c55e; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        
        /* 关于对话框样式 */
        QMessageBox { background-color: white; color: #333333; }
        QMessageBox QLabel { color: #333333; font-weight: normal; }
        QMessageBox QPushButton { 
            background-color: #1f2a44; 
            color: #e5e7eb; 
            border: 2px solid #334155; 
            border-radius: 8px; 
            padding: 6px 12px; 
            font-weight: 600; 
        }
        QMessageBox QPushButton:hover { 
            background-color: #263455; 
            border-color: #60a5fa; 
        }
        """

    def on_about(self):
        QMessageBox.about(self, "关于", "灵巧手自动化测试工具 v1.0\n基于PyQt5开发")
        self.log_text_edit.append(f"[{self.get_time()}] 查看关于信息")

    def update_test_table(self, row, case_id, case_name, status, res):
        # 只更新端口号和测试结果，保留软件版本和设备ID
        self.test_data_table.setItem(row, 0, QTableWidgetItem(case_id))
        # 保留软件版本和设备ID，不更新
        # self.test_data_table.setItem(row, 1, QTableWidgetItem(case_name))
        # self.test_data_table.setItem(row, 2, QTableWidgetItem(status))
        # 更新连接状态为"已连接"
        self.test_data_table.setItem(row, 3, QTableWidgetItem(STATUS_CONNECTED_UI))
        # 更新测试结果
        item = QTableWidgetItem(res)
        if res == RESULT_PASS:
            item.setForeground(QColor(0, 180, 0))
        elif res == RESULT_FAIL:
            item.setForeground(QColor(255, 0, 0))
        else:
            item.setForeground(QColor(200, 160, 0))
        self.test_data_table.setItem(row, 4, item)

    def update_test_result(self, total, success, fail, skip):
        self.total_case_value.setText(f"{total}条")
        self.success_case_value.setText(f"{success}条")
        self.fail_case_value.setText(f"{fail}条")
        self.skip_case_value.setText(f"{skip}条")

    def update_test_data_table(self, port, checked):
        """更新测试数据表格中的端口信息"""
        try:
            # 查找表格中是否已存在该端口的行
            row = -1
            for i in range(self.test_data_table.rowCount()):
                item = self.test_data_table.item(i, 0)
                if item and item.text() == port:
                    row = i
                    break
            
            # 如果不存在，找到第一个空行
            if row == -1:
                for i in range(self.test_data_table.rowCount()):
                    item = self.test_data_table.item(i, 0)
                    if not item or item.text() == "":
                        row = i
                        break
            
            # 如果找到行
            if row != -1:
                if checked:
                    # 端口被勾选，更新信息
                    self.test_data_table.setItem(row, 0, QTableWidgetItem(port))

                    # 恢复需求：勾选端口时同步读取软件版本和设备ID。
                    # 正确调用：使用 rohand_manager.py 的 get_device_info()（内部会扫描有效ID并读取固件版本）。
                    software_version = "-"
                    device_id = "-"
                    connect_status = STATUS_NOT_CONNECTED

                    rohan_manager = None
                    try:
                        # 统一从全局管理器获取，避免重复创建实例
                        rohan_manager = self._get_manager()
                        if rohan_manager.create_client(port):
                            info = rohan_manager.get_device_info(port)
                            if info:
                                software_version = str(info.get(COL_SOFTWARE_VERSION, "-"))
                                device_id = str(info.get(COL_DEVICE_ID, "-"))
                                connect_status = str(info.get(COL_CONNECT_STATUS, STATUS_CONNECTED_UI))
                            else:
                                # 兜底：如果 get_device_info 扫描不到设备，直接用默认节点ID读取固件版本
                                try:
                                    node_id = getattr(rohan_manager, "node_id", 2)
                                    sw = rohan_manager.get_firmware_version(node_id)
                                    if sw and "无法获取" not in sw:
                                        software_version = str(sw)
                                        device_id = str(node_id)
                                        connect_status = STATUS_CONNECTED_UI
                                    else:
                                        connect_status = STATUS_UNKNOWN_DEVICE
                                except Exception as inner_e:
                                    self.log_text_edit.append(
                                        f"[{self.get_time()}] 使用默认节点读取固件版本失败：{str(inner_e)}"
                                    )
                                    connect_status = STATUS_UNKNOWN_DEVICE
                    except Exception as e:
                        self.log_text_edit.append(f"[{self.get_time()}] 读取设备信息失败：{str(e)}")
                        connect_status = STATUS_READ_FAIL
                    finally:
                        try:
                            if rohan_manager and getattr(rohan_manager, "client", None):
                                rohan_manager.client.disconnect()
                        except Exception:
                            pass

                    self.test_data_table.setItem(row, 1, QTableWidgetItem(software_version))
                    self.test_data_table.setItem(row, 2, QTableWidgetItem(device_id))
                    self.test_data_table.setItem(row, 3, QTableWidgetItem(connect_status))
                    self.test_data_table.setItem(row, 4, QTableWidgetItem(""))  # 测试结果为空
                else:
                    # 端口被取消勾选，清空信息
                    self.test_data_table.setItem(row, 0, QTableWidgetItem(""))
                    self.test_data_table.setItem(row, 1, QTableWidgetItem(""))
                    self.test_data_table.setItem(row, 2, QTableWidgetItem(""))
                    self.test_data_table.setItem(row, 3, QTableWidgetItem(""))
                    self.test_data_table.setItem(row, 4, QTableWidgetItem(""))
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 更新测试数据表格失败：{str(e)}")

    @staticmethod
    def get_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _load_protocol_from_config_file(self):
        """从 config.ini 读取协议并同步全局 RohanManager。"""
        self.protocol_type = RohanManager.read_protocol_type_from_config(self._config_path)
        RohanManager.ensure_global(self.protocol_type)

    def _get_manager(self, refresh_protocol: bool = False):
        """统一获取全局 manager，必要时先从配置刷新协议。"""
        if refresh_protocol:
            self._load_protocol_from_config_file()
        return RohanManager.ensure_global(self.protocol_type)

    def _attach_project_log_handler(self):
        if not hasattr(self, "log_text_edit"):
            return

        handler = GuiLogHandler(self.log_text_edit.append)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        handler.addFilter(RoHandGuiLogFilter())

        root_logger = logging.getLogger()
        for h in root_logger.handlers:
            if getattr(h, "_is_rohand_gui_handler", False):
                return
        root_logger.addHandler(handler)

    def closeEvent(self, event):
        if self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        RohanManager.release_global()
        event.accept()

    def _restart_application(self):
        """重启整个客户端进程，用于配置文件修改后生效。"""
        try:
            python = sys.executable or "python"
            script = os.path.abspath(sys.argv[0])
            import subprocess
            subprocess.Popen([python, script])
        except Exception as e:
            self.log_text_edit.append(f"[{self.get_time()}] 重启应用失败：{e}")
        finally:
            QApplication.instance().quit()


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