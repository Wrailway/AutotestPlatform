import sys
import time
import json
import re
import csv
import random
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout,
QLineEdit, QSpinBox, QProgressBar, QLabel, QPushButton,
QPlainTextEdit, QFileDialog, QHeaderView, QMessageBox,
QMenuBar, QAction, QComboBox, QTabWidget, QCheckBox,
QSplitter, QDialog, QListWidget, QListWidgetItem, QDialogButtonBox,
QTreeWidget, QTreeWidgetItem, QSizePolicy, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QMargins
from PyQt5.QtGui import QFont, QClipboard, QColor, QPalette, QBrush, QIcon


# ------------------------------ 全局样式配置 ------------------------------
class ModernStyle:
    """UI样式常量"""
    # 颜色方案（莫兰迪色系）
    PRIMARY_COLOR = "#2563eb"  # 主色调-蓝
    SECONDARY_COLOR = "#4f46e5"  # 辅助色-紫蓝
    SUCCESS_COLOR = "#10b981"  # 成功色-绿
    DANGER_COLOR = "#ef4444"  # 危险色-红
    WARNING_COLOR = "#f59e0b"  # 警告色-黄
    INFO_COLOR = "#3b82f6"  # 信息色-浅蓝
    BG_COLOR = "#f8fafc"  # 背景色
    PANEL_BG = "#ffffff"  # 面板背景
    TEXT_PRIMARY = "#1e293b"  # 主要文本
    TEXT_SECONDARY = "#64748b"  # 次要文本
    BORDER_COLOR = "#e2e8f0"  # 边框色
    HOVER_COLOR = "#f1f5f9"  # 悬停色
    # 滚动条颜色
    SCROLL_BAR_BG = "#f1f5f9"  # 滚动条背景
    SCROLL_BAR_HANDLE = "#e2e8f0"  # 滚动条滑块
    SCROLL_BAR_HOVER = "#cbd5e1"  # 滚动条悬停
    SCROLL_BAR_PRESS = "#94a3b8"  # 滚动条按下
    # 圆角与阴影
    BORDER_RADIUS = "8px"
    SHADOW_EFFECT = "0px 2px 8px rgba(0,0,0,0.08)"
    # 字体配置
    FONT_MAIN = "Microsoft YaHei UI"
    FONT_MONO = "Consolas"
    FONT_SIZE_BASE = 9
    FONT_SIZE_SMALL = 8
    FONT_SIZE_LARGE = 10

    @classmethod
    def get_global_style(cls):
        return f"""
            /* ========== 基础样式 ========== */
            QWidget {{
                background-color: {cls.BG_COLOR};
                color: {cls.TEXT_PRIMARY};
                font-family: {cls.FONT_MAIN};
                font-size: {cls.FONT_SIZE_BASE}pt;
            }}
            QMainWindow {{
                background-color: {cls.BG_COLOR};
            }}
            /* ========== 面板容器 ========== */
            QGroupBox {{
                background-color: {cls.PANEL_BG};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.BORDER_RADIUS};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: 600;
                color: {cls.TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {cls.PRIMARY_COLOR};
            }}
            /* ========== 按钮样式 ========== */
            QPushButton {{
                background-color: {cls.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: {cls.BORDER_RADIUS};
                padding: 8px 16px;
                font-weight: 600;
                min-height: 36px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {cls.SECONDARY_COLOR};
            }}
            QPushButton:pressed {{
                background-color: #1d4ed8;
            }}
            QPushButton:disabled {{
                background-color: {cls.TEXT_SECONDARY};
                opacity: 0.6;
            }}
            /* 开始按钮 - 绿色 */
            QPushButton#btnStart {{
                background-color: {cls.SUCCESS_COLOR};
            }}
            QPushButton#btnStart:hover {{
                background-color: #0da271;
            }}
            QPushButton#btnStart:pressed {{
                background-color: #0c9969;
            }}
            /* 暂停按钮 - 黄色 */
            QPushButton#btnPause {{
                background-color: {cls.WARNING_COLOR};
            }}
            QPushButton#btnPause:hover {{
                background-color: #e69500;
            }}
            QPushButton#btnPause:pressed {{
                background-color: #d68900;
            }}
            /* 停止按钮 - 红色 */
            QPushButton#btnStop {{
                background-color: {cls.DANGER_COLOR};
            }}
            QPushButton#btnStop:hover {{
                background-color: #dc2626;
            }}
            QPushButton#btnStop:pressed {{
                background-color: #c7221f;
            }}
            /* 工具按钮 */
            QPushButton#btnTool {{
                background-color: {cls.PANEL_BG};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER_COLOR};
                padding: 4px 8px;
                min-height: 24px;
                min-width: 80px;
            }}
            /* ========== 输入框/文本框 ========== */
            QLineEdit, QPlainTextEdit, QSpinBox, QComboBox {{
                background-color: {cls.PANEL_BG};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.BORDER_RADIUS};
                padding: 6px 8px;
                selection-background-color: {cls.INFO_COLOR};
                selection-color: white;
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border: 1px solid {cls.PRIMARY_COLOR};
                outline: none;
            }}
            /* ========== 下拉框 ========== */
            QComboBox {{
                min-height: 32px;
                padding-right: 20px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
            QComboBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {cls.PRIMARY_COLOR};
                margin-right: 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {cls.PANEL_BG};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.BORDER_RADIUS};
                selection-background-color: {cls.HOVER_COLOR};
                selection-color: {cls.PRIMARY_COLOR};
            }}
            /* ========== 数字输入框（SpinBox）箭头美化 ========== */
            QSpinBox {{
                padding-right: 28px;
                min-height: 32px;
                border: 1px solid {ModernStyle.BORDER_COLOR};
                border-radius: {ModernStyle.BORDER_RADIUS};
                background-color: {ModernStyle.PANEL_BG};
            }}
            QSpinBox:focus {{
                border: 1px solid {ModernStyle.PRIMARY_COLOR};
            }}
            /* 上下按钮区域 */
            QSpinBox::up-button {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                height: 16px;
                background-color: transparent;
                border: none;
                margin-right: 2px;
                margin-top: 2px;
            }}
            QSpinBox::down-button {{
                subcontrol-origin: padding;
                subcontrol-position: bottom right;
                width: 20px;
                height: 16px;
                background-color: transparent;
                border: none;
                margin-right: 2px;
                margin-bottom: 2px;
            }}
            /* 上箭头 */
            QSpinBox::up-arrow {{
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid {ModernStyle.PRIMARY_COLOR};
                margin: 4px;
            }}
            /* 下箭头 */
            QSpinBox::down-arrow {{
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {ModernStyle.PRIMARY_COLOR};
                margin: 4px;
            }}
            /* 箭头悬停效果 */
            QSpinBox::up-button:hover {{
                background-color: {ModernStyle.HOVER_COLOR};
                border-radius: 2px;
            }}
            QSpinBox::down-button:hover {{
                background-color: {ModernStyle.HOVER_COLOR};
                border-radius: 2px;
            }}
            QSpinBox::up-button:hover QSpinBox::up-arrow {{
                border-bottom-color: {ModernStyle.SECONDARY_COLOR};
            }}
            QSpinBox::down-button:hover QSpinBox::down-arrow {{
                border-top-color: {ModernStyle.SECONDARY_COLOR};
            }}
            /* 按下效果 */
            QSpinBox::up-button:pressed {{
                background-color: {ModernStyle.BORDER_COLOR};
            }}
            QSpinBox::down-button:pressed {{
                background-color: {ModernStyle.BORDER_COLOR};
            }}
            /* ========== 表格控件（核心优化） ========== */
            QTableWidget {{
                background-color: {cls.PANEL_BG};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.BORDER_RADIUS};
                gridline-color: {cls.BORDER_COLOR};
                alternate-background-color: {cls.HOVER_COLOR};
            }}
            QTableWidget::item {{
                padding: 8px 4px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {cls.INFO_COLOR};
                color: white;
            }}
            /* 水平表头（保留） */
            QTableWidget::horizontalHeader {{
                background-color: {cls.HOVER_COLOR};
                border: none;
            }}
            QTableWidget::horizontalHeader::section {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {cls.BORDER_COLOR};
                padding: 8px 6px;
                font-weight: 600;
                color: {cls.TEXT_PRIMARY};
            }}
            /* 垂直表头（自动序号）：直接隐藏 */
            QTableWidget::verticalHeader {{
                border: none;
            }}
            /* ========== 滚动条美化 ========== */
            QScrollBar:vertical {{
                background-color: {cls.SCROLL_BAR_BG};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {cls.SCROLL_BAR_HANDLE};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.SCROLL_BAR_HOVER};
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: {cls.SCROLL_BAR_PRESS};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                width: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background-color: transparent;
            }}
            QScrollBar:horizontal {{
                background-color: {cls.SCROLL_BAR_BG};
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {cls.SCROLL_BAR_HANDLE};
                min-width: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {cls.SCROLL_BAR_HOVER};
            }}
            QScrollBar::handle:horizontal:pressed {{
                background-color: {cls.SCROLL_BAR_PRESS};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                height: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background-color: transparent;
            }}
            QPlainTextEdit QScrollBar:vertical {{
                width: 6px;
            }}
            QTableWidget QScrollBar:vertical {{
                width: 6px;
            }}
            /* ========== 进度条 ========== */
            QProgressBar {{
                background-color: {cls.HOVER_COLOR};
                border: none;
                border-radius: 10px;
                text-align: center;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {cls.PRIMARY_COLOR};
                border-radius: 8px;
            }}
            /* ========== 菜单栏 ========== */
            QMenuBar {{
                background-color: {cls.PANEL_BG};
                border-bottom: 1px solid {cls.BORDER_COLOR};
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {cls.HOVER_COLOR};
                color: {cls.PRIMARY_COLOR};
            }}
            QMenu {{
                background-color: {cls.PANEL_BG};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.BORDER_RADIUS};
            }}
            QMenu::item:selected {{
                background-color: {cls.HOVER_COLOR};
                color: {cls.PRIMARY_COLOR};
            }}
        """


# ------------------------------ 测试执行核心线程 ------------------------------
class TestWorker(QThread):
    update_progress = pyqtSignal(int, str)  # 进度，状态
    update_result = pyqtSignal(int, str)  # 用例编号，结果
    update_stats = pyqtSignal(dict)  # 统计信息
    log_message = pyqtSignal(str)  # 日志消息

    def __init__(self, test_cases, params):
        super().__init__()
        self.test_cases = test_cases
        self.params = params
        self.is_running = True
        self.is_paused = False

    def run(self):
        total_cases = len(self.test_cases)
        success = 0
        failure = 0
        start_time = time.time()

        for i, test_case in enumerate(self.test_cases):
            # 检查是否暂停
            while self.is_paused and self.is_running:
                self.sleep(0.1)
            # 检查是否停止
            if not self.is_running:
                break
            # 模拟测试执行
            self.log_message.emit(f"开始执行测试用例 {test_case['id']}: {test_case['description']}")
            # 模拟测试执行时间
            execution_time = random.uniform(0.5, 2.0)
            self.msleep(int(execution_time * 1000))
            # 随机生成测试结果（模拟）
            result = random.choices(["成功", "失败"], weights=[0.8, 0.2])[0]
            # 更新结果
            self.update_result.emit(test_case['id'], result)
            if result == "成功":
                success += 1
            else:
                failure += 1
            # 更新进度
            progress = int((i + 1) / total_cases * 100)
            self.update_progress.emit(progress, f"正在执行: {test_case['description']}")
            # 更新统计信息
            elapsed_time = time.time() - start_time
            stats = {
                'total': total_cases,
                'success': success,
                'failure': failure,
                'pass_rate': success / (i + 1) * 100 if (i + 1) > 0 else 0,
                'elapsed_time': elapsed_time
            }
            self.update_stats.emit(stats)
            # 模拟间隔停顿
            if 'interval' in self.params and i < total_cases - 1:
                self.msleep(int(self.params['interval'] * 1000))
        # 测试完成
        elapsed_time = time.time() - start_time
        self.log_message.emit(f"测试执行完成，总耗时: {elapsed_time:.2f}秒")
        self.update_progress.emit(100, "测试完成")


# ------------------------------ 主界面类 ------------------------------
class ServerTestTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.test_worker = None
        self.test_cases = []
        self.init_ui()
        self.init_test_cases()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle("服务器测试自动化工具 v1.0")
        self.resize(1600, 900)
        self.setStyleSheet(ModernStyle.get_global_style())
        # 创建菜单栏
        self.create_menu_bar()
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ====================== 主体三栏布局 ======================
        body_splitter = QSplitter(Qt.Horizontal)
        body_splitter.setStyleSheet(f"QSplitter::handle{{width: 2px; background-color: {ModernStyle.BORDER_COLOR};}}")

        # 左侧：测试用例表格（核心修改：保留表格，隐藏自动序号）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        left_header = QLabel("📋 测试用例")
        left_header.setStyleSheet(f"""
            font-size: 11pt; font-weight: 600; color: {ModernStyle.PRIMARY_COLOR};
            padding: 8px; border-bottom: 1px solid {ModernStyle.BORDER_COLOR};
        """)
        left_layout.addWidget(left_header)

        # ========== 核心修改1：表格初始化，隐藏自动序号 ==========
        self.case_table = QTableWidget()
        self.case_table.setColumnCount(3)  # 3列：编号、用例描述、执行结果
        self.case_table.setHorizontalHeaderLabels(["编号", "用例描述", "执行结果"])
        # 关键：隐藏垂直表头（自带的自动行号/序号）
        self.case_table.verticalHeader().setVisible(False)
        # 表格列宽适配优化
        self.case_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.case_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.case_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # 隔行变色、禁止编辑
        self.case_table.setAlternatingRowColors(True)
        self.case_table.setEditTriggers(QTableWidget.NoEditTriggers)
        left_layout.addWidget(self.case_table, stretch=1)
        left_panel.setMinimumWidth(400)
        body_splitter.addWidget(left_panel)

        # 中间：操作日志面板
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        center_header = QLabel("📝 操作日志")
        center_header.setStyleSheet(f"""
            font-size: 11pt; font-weight: 600; color: {ModernStyle.PRIMARY_COLOR};
            padding: 8px; border-bottom: 1px solid {ModernStyle.BORDER_COLOR};
        """)
        center_layout.addWidget(center_header)

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont(ModernStyle.FONT_MONO, 9))
        center_layout.addWidget(self.log_text, stretch=1)

        # 日志操作按钮
        log_buttons_layout = QHBoxLayout()
        self.btn_save_log = QPushButton("保存日志")
        self.btn_save_log.setObjectName("btnTool")
        self.btn_save_log.clicked.connect(self.save_log)
        self.btn_clear_log = QPushButton("清空日志")
        self.btn_clear_log.setObjectName("btnTool")
        self.btn_clear_log.clicked.connect(self.clear_log)
        log_buttons_layout.addWidget(self.btn_save_log)
        log_buttons_layout.addWidget(self.btn_clear_log)
        log_buttons_layout.addStretch()
        center_layout.addLayout(log_buttons_layout)
        body_splitter.addWidget(center_panel)

        # 右侧：设置和统计面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        right_header = QLabel("⚙️ 测试配置")
        right_header.setStyleSheet(f"""
            font-size: 11pt; font-weight: 600; color: {ModernStyle.PRIMARY_COLOR};
            padding: 8px; border-bottom: 1px solid {ModernStyle.BORDER_COLOR};
        """)
        right_layout.addWidget(right_header)

        # 测试配置标签页
        self.config_tab = QTabWidget()
        # 功能测试配置
        function_widget = QWidget()
        function_layout = QFormLayout(function_widget)
        function_layout.setContentsMargins(10, 10, 10, 10)
        function_layout.setSpacing(10)
        self.loop_spin = QSpinBox()
        self.loop_spin.setRange(1, 1000)
        self.loop_spin.setValue(1)
        self.loop_spin.setSuffix(" 次")
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 100)
        self.thread_spin.setValue(1)
        self.thread_spin.setSuffix(" 线程")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 60)
        self.interval_spin.setValue(1)
        self.interval_spin.setSuffix(" 秒")
        function_layout.addRow("循环次数:", self.loop_spin)
        function_layout.addRow("线程数:", self.thread_spin)
        function_layout.addRow("间隔停顿:", self.interval_spin)
        self.config_tab.addTab(function_widget, "功能测试")

        # 性能测试配置
        performance_widget = QWidget()
        performance_layout = QFormLayout(performance_widget)
        performance_layout.setContentsMargins(10, 10, 10, 10)
        performance_layout.setSpacing(10)
        self.user_spin = QSpinBox()
        self.user_spin.setRange(1, 1000)
        self.user_spin.setValue(10)
        self.user_spin.setSuffix(" 用户")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 600)
        self.duration_spin.setValue(10)
        self.duration_spin.setSuffix(" 分钟")
        self.ramp_spin = QSpinBox()
        self.ramp_spin.setRange(0, 600)
        self.ramp_spin.setValue(30)
        self.ramp_spin.setSuffix(" 秒")
        performance_layout.addRow("并发用户数:", self.user_spin)
        performance_layout.addRow("运行时间:", self.duration_spin)
        performance_layout.addRow("爬坡时间:", self.ramp_spin)
        self.config_tab.addTab(performance_widget, "性能测试")
        right_layout.addWidget(self.config_tab)

        # 实时统计
        stats_group = QGroupBox("📊 实时统计")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setContentsMargins(15, 20, 15, 20)
        stats_layout.setSpacing(10)
        # 统计标签
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ModernStyle.PRIMARY_COLOR};")
        self.success_label = QLabel("0")
        self.success_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ModernStyle.SUCCESS_COLOR};")
        self.failure_label = QLabel("0")
        self.failure_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ModernStyle.DANGER_COLOR};")
        self.pass_rate_label = QLabel("0%")
        self.pass_rate_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ModernStyle.PRIMARY_COLOR};")
        self.runtime_label = QLabel("0秒")
        self.runtime_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {ModernStyle.INFO_COLOR};")
        stats_layout.addWidget(QLabel("总用例:"), 0, 0)
        stats_layout.addWidget(self.total_label, 0, 1)
        stats_layout.addWidget(QLabel("成功:"), 1, 0)
        stats_layout.addWidget(self.success_label, 1, 1)
        stats_layout.addWidget(QLabel("失败:"), 2, 0)
        stats_layout.addWidget(self.failure_label, 2, 1)
        stats_layout.addWidget(QLabel("通过率:"), 3, 0)
        stats_layout.addWidget(self.pass_rate_label, 3, 1)
        stats_layout.addWidget(QLabel("运行时长:"), 4, 0)
        stats_layout.addWidget(self.runtime_label, 4, 1)
        right_layout.addWidget(stats_group, stretch=1)
        right_panel.setMinimumWidth(380)
        body_splitter.addWidget(right_panel)

        body_splitter.setStretchFactor(0, 1)
        body_splitter.setStretchFactor(1, 2)
        body_splitter.setStretchFactor(2, 1)
        main_layout.addWidget(body_splitter, stretch=1)

        # ====================== 底部进度和状态栏 ======================
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setSpacing(8)
        # 状态和进度条
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"font-weight: 600; color: {ModernStyle.TEXT_PRIMARY}; padding: 0 10px;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("执行进度: %p%")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar, stretch=1)
        bottom_layout.addLayout(status_layout)

        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.addStretch()
        self.btn_start = QPushButton("▶️ 开始测试")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setMinimumHeight(40)
        self.btn_start.clicked.connect(self.start_test)
        self.btn_pause = QPushButton("⏸️ 暂停")
        self.btn_pause.setObjectName("btnPause")
        self.btn_pause.setMinimumHeight(40)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.pause_test)
        self.btn_stop = QPushButton("⏹️ 停止")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_test)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addStretch()
        bottom_layout.addLayout(btn_layout)
        main_layout.addWidget(bottom_widget)

    def create_menu_bar(self):
        menubar = self.menuBar()
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        load_script_action = QAction("脚本加载(&L)", self)
        load_script_action.setShortcut("Ctrl+L")
        load_script_action.triggered.connect(self.load_script)
        file_menu.addAction(load_script_action)
        output_report_action = QAction("输出报告(&R)", self)
        output_report_action.setShortcut("Ctrl+R")
        output_report_action.triggered.connect(self.output_report)
        file_menu.addAction(output_report_action)
        file_menu.addSeparator()
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # 配置菜单
        config_menu = menubar.addMenu("配置(&C)")
        open_config_action = QAction("打开配置文件(&O)", self)
        open_config_action.triggered.connect(self.open_config)
        config_menu.addAction(open_config_action)
        # 选项菜单
        option_menu = menubar.addMenu("选项(&O)")
        theme_action = QAction("主题切换(&T)", self)
        theme_action.triggered.connect(self.toggle_theme)
        option_menu.addAction(theme_action)
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        about_action = QAction("版权及版本信息(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def init_test_cases(self):
        # 初始化测试用例
        test_cases = [
            {"id": 1, "description": "服务器连接测试", "result": "未执行"},
            {"id": 2, "description": "用户登录验证", "result": "未执行"},
            {"id": 3, "description": "数据查询测试", "result": "未执行"},
            {"id": 4, "description": "文件上传测试", "result": "未执行"},
            {"id": 5, "description": "数据库连接测试", "result": "未执行"},
            {"id": 6, "description": "API接口测试", "result": "未执行"},
            {"id": 7, "description": "压力测试", "result": "未执行"},
            {"id": 8, "description": "并发测试", "result": "未执行"},
            {"id": 9, "description": "安全性测试", "result": "未执行"},
            {"id": 10, "description": "性能基准测试", "result": "未执行"},
        ]
        self.test_cases = test_cases
        self.update_case_table()

    # ========== 核心修改2：保留原表格更新逻辑，完全兼容 ==========
    def update_case_table(self):
        self.case_table.setRowCount(len(self.test_cases))
        for i, case in enumerate(self.test_cases):
            # 第一列：自定义编号（完全保留，不受自动序号影响）
            id_item = QTableWidgetItem(str(case["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.case_table.setItem(i, 0, id_item)
            # 第二列：用例描述
            desc_item = QTableWidgetItem(case["description"])
            self.case_table.setItem(i, 1, desc_item)
            # 第三列：结果
            result_item = QTableWidgetItem(case["result"])
            result_item.setTextAlignment(Qt.AlignCenter)
            # 根据结果设置颜色
            if case["result"] == "成功":
                result_item.setForeground(QColor(ModernStyle.SUCCESS_COLOR))
                result_item.setFont(QFont("", -1, QFont.Bold))
            elif case["result"] == "失败":
                result_item.setForeground(QColor(ModernStyle.DANGER_COLOR))
                result_item.setFont(QFont("", -1, QFont.Bold))
            else:
                result_item.setForeground(QColor(ModernStyle.TEXT_SECONDARY))
            self.case_table.setItem(i, 2, result_item)

    def add_log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")

    def clear_log(self):
        self.log_text.clear()
        self.add_log_message("日志已清空")

    def save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志文件", "", "文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.add_log_message(f"日志已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存日志失败: {str(e)}")

    def start_test(self):
        if self.test_worker and self.test_worker.isRunning():
            QMessageBox.warning(self, "警告", "测试正在运行中")
            return
        # 重置测试结果
        for case in self.test_cases:
            case["result"] = "未执行"
        self.update_case_table()
        # 重置统计信息
        self.total_label.setText(str(len(self.test_cases)))
        self.success_label.setText("0")
        self.failure_label.setText("0")
        self.pass_rate_label.setText("0%")
        self.runtime_label.setText("0秒")
        self.progress_bar.setValue(0)
        self.status_label.setText("测试准备中...")
        # 获取测试参数
        test_type_index = self.config_tab.currentIndex()
        if test_type_index == 0:  # 功能测试
            params = {
                'loop_count': self.loop_spin.value(),
                'thread_count': self.thread_spin.value(),
                'interval': self.interval_spin.value()
            }
            test_type_name = "功能测试"
        else:  # 性能测试
            params = {
                'user_count': self.user_spin.value(),
                'duration': self.duration_spin.value(),
                'ramp_time': self.ramp_spin.value()
            }
            test_type_name = "性能测试"
        # 创建并启动测试线程
        self.test_worker = TestWorker(self.test_cases, params)
        self.test_worker.update_progress.connect(self.update_progress)
        self.test_worker.update_result.connect(self.update_case_result)
        self.test_worker.update_stats.connect(self.update_statistics)
        self.test_worker.log_message.connect(self.add_log_message)
        self.test_worker.finished.connect(self.on_test_finished)
        # 更新按钮状态
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        # 启动测试
        self.test_worker.start()
        self.add_log_message(f"开始{test_type_name}，用例数: {len(self.test_cases)}，参数: {params}")

    def pause_test(self):
        if self.test_worker and self.test_worker.isRunning():
            try:
                if not self.test_worker.is_paused:
                    self.test_worker.is_paused = True
                    self.btn_pause.setText("▶️ 继续")
                    self.add_log_message("测试已暂停")
                    self.status_label.setText("已暂停")
                else:
                    self.test_worker.is_paused = False
                    self.btn_pause.setText("⏸️ 暂停")
                    self.add_log_message("测试继续执行")
                    self.status_label.setText("运行中...")
            except Exception as e:
                self.add_log_message(f"暂停操作出错: {str(e)}")

    def stop_test(self):
        if self.test_worker and self.test_worker.isRunning():
            self.test_worker.is_running = False
            self.test_worker.wait()
            self.on_test_finished()
            self.add_log_message("测试已停止")

    def on_test_finished(self):
        """测试完成后的处理"""
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸️ 暂停")
        self.btn_stop.setEnabled(False)
        self.status_label.setText("测试完成")

    def update_progress(self, progress, status):
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)

    def update_case_result(self, case_id, result):
        # 更新用例结果
        for case in self.test_cases:
            if case["id"] == case_id:
                case["result"] = result
                break
        self.update_case_table()

    def update_statistics(self, stats):
        self.success_label.setText(str(stats['success']))
        self.failure_label.setText(str(stats['failure']))
        self.pass_rate_label.setText(f"{stats['pass_rate']:.1f}%")
        self.runtime_label.setText(f"{stats['elapsed_time']:.1f}秒")

    def load_script(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择测试脚本", "", "Python文件 (*.py);;所有文件 (*)"
        )
        if file_path:
            self.add_log_message(f"加载测试脚本: {file_path}")

    def output_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存测试报告", "", "HTML文件 (*.html);;文本文件 (*.txt);;所有文件 (*)"
        )
        if file_path:
            report_content = f"""
<h2>服务器测试报告</h2>
<p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>测试类型: {self.config_tab.tabText(self.config_tab.currentIndex())}</p>
<p>总用例数: {self.total_label.text()}</p>
<p>成功: {self.success_label.text()}</p>
<p>失败: {self.failure_label.text()}</p>
<p>通过率: {self.pass_rate_label.text()}</p>
<p>运行时长: {self.runtime_label.text()}</p>
<hr>
<h3>用例详情</h3>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">
<tr><th>编号</th><th>用例描述</th><th>执行结果</th></tr>
            """
            for case in self.test_cases:
                report_content += f"<tr><td>{case['id']}</td><td>{case['description']}</td><td>{case['result']}</td></tr>"
            report_content += "</table>"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.add_log_message(f"测试报告已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存报告失败: {str(e)}")

    def open_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开配置文件", "", "配置文件 (*.ini *.conf *.json);;所有文件 (*)"
        )
        if file_path:
            self.add_log_message(f"打开配置文件: {file_path}")

    def toggle_theme(self):
        self.add_log_message("主题切换功能暂未实现")

    def show_about(self):
        about_text = f"""
<h2>服务器测试自动化工具</h2>
<p>版本: 1.0</p>
<p>本工具用于服务器功能与性能自动化测试</p>
<p>开发语言: Python + PyQt5</p>
<hr>
<p>当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        """
        QMessageBox.about(self, "关于", about_text)

    # 窗口关闭时安全退出线程
    def closeEvent(self, event):
        if self.test_worker and self.test_worker.isRunning():
            self.test_worker.is_running = False
            self.test_worker.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerTestTool()
    window.show()
    sys.exit(app.exec_())