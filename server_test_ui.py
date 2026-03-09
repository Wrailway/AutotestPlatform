import sys
import datetime
import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QAction, QLabel, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QFileDialog, QMessageBox,
    QComboBox, QGroupBox, QFormLayout, QRadioButton, QButtonGroup,
    QTreeWidget, QTreeWidgetItem, QApplication, QProgressBar  # 新增进度条
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint  
from PyQt5.QtGui import QFont, QColor, QTextCursor, QPalette  


# 统一的带嵌入标题的边框容器（和灵巧手/模型测试工具完全一致）
class FramedGroupBox(QWidget):
    def __init__(self, title="标题", parent=None):
        super().__init__(parent)
        self.title = title

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 外框
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 6px;
                background-color: #ffffff;
                margin-top: 8px;
            }
        """)

        # 标题
        self.title_label = QLabel(title, self)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                padding: 2px 8px;
                font-size: 16px;
                font-weight: bold;
                color: #1E293B;
                border: none;
            }
        """)
        self.title_label.setAlignment(Qt.AlignLeft)
        self.title_label.adjustSize()

        # 内容布局
        self.content_layout = QVBoxLayout(self.frame)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(10)

        self.main_layout.addWidget(self.frame)
        self.title_label.raise_()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.title_label.adjustSize()
        frame_rect = self.frame.rect()
        x = frame_rect.x() + 15
        y = 0
        self.title_label.move(x, y)


# 服务器测试线程（新增进度信号）
class ServerTestThread(QThread):
    log_signal = pyqtSignal(str, str)
    case_result_signal = pyqtSignal(str, str)
    result_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)  # 新增进度信号

    def __init__(self, test_type, response_time, operate_interval, user_count):
        super().__init__()
        self.test_type = test_type
        self.response_time = response_time
        self.operate_interval = operate_interval
        self.user_count = user_count
        self.is_running = True
        self.is_paused = False
        self.test_cases = [
            ("CASE-001", "单接口响应时长测试"),
            ("CASE-002", "多接口并发请求测试"),
            ("CASE-003", "数据写入性能测试"),
            ("CASE-004", "数据读取性能测试"),
            ("CASE-005", "服务器资源占用测试"),
            ("CASE-006", "异常请求处理测试")
        ]

    def run(self):
        self.log_signal.emit(f"开始{self.test_type}测试 | 响应时长：{self.response_time}S | 操作间隔：{self.operate_interval}s", "#2563EB")
        total_cases = len(self.test_cases)
        pass_count = 0

        for idx, (serial, desc) in enumerate(self.test_cases):
            if not self.is_running:
                self.log_signal.emit("测试被终止", "#DC2626")
                self.result_signal.emit("不通过")
                break
            while self.is_paused and self.is_running:
                self.log_signal.emit("测试已暂停", "#F59E0B")
                self.msleep(500)

            # 发送进度更新
            progress = int((idx + 1) / total_cases * 100)
            self.progress_signal.emit(progress)
            
            self.log_signal.emit(f"执行用例 {serial}：{desc}", "#1E293B")
            self.msleep(int(self.operate_interval * 1000))

            # 模拟测试结果
            if self.test_type == "基本功能测试":
                actual_response = random.uniform(0, self.response_time + 1)
                result = "通过" if actual_response <= self.response_time else "不通过"
                self.log_signal.emit(f"响应时长：{actual_response:.2f}S | 结果：{result}", "#10B981" if result == "通过" else "#DC2626")
            elif self.test_type == "负载测试":
                result = "通过" if self.user_count <= 500 else "不通过"
                self.log_signal.emit(f"用户数：{self.user_count} | 结果：{result}", "#10B981" if result == "通过" else "#DC2626")
            else:
                result = "通过"
                self.log_signal.emit(f"容错测试完成 | 结果：{result}", "#10B981")

            self.case_result_signal.emit(serial, result)
            if result == "通过":
                pass_count += 1

        if self.is_running:
            final_result = "通过" if pass_count == total_cases else "不通过"
            self.log_signal.emit(f"测试完成 | 通过：{pass_count}/{total_cases} | 结论：{final_result}", "#10B981" if final_result == "通过" else "#DC2626")
            self.result_signal.emit(final_result)
            self.progress_signal.emit(100)  # 测试完成进度拉满

    def stop(self):
        self.is_running = False

    def pause_resume(self):
        self.is_paused = not self.is_paused


