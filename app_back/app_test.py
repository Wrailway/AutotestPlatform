"""
@File    : app_test.py
@Author  : 梁宗豪 (Optimized Version)
@Date    : 2026-03-05
@Version : 1.0.0
@Desc    : APP自动化测试业务控制层 (Controller)
           采用 Pytest Collector 精准收集用例，NodeID 映射更新状态，支持富文本日志渲染。
"""
import os
import sys
import time
from typing import Dict, List, Optional
import importlib

import pytest
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox

# 导入UI编译生成的模块
from app.app_test_ui import Ui_AppTestWindow

# 热重载辅助函数
def _clear_module_cache(script_path: str):
    """
    清理 sys.modules 中与测试脚本同目录的用户自定义模块缓存。
    确保每次运行都能加载到最新的外部修改。
    """
    script_dir = os.path.dirname(os.path.abspath(script_path))
    modules_to_delete = []

    # 遍历当前已加载的所有模块
    for mod_name, mod in list(sys.modules.items()):
        try:
            # 如果模块拥有物理路径，并且该路径在我们的测试脚本目录下，则将其判定为需要热重载的文件
            if hasattr(mod, '__file__') and mod.__file__:
                if mod.__file__.startswith(script_dir):
                    modules_to_delete.append(mod_name)
        except Exception:
            continue

    # 从系统缓存中将其剔除
    for mod_name in modules_to_delete:
        del sys.modules[mod_name]


class PytestCollectPlugin:
    """拦截 Pytest 收集阶段，提取真实的测试用例列表"""
    def __init__(self):
        self.collected_items: List[dict] = []

    def pytest_collection_modifyitems(self, session, config, items):
        """Hook: 在用例收集完成后触发"""
        for item in items:
            # 优先获取 docstring，如果没有则使用用例函数名
            doc = item.obj.__doc__.strip() if item.obj.__doc__ else item.name
            self.collected_items.append({
                "nodeid": item.nodeid,  # 唯一标识符
                "name": doc
            })


class TestCollectorThread(QThread):
    """后台异步收集测试用例的线程"""
    sig_collected = pyqtSignal(list)
    sig_error = pyqtSignal(str)

    def __init__(self, script_path: str, parent=None):
        super().__init__(parent)
        # 保存脚本路径，供后续热重载使用
        self.script_path = script_path

    def run(self):
        try:
            plugin = PytestCollectPlugin()

            # 清理 Python 内部缓存，强制重新读取磁盘文件
            importlib.invalidate_caches()
            _clear_module_cache(self.script_path)

            # 添加 --import-mode=importlib 参数，防止 pytest 污染 sys.modules
            pytest.main([
                "--collect-only",
                "-q",
                "--import-mode=importlib",  # 强制 Pytest 每次动态加载模块
                self.script_path
            ], plugins=[plugin])

            # 收集完成后发送信号，传递用例列表
            self.sig_collected.emit(plugin.collected_items)
        except Exception as e:
            self.sig_error.emit(str(e))


class PytestRunnerPlugin:
    """自定义 Pytest 执行插件，基于 NodeID 精准同步状态"""
    def __init__(self, log_signal: pyqtSignal, status_signal: pyqtSignal, node_mapping: Dict[str, int]):
        self.log_signal = log_signal
        self.status_signal = status_signal
        self.node_mapping = node_mapping

    @pytest.fixture
    def logger(self):
        """向测试脚本注入的 logger fixture"""
        def _logger(msg: str):
            # 发送普通业务日志
            self.log_signal.emit({"level": "info", "msg": str(msg)})
        return _logger

    def pytest_runtest_setup(self, item):
        """Hook: 用例执行前准备"""
        row = self.node_mapping.get(item.nodeid)
        if row is not None:
            self.log_signal.emit({"level": "sys", "msg": f"开始执行用例: {item.name}"})
            self.status_signal.emit(row, "RUNNING")

    def pytest_runtest_logreport(self, report):
        """Hook: 捕获测试结果"""
        row = self.node_mapping.get(report.nodeid)
        if row is None:
            return

        # 优先处理跳过的情况，避免后续状态覆盖
        if report.skipped:
            self.status_signal.emit(row, "SKIP")
            # 尝试提取跳过的原因
            reason = "条件跳过"
            if hasattr(report, 'wasxfail'):
                reason = f"预期失败: {report.wasxfail}"
            elif isinstance(report.longrepr, tuple):
                reason = report.longrepr[2]
            elif hasattr(report.longrepr, 'reprcrash'):
                reason = report.longrepr.reprcrash.message
            elif report.longreprtext:
                reason = report.longreprtext.splitlines()[-1]
            self.log_signal.emit({"level": "skip", "msg": f"用例已跳过: {report.nodeid} [原因: {reason}]"})
            return

        if report.when == 'call':
            if report.passed:
                self.status_signal.emit(row, "PASS")
                self.log_signal.emit({"level": "success", "msg": f"用例执行通过: {report.nodeid}"})
            elif report.failed:
                self.status_signal.emit(row, "FAIL")
                err_msg = report.longreprtext.splitlines()[-1] if report.longreprtext else "未知错误"
                self.log_signal.emit({"level": "error", "msg": f"用例执行失败: {err_msg}"})

        elif report.when == 'setup' and report.failed:
            self.status_signal.emit(row, "FAIL")
            self.log_signal.emit({"level": "error", "msg": f"用例前置 Setup 失败: {report.nodeid}"})

        elif report.when == 'teardown' and report.failed:
            self.status_signal.emit(row, "FAIL")
            self.log_signal.emit({"level": "error", "msg": f"用例后置 Teardown 失败: {report.nodeid}"})