# 服务器测试主界面（调整位置+添加进度条）
class ServerTestUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("服务器测试界面 | AutoTest Pro")
        
        # 1080p适配 + 窗口居中（和其他工具统一）
        self._setup_1080p_layout()

        self.test_thread = None
        self.test_cases = {
            "CASE-001": ("单接口响应时长测试", "-"),
            "CASE-002": ("多接口并发请求测试", "-"),
            "CASE-003": ("数据写入性能测试", "-"),
            "CASE-004": ("数据读取性能测试", "-"),
            "CASE-005": ("服务器资源占用测试", "-"),
            "CASE-006": ("异常请求处理测试", "-")
        }
        self.is_table_view = True
        
        # 全局样式初始化（添加进度条样式）
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #1E293B;
                font-family: "Microsoft YaHei", Arial;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QPushButton:disabled {
                background-color: #94A3B8;
                color: #E2E8F0;
            }
            QComboBox {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 6px 8px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                gridline-color: #F1F5F9;
                font-family: "Microsoft YaHei", Arial;
                font-size: 11px;
                padding: 2px;
            }
            QTableWidget::item {
                padding: 4px 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E293B;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                border: none;
                border-bottom: 1px solid #E2E8F0;
                padding: 6px;
                font-weight: bold;
                color: #475569;
                font-size: 12px;
            }
            QTextEdit {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
                background-color: white;
                padding: 8px;
            }
            QMenuBar {
                background-color: #1E293B;
                color: white;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
            }
            QMenuBar::item {
                padding: 8px 16px;
            }
            QMenuBar::item:selected {
                background-color: #3B82F6;
            }
            QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #EFF6FF;
                color: #2563EB;
            }
            QGroupBox {
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
                color: #475569;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 10px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
            QRadioButton {
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
                color: #1E293B;
                padding: 4px 0;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QTreeWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 11px;
                background-color: white;
            }
            QTreeWidget::item {
                padding: 4px 6px;
            }
            QTreeWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E293B;
            }
            QTreeWidget::header {
                background-color: #F8FAFC;
                border: none;
                border-bottom: 1px solid #E2E8F0;
                padding: 6px;
            }
            /* ========== 统一进度条样式（和模型测试工具一致） ========== */
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
                font-family: "Microsoft YaHei";
                height: 26px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 8px;
            }
        """)
        
        self.init_ui()
        self.init_menu_bar()
        self.update_case_display()
        
        # 窗口居中
        self._center_window()

    # 1080p适配方法
    def _setup_1080p_layout(self):
        screen_geo = QApplication.primaryScreen().geometry()
        self.setMaximumSize(int(screen_geo.width() * 0.9), int(screen_geo.height() * 0.9))
        init_w = int(screen_geo.width() * 0.85)
        init_h = int(screen_geo.height() * 0.85)
        self.setGeometry(0, 0, init_w, init_h)

    # 窗口居中方法
    def _center_window(self):
        screen_geo = QApplication.primaryScreen().geometry()
        win_geo = self.frameGeometry()
        win_geo.moveCenter(screen_geo.center())
        self.move(win_geo.topLeft())

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 第一行：Case + 日志 + 功能控件（保持不变）
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)
        
        # Case展示 
        case_box = FramedGroupBox("测试数据")
        case_title_layout = QHBoxLayout()
        self.switch_view_btn = QPushButton("切换为树状视图")
        self.switch_view_btn.setFixedHeight(32)
        self.switch_view_btn.clicked.connect(self.switch_case_view)
        case_title_layout.addStretch()
        case_title_layout.addWidget(self.switch_view_btn)
        
        # 表格视图
        self.case_table = QTableWidget()
        self.case_table.setRowCount(len(self.test_cases))
        self.case_table.setColumnCount(3)
        self.case_table.setHorizontalHeaderLabels(["序列号", "用例描述", "测试结果"])
        self.case_table.verticalHeader().setDefaultSectionSize(28)
        self.case_table.setColumnWidth(0, 100)
        self.case_table.setColumnWidth(1, 300)
        self.case_table.setColumnWidth(2, 100)
        
        # 树状视图
        self.case_tree = QTreeWidget()
        self.case_tree.setHeaderLabels(["序列号", "用例描述", "测试结果"])
        self.case_tree.hide()
        
        case_box.content_layout.addLayout(case_title_layout)
        case_box.content_layout.addWidget(self.case_table)
        case_box.content_layout.addWidget(self.case_tree)
        row1_layout.addWidget(case_box, 5)

        # 日志区域
        log_box = FramedGroupBox("动态日志输出")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        log_btn_layout = QHBoxLayout()
        self.copy_log_btn = QPushButton("拷贝")
        self.clear_log_btn = QPushButton("清理")
        self.save_log_btn = QPushButton("保存")
        self.copy_log_btn.setFixedHeight(32)
        self.clear_log_btn.setFixedHeight(32)
        self.save_log_btn.setFixedHeight(32)
        log_btn_layout.addWidget(self.copy_log_btn)
        log_btn_layout.addWidget(self.clear_log_btn)
        log_btn_layout.addWidget(self.save_log_btn)
        log_btn_layout.setSpacing(10)
        
        log_box.content_layout.addWidget(self.log_text)
        log_box.content_layout.addLayout(log_btn_layout)
        row1_layout.addWidget(log_box, 3)

        # 功能控件
        func_box = FramedGroupBox("功能选项")
        # 测试类型选择
        test_type_group = QGroupBox("测试类型")
        test_type_layout = QVBoxLayout(test_type_group)
        self.test_type_btn_group = QButtonGroup()
        self.basic_test_radio = QRadioButton("基本功能测试")
        self.load_test_radio = QRadioButton("负载测试")
        self.fault_test_radio = QRadioButton("容错测试")
        self.basic_test_radio.setChecked(True)
        self.test_type_btn_group.addButton(self.basic_test_radio)
        self.test_type_btn_group.addButton(self.load_test_radio)
        self.test_type_btn_group.addButton(self.fault_test_radio)
        test_type_layout.addWidget(self.basic_test_radio)
        test_type_layout.addWidget(self.load_test_radio)
        test_type_layout.addWidget(self.fault_test_radio)
        
        # 基本配置
        basic_config_group = QGroupBox("基本功能测试配置")
        basic_config_layout = QFormLayout(basic_config_group)
        basic_config_layout.setSpacing(10)
        self.response_time_combo = QComboBox()
        self.response_time_combo.addItems(["3", "5", "10", "20", "30"])
        self.response_time_combo.setFixedHeight(32)
        self.operate_interval_combo = QComboBox()
        self.operate_interval_combo.addItems(["2", "5", "10", "15"])
        self.operate_interval_combo.setFixedHeight(32)
        basic_config_layout.addRow("响应时长(S)：", self.response_time_combo)
        basic_config_layout.addRow("操作间隔(s)：", self.operate_interval_combo)
        
        # 负载配置
        load_config_group = QGroupBox("负载测试配置")
        load_config_layout = QFormLayout(load_config_group)
        load_config_layout.setSpacing(10)
        self.user_count_combo = QComboBox()
        self.user_count_combo.addItems(["10", "20", "30", "50", "100", "200", "500", "1000", "5000"])
        self.user_count_combo.setFixedHeight(32)
        load_config_layout.addRow("用户数：", self.user_count_combo)
        
        # 容错配置
        fault_config_group = QGroupBox("容错测试配置")
        fault_config_layout = QVBoxLayout(fault_config_group)
        fault_config_layout.addWidget(QLabel("模拟服务器宕机等操作"))
        
        # 组装
        func_box.content_layout.addWidget(test_type_group)
        func_box.content_layout.addWidget(basic_config_group)
        func_box.content_layout.addWidget(load_config_group)
        func_box.content_layout.addWidget(fault_config_group)
        func_box.content_layout.addStretch()
        row1_layout.addWidget(func_box, 2)
        
        main_layout.addLayout(row1_layout)

        # ===================== 核心调整：互换位置 + 添加进度条 =====================
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)
        
        # 左侧：测试结果区域（占7份，添加进度条）
        result_box = FramedGroupBox("测试结果")
        result_layout = QVBoxLayout()
        
        # 进度条（统一样式）
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # 测试结果文本
        self.result_text = QLabel("等待测试...")
        self.result_text.setAlignment(Qt.AlignCenter)
        self.result_text.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        self.result_text.setStyleSheet("color: #64748B; padding: 16px;border: none;")
        
        result_layout.addWidget(self.progress_bar)
        result_layout.addWidget(self.result_text)
        result_box.content_layout.addLayout(result_layout)
        row2_layout.addWidget(result_box, 7)  # 占7份

        # 右侧：执行区域（占3份）
        exec_box = FramedGroupBox("执行区域")
        exec_layout = QHBoxLayout()
        exec_layout.setSpacing(10)  # 缩小按钮间距适配宽度
        
        self.start_btn = QPushButton("开始测试")
        self.stop_btn = QPushButton("结束测试")
        self.pause_resume_btn = QPushButton("暂停/恢复测试")
        # 统一按钮尺寸+字体
        self.start_btn.setFixedSize(100, 40)  # 缩小宽度适配
        self.stop_btn.setFixedSize(100, 40)
        self.pause_resume_btn.setFixedSize(100, 40)
        self.start_btn.setFont(QFont("Microsoft YaHei", 12))
        self.stop_btn.setFont(QFont("Microsoft YaHei", 12))
        self.pause_resume_btn.setFont(QFont("Microsoft YaHei", 12))
        
        self.start_btn.clicked.connect(self.start_test)
        self.stop_btn.clicked.connect(self.stop_test)
        self.pause_resume_btn.clicked.connect(self.pause_resume_test)
        self.stop_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        
        exec_layout.addWidget(self.start_btn)
        exec_layout.addWidget(self.stop_btn)
        exec_layout.addWidget(self.pause_resume_btn)
        exec_layout.addStretch()
        exec_box.content_layout.addLayout(exec_layout)
        row2_layout.addWidget(exec_box, 3)  # 占3份
        
        main_layout.addLayout(row2_layout)

        # 绑定日志按钮事件
        self.copy_log_btn.clicked.connect(self.copy_log)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.save_log_btn.clicked.connect(self.save_log)

    def init_menu_bar(self):
        """菜单栏样式与其他工具完全统一"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(File)")
        load_script_action = QAction("脚本加载", self)
        load_script_action.triggered.connect(self.load_script)
        export_report_action = QAction("输出报告", self)
        export_report_action.triggered.connect(self.export_test_report)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(load_script_action)
        file_menu.addAction(export_report_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # 配置菜单
        config_menu = menubar.addMenu("配置")
        open_config_action = QAction("打开配置文件", self)
        open_config_action.triggered.connect(self.open_config_file)
        config_menu.addAction(open_config_action)

        # 选项菜单
        option_menu = menubar.addMenu("选项")
        theme_action = QAction("主题(Optional)", self)
        theme_action.triggered.connect(self.change_theme)
        option_menu.addAction(theme_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("版权及版本信息", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # Case视图切换
    def switch_case_view(self):
        if self.is_table_view:
            self.case_table.hide()
            self.case_tree.show()
            self.switch_view_btn.setText("切换为表格视图")
            self.is_table_view = False
        else:
            self.case_tree.hide()
            self.case_table.show()
            self.switch_view_btn.setText("切换为树状视图")
            self.is_table_view = True
        self.update_case_display()

    def update_case_display(self):
        table_font = QFont("Microsoft YaHei")
        table_font.setPointSize(11)
        
        if self.is_table_view:
            for row, (serial, (desc, result)) in enumerate(self.test_cases.items()):
                # 序列号
                item_serial = QTableWidgetItem(serial)
                item_serial.setFont(table_font)
                self.case_table.setItem(row, 0, item_serial)
                
                # 描述
                item_desc = QTableWidgetItem(desc)
                item_desc.setFont(table_font)
                self.case_table.setItem(row, 1, item_desc)
                
                # 结果
                item_result = QTableWidgetItem(result)
                item_result.setFont(table_font)
                if result == "通过":
                    item_result.setForeground(QColor("#10B981"))
                elif result == "不通过":
                    item_result.setForeground(QColor("#DC2626"))
                else:
                    item_result.setForeground(QColor("#64748B"))
                self.case_table.setItem(row, 2, item_result)
        else:
            self.case_tree.clear()
            root = QTreeWidgetItem(self.case_tree, ["服务器测试用例"])
            root.setExpanded(True)
            root.setFont(0, QFont("Microsoft YaHei", 11, QFont.Bold))
            
            for serial, (desc, result) in self.test_cases.items():
                item = QTreeWidgetItem(root, [serial, desc, result])
                item.setFont(0, table_font)
                item.setFont(1, table_font)
                item.setFont(2, table_font)
                
                if result == "通过":
                    item.setForeground(2, QColor("#10B981"))
                elif result == "不通过":
                    item.setForeground(2, QColor("#DC2626"))
                else:
                    item.setForeground(2, QColor("#64748B"))

    def update_case_result(self, serial, result):
        if serial in self.test_cases:
            self.test_cases[serial] = (self.test_cases[serial][0], result)
            self.update_case_display()

    # 新增：更新进度条
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    # 日志操作
    def append_log(self, text, color="#1E293B"):
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        char_format = self.log_text.currentCharFormat()
        char_format.setForeground(QColor(color))
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        cursor.insertText(f"[{timestamp}] {text}\n", char_format)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def copy_log(self):
        self.log_text.selectAll()
        self.log_text.copy()
        self.append_log("日志已拷贝到剪贴板", "#10B981")

    def clear_log(self):
        self.log_text.clear()
        self.append_log("日志已清空", "#10B981")

    def save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "保存日志", "", "文本文件 (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.append_log(f"日志已保存到：{file_path}", "#10B981")

    # 测试控制（绑定进度条）
    def start_test(self):
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "测试已在运行中！")
            return
        # 获取配置
        if self.basic_test_radio.isChecked():
            test_type = "基本功能测试"
            response_time = int(self.response_time_combo.currentText())
            operate_interval = int(self.operate_interval_combo.currentText())
            user_count = 0
        elif self.load_test_radio.isChecked():
            test_type = "负载测试"
            response_time = 0
            operate_interval = int(self.operate_interval_combo.currentText())
            user_count = int(self.user_count_combo.currentText())
        else:
            test_type = "容错测试"
            response_time = 0
            operate_interval = int(self.operate_interval_combo.currentText())
            user_count = 0
        # 重置用例
        for serial in self.test_cases.keys():
            self.test_cases[serial] = (self.test_cases[serial][0], "-")
        self.update_case_display()
        # 重置进度条
        self.progress_bar.setValue(0)
        # 启动线程
        self.test_thread = ServerTestThread(test_type, response_time, operate_interval, user_count)
        self.test_thread.log_signal.connect(self.append_log)
        self.test_thread.case_result_signal.connect(self.update_case_result)
        self.test_thread.result_signal.connect(self.update_test_result)
        self.test_thread.progress_signal.connect(self.update_progress)  # 绑定进度信号
        self.test_thread.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_resume_btn.setEnabled(True)
        self.result_text.setText("测试进行中...")
        self.result_text.setStyleSheet("color: #F59E0B; padding: 16px;border: none;")

    def stop_test(self):
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        self.pause_resume_btn.setText("暂停/恢复测试")
        self.result_text.setText("测试已终止")
        self.result_text.setStyleSheet("color: #DC2626; padding: 16px;border: none;")

    def pause_resume_test(self):
        if not self.test_thread or not self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "暂无运行中的测试！")
            return
        self.test_thread.pause_resume()
        if self.test_thread.is_paused:
            self.pause_resume_btn.setText("恢复测试")
            self.append_log("测试已暂停", "#F59E0B")
            self.result_text.setText("测试已暂停")
            self.result_text.setStyleSheet("color: #9333EA; padding: 16px;border: none;")
        else:
            self.pause_resume_btn.setText("暂停/恢复测试")
            self.append_log("测试已恢复", "#2563EB")
            self.result_text.setText("测试进行中...")
            self.result_text.setStyleSheet("color: #F59E0B; padding: 16px;border: none;")

    def update_test_result(self, result):
        self.result_text.setText(f"测试结论：{result}")
        self.result_text.setStyleSheet(f"color: {'#10B981' if result == '通过' else '#DC2626'}; padding: 16px;border: none;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        self.pause_resume_btn.setText("暂停/恢复测试")
        self.progress_bar.setValue(100)  # 测试完成进度拉满

    # 菜单功能
    def load_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python脚本 (*.py)")
        if file_path:
            self.append_log(f"已加载服务器测试脚本：{file_path}", "#2563EB")

    def export_test_report(self):
        if all(v[1] == "-" for v in self.test_cases.values()):
            QMessageBox.warning(self, "警告", "暂无测试数据！")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "导出报告", "", "HTML (*.html);;TXT (*.txt)")
        if file_path:
            if file_path.endswith(".html"):
                report_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>服务器测试报告 | AutoTest Pro</title>
    <style>
        body {{ font-family: "Microsoft YaHei", Arial; margin: 30px; color: #1E293B; }}
        .title {{ color: #2563EB; text-align: center; font-size: 24px; }}
        .info {{ margin: 20px 0; font-size: 16px; }}
        .case-table {{ border-collapse: collapse; width: 80%; margin: 20px auto; }}
        .case-table th, .case-table td {{ border: 1px solid #E2E8F0; padding: 10px; text-align: center; }}
        .case-table th {{ background-color: #F8FAFC; font-weight: bold; color: #475569; }}
        .pass {{ color: #10B981; font-weight: bold; }}
        .fail {{ color: #DC2626; font-weight: bold; }}
        .log {{ margin: 30px 0; padding: 20px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1 class="title">服务器测试报告</h1>
    <div class="info">
        <p>生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>测试结论：<span class="{'pass' if self.result_text.text().endswith('通过') else 'fail'}">{self.result_text.text()}</span></p>
    </div>
    <h3 style="text-align: center; color: #475569;">测试用例结果</h3>
    <table class="case-table">
        <tr>
            <th>序列号</th>
            <th>用例描述</th>
            <th>测试结果</th>
        </tr>
"""
                for serial, (desc, res) in self.test_cases.items():
                    report_content += f"""
        <tr>
            <td>{serial}</td>
            <td>{desc}</td>
            <td class="{'pass' if res == '通过' else 'fail' if res == '不通过' else ''}">{res}</td>
        </tr>
                    """
                report_content += f"""
    </table>
    <div class="log">
        <h3 style="color: #475569;">测试日志</h3>
        <pre style="font-size: 14px; line-height: 1.5;">{self.log_text.toPlainText()}</pre>
    </div>
</body>
</html>
"""
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"=== 服务器测试报告 | AutoTest Pro ===\n")
                    f.write(f"生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"测试结论：{self.result_text.text()}\n\n")
                    f.write("=== 测试用例结果 ===\n")
                    f.write("序列号\t\t用例描述\t\t测试结果\n")
                    for serial, (desc, res) in self.test_cases.items():
                        f.write(f"{serial}\t{desc}\t{res}\n")
                    f.write("\n=== 测试日志 ===\n")
                    f.write(self.log_text.toPlainText())
            self.append_log(f"服务器测试报告已导出到：{file_path}", "#10B981")

    def open_config_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开配置", "", "配置文件 (*.ini *.json)")
        if file_path:
            self.append_log(f"已加载服务器测试配置文件：{file_path}", "#2563EB")

    def change_theme(self):
        QMessageBox.information(self, "提示", "主题切换功能待实现", QMessageBox.Ok)
        QMessageBox.setStyleSheet("""
            QMessageBox {
                font-family: "Microsoft YaHei";
                border-radius: 8px;
                background: white;
            }
            QMessageBox QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563EB;
            }
        """)

    def show_about(self):
        about_box = QMessageBox(self)
        about_box.setWindowTitle("关于 | AutoTest Pro")
        about_box.setText("""
            <div style='text-align:center; font-family:Microsoft YaHei;'>
                <h3 style='color:#2563EB; margin:0;'>服务器自动化测试工具 v1.0</h3>
                <p style='color:#475569; margin:12px 0;'>基于PyQt5开发 | 企业级自动化测试解决方案</p>
                <p style='color:#64748B; font-size:12px;'>© 2026 测试技术团队 版权所有</p>
            </div>
        """)
        about_box.setStyleSheet("""
            QMessageBox {
                font-family: "Microsoft YaHei";
                border-radius: 8px;
                background: white;
            }
            QMessageBox QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        about_box.exec_()


# 独立运行入口
if __name__ == "__main__":
    # 统一高DPI适配
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    # 全局调色板统一
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 250, 252))
    app.setPalette(palette)
    
    window = ServerTestUI()
    window.show()
    sys.exit(app.exec_())