class TestRunnerThread(QThread):
    """后台异步执行测试用例的线程"""
    sig_log = pyqtSignal(dict)           # 字典结构：{"level": "sys", "msg": "..."}
    sig_status = pyqtSignal(int, str)    # 行号, 状态
    sig_finished = pyqtSignal()

    def __init__(self, script_path: str, node_mapping: Dict[str, int], parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.node_mapping = node_mapping

    def run(self):
        # 清理 Python 内部缓存
        importlib.invalidate_caches()
        _clear_module_cache(self.script_path)

        plugin = PytestRunnerPlugin(self.sig_log, self.sig_status, self.node_mapping)
        # 同样添加 --import-mode=importlib 参数
        pytest.main([
            "-q",
            "--import-mode=importlib",
            self.script_path
        ], plugins=[plugin])

        self.sig_finished.emit()


class AppTestWindow(QMainWindow, Ui_AppTestWindow):
    """APP 自动化测试业务主窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 实例变量初始化
        self.current_script_path: Optional[str] = None
        self.case_node_mapping: Dict[str, int] = {}  # 核心：保存 nodeid 和行号的映射关系

        self.executed_cases_count: int = 0  # 在初始化时，增加已执行用例数量的变量

        # 线程占位符
        self.collector_thread: Optional[TestCollectorThread] = None
        self.runner_thread: Optional[TestRunnerThread] = None

        # 绑定信号槽
        self.actionLoadScript.triggered.connect(self.on_load_script)
        self.start_btn.clicked.connect(self.run_cases)

    def on_load_script(self):
        """选择脚本并启动后台收集"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择测试脚本", os.getcwd(), "Python Scripts (*.py);"
        )
        if not file_path:
            return

        self.current_script_path = file_path
        self.log_message({"level": "sys", "msg": f"正在深度解析脚本：{file_path} ..."})

        # 禁用 UI，等待收集完成
        self.start_btn.setEnabled(False)
        self.case_table.setRowCount(0)
        self.case_node_mapping.clear()

        # 启动后台收集线程 (防止大文件导致 UI 卡顿)
        self.collector_thread = TestCollectorThread(file_path)
        self.collector_thread.sig_collected.connect(self.render_cases_to_table)
        self.collector_thread.sig_error.connect(
            lambda err: self.log_message({"level": "error", "msg": f"解析失败: {err}"})
        )
        self.collector_thread.start()

    def render_cases_to_table(self, collected_items: List[dict]):
        """将收集到的用例渲染到 TableWidget"""
        cases_count = len(collected_items)
        if cases_count == 0:
            self.log_message({"level": "error", "msg": "未在脚本中发现有效的测试用例！"})
            self.start_btn.setEnabled(True)
            return

        for row_index, item in enumerate(collected_items):
            self.case_table.insertRow(row_index)
            # 记录映射关系，供执行器定位行号
            self.case_node_mapping[item["nodeid"]] = row_index

            # ID 列
            id_item = QTableWidgetItem(str(row_index + 1))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.case_table.setItem(row_index, 0, id_item)

            # 名称/描述 列
            name_item = QTableWidgetItem(item["name"])
            name_item.setToolTip(item["nodeid"])  # 鼠标悬停显示完整 nodeid
            self.case_table.setItem(row_index, 1, name_item)

            # 状态 列
            status_item = QTableWidgetItem("待执行(Pending)")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QtGui.QBrush(QtGui.QColor("#909399")))
            self.case_table.setItem(row_index, 2, status_item)

        # 更新仪表盘与UI状态
        self.stat_num_total.setText(str(cases_count))
        self.stat_num_pass.setText("0")
        self.stat_num_fail.setText("0")
        self.stat_num_skip.setText("0") # 重置跳过数据
        self.progressBar.setValue(0)
        self.label_status.setText("就绪")

        self.start_btn.setEnabled(True)
        self.log_message({"level": "success", "msg": f"脚本加载完毕，共发现 {cases_count} 个测试用例。"})

    def run_cases(self):
        """启动测试执行引擎"""
        if not self.current_script_path or self.case_table.rowCount() == 0:
            QMessageBox.warning(self, "提示", "请先加载包含用例的测试脚本！")
            return

        # UI 状态初始化
        self.start_btn.setEnabled(False)
        self.start_btn.setText("测试执行中...")
        self.stat_num_pass.setText("0")
        self.stat_num_fail.setText("0")
        self.stat_num_skip.setText("0") # 重置跳过数据
        self.progressBar.setValue(0)
        self.label_status.setText("执行中...")

        self.log_message({"level": "sys", "msg": "🚀 自动化测试任务正式启动！"})

        # 每次点击执行时，将执行计数器归零
        self.executed_cases_count = 0

        # 启动执行线程，并传入映射字典
        self.runner_thread = TestRunnerThread(self.current_script_path, self.case_node_mapping)
        self.runner_thread.sig_log.connect(self.log_message)
        self.runner_thread.sig_status.connect(self.update_case_status)
        self.runner_thread.sig_finished.connect(self.on_test_finished)
        self.runner_thread.start()

    def update_case_status(self, row: int, status: str):
        """精准更新指定行的状态 (线程安全)"""
        if row >= self.case_table.rowCount():
            return

        item = self.case_table.item(row, 2)
        total_cases = self.case_table.rowCount()

        if status == "RUNNING":
            item.setText("执行中...")
            item.setForeground(QtGui.QBrush(QtGui.QColor("#E6A23C"))) # 橙色
            self.case_table.selectRow(row)  # 自动高亮当前行

        elif status == "PASS":
            item.setText("通过 (PASS)")
            item.setForeground(QtGui.QBrush(QtGui.QColor("#67C23A"))) # 绿色
            self.stat_num_pass.setText(str(int(self.stat_num_pass.text()) + 1))

        elif status == "FAIL":
            item.setText("失败 (FAIL)")
            item.setForeground(QtGui.QBrush(QtGui.QColor("#F56C6C"))) # 红色
            self.stat_num_fail.setText(str(int(self.stat_num_fail.text()) + 1))

        elif status == "SKIP":
            item.setText("跳过 (SKIP)")
            item.setForeground(QtGui.QBrush(QtGui.QColor("#E6A23C"))) # 橙色
            self.stat_num_skip.setText(str(int(self.stat_num_skip.text()) + 1))

        # 只有在 PASS/FAIL/SKIP 状态下才增加已执行用例计数，确保进度条准确反映实际执行进度
        if status in ["PASS", "FAIL", "SKIP"]:
            self.executed_cases_count += 1
            self.progressBar.setValue(int((self.executed_cases_count / total_cases) * 100))

    def on_test_finished(self):
        """测试结束清理与提示"""
        self.start_btn.setEnabled(True)
        self.start_btn.setText(" 开始测试")
        self.label_status.setText("执行完毕")
        self.progressBar.setValue(100) # 确保进度条走满

        self.log_message({"level": "sys", "msg": "✅ 自动化测试任务执行完毕！"})

    def log_message(self, log_data: dict):
        """
        支持 HTML 富文本的高级日志渲染器
        :param log_data: dict, 例: {"level": "error", "msg": "崩溃了"}
        """
        level = log_data.get("level", "info")
        msg = log_data.get("msg", "")
        timestamp = time.strftime("%H:%M:%S", time.localtime())

        # 颜色主题配置 (类似于前端的 Element UI 色系)
        color_map = {
            "sys": "#409EFF",     # 蓝色 (系统级提示)
            "success": "#67C23A", # 绿色 (成功)
            "error": "#F56C6C",   # 红色 (失败/异常)
            "skip": "#E6A23C",    # 橙色 (跳过/警告)
            "info": "#606266"     # 灰色 (常规输出)
        }
        color = color_map.get(level, "#000000")

        # 组装 HTML 富文本
        html_msg = f'<span style="color: #909399;">[{timestamp}]</span> <span style="color: {color};">{msg}</span>'
        self.log_text.append(html_msg)

        # 自动滚动至底部
        if self.chk_auto_scroll.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            self.log_text.setTextCursor(cursor)