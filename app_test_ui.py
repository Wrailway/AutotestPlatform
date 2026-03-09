import sys
import time
import datetime
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QAction,
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QFileDialog, QHeaderView, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QFont, QColor, QTextCursor, QPalette


# 核心组件：用QFrame实现「完整外框 + 标题嵌边框靠左」
class FramedGroupBox(QWidget):
    def __init__(self, title="标题", parent=None):
        super().__init__(parent)
        self.title = title
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. 框架（外框）
        self.frame = QFrame()
        self.frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.frame.setLineWidth(1)  # 边框粗细
        self.frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;  /* 外框颜色 */
                border-radius: 6px;         /* 圆角 */
                background-color: #ffffff;
                margin-top: 8px;            /* 给标题留顶部空间 */
            }
        """)

        # 2. 标题Label（靠左显示 + 透明边框）
        self.title_label = QLabel(title, self)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;  /* 白色背景覆盖边框 */
                padding: 2px 8px;           /* 上下加内边距，避免文字贴边 */
                font-size: 16px;
                font-weight: bold;
                color: #1E293B;
                border: none;               /* 标题Label透明边框 */
            }
        """)
        self.title_label.setAlignment(Qt.AlignLeft)  # 文字靠左对齐
        self.title_label.adjustSize()  # 自动适配文字大小

        # 3. 内容布局（frame内的内容区）
        self.content_layout = QVBoxLayout(self.frame)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(10)

        self.main_layout.addWidget(self.frame)

        # 强制置顶显示（避免被遮挡）
        self.title_label.raise_()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # 重新计算标题位置（核心：靠左）
        self.title_label.adjustSize()  # 确保尺寸最新
        frame_rect = self.frame.rect()
        
        # 水平位置：靠左，距离边框左侧15px（可调整）
        x = frame_rect.x() + 15  # 15px是偏移量，越大越靠右，越小越靠左
        # 垂直位置：确保文字完整显示
        y = 0
        
        self.title_label.move(x, y)


# 模拟测试线程（新增进度信号）
class TestThread(QThread):
    log_signal = pyqtSignal(str, str)
    result_signal = pyqtSignal(str)
    case_result_signal = pyqtSignal(int, str)
    progress_signal = pyqtSignal(int)  # 新增进度更新信号

    def __init__(self, test_type, interval, count, case_count):
        super().__init__()
        self.test_type = test_type
        self.interval = interval
        self.count = count
        self.case_count = case_count
        self.is_running = True
        self.is_paused = False

    def run(self):
        self.log_signal.emit(f"开始{self.test_type}测试，间隔{self.interval}s，次数{self.count}次", "#2563EB")

        for i in range(self.count):
            if not self.is_running:
                self.log_signal.emit("测试被用户终止", "#DC2626")
                break

            while self.is_paused:
                time.sleep(0.1)

            time.sleep(self.interval)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # 发送进度更新信号（当前执行次数）
            self.progress_signal.emit(i + 1)

            if i < self.case_count:
                self.log_signal.emit(f"[{timestamp}] 执行第 {i+1} 个测试用例", "#1E293B")
                result = "通过" if random.random() > 0.1 else "失败"
                self.case_result_signal.emit(i, result)
            else:
                self.log_signal.emit(f"[{timestamp}] 执行第 {i+1} 次操作（无新用例）", "#1E293B")

        self.result_signal.emit(f"{self.test_type}测试完成：{'通过' if self.is_running else '终止'}")

    def stop(self):
        self.is_running = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False


class AppTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APP自动化测试工具 | AutoTest Pro")
        
        # 1080p适配 - 窗口尺寸控制
        self._setup_1080p_layout()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
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
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                gridline-color: #F1F5F9;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px;
                text-align: center;
                vertical-align: middle;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E293B;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                border: none;
                border-bottom: 1px solid #E2E8F0;
                padding: 8px;
                font-weight: bold;
                color: #475569;
                text-align: center;
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
            /* 测试结果文字样式（强制透明无边框） */
            #result-text-label {
                padding: 8px 0;
                background-color: transparent !important;
                border: none !important;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                color: #1E293B;
            }
            /* 进度条默认样式 */
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
                font-family: "Microsoft YaHei";
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 8px;
            }
        """)

        self.test_thread = None
        self.init_ui()
        self.init_menu_bar()
        self.load_app_test_cases()
        
        # 窗口居中
        self._center_window()

    # 1080p尺寸适配方法
    def _setup_1080p_layout(self):
        screen_geo = QApplication.primaryScreen().geometry()
        self.setMaximumSize(int(screen_geo.width()*0.9), int(screen_geo.height()*0.9))
        init_width = int(screen_geo.width()*0.85)
        init_height = int(screen_geo.height()*0.85)
        self.setGeometry(0, 0, init_width, init_height)

    # 窗口居中方法
    def _center_window(self):
        screen_geo = QApplication.primaryScreen().geometry()
        win_geo = self.frameGeometry()
        win_geo.moveCenter(screen_geo.center())
        self.move(win_geo.topLeft())

    def load_app_test_cases(self):
        """加载APP专项测试用例"""
        app_cases = [
            ("CASE-APP-001", "APP正常启动测试", "待执行"),
            ("CASE-APP-002", "APP冷启动耗时测试", "待执行"),
            ("CASE-APP-003", "APP热启动响应测试", "待执行"),
            ("CASE-APP-004", "APP安装功能验证", "待执行"),
            ("CASE-APP-005", "APP卸载功能验证", "待执行"),
            ("CASE-APP-006", "APP升级覆盖安装测试", "待执行"),
            ("CASE-APP-007", "权限申请弹窗验证", "待执行"),
            ("CASE-APP-008", "权限拒绝后功能可用性", "待执行"),
            ("CASE-APP-009", "网络切换（Wi‑Fi/4G）稳定性", "待执行"),
            ("CASE-APP-010", "无网络状态功能容错", "待执行"),
            ("CASE-APP-011", "弱网超时重试机制", "待执行"),
            ("CASE-APP-012", "前后台切换数据保存", "待执行"),
            ("CASE-APP-013", "锁屏解锁后状态恢复", "待执行"),
            ("CASE-APP-014", "电话打断恢复测试", "待执行"),
            ("CASE-APP-015", "UI布局适配（不同分辨率）", "待执行"),
            ("CASE-APP-016", "横竖屏切换显示正常", "待执行"),
            ("CASE-APP-017", "按钮点击/输入框功能验证", "待执行"),
            ("CASE-APP-018", "列表滑动流畅度测试", "待执行"),
            ("CASE-APP-019", "图片加载/缓存验证", "待执行"),
            ("CASE-APP-020", "崩溃/ANR 异常捕获", "待执行"),
            ("CASE-APP-021", "内存泄漏稳定性测试", "待执行"),
            ("CASE-APP-022", "CPU/电量消耗测试", "待执行"),
            ("CASE-APP-023", "Monkey随机操作稳定性", "待执行"),
            ("CASE-APP-024", "长时间运行稳定性", "待执行"),
            ("CASE-APP-025", "用户登录/登出功能", "待执行"),
            ("CASE-APP-026", "登录状态过期处理", "待执行"),
            ("CASE-APP-027", "Token 过期自动刷新", "待执行"),
            ("CASE-APP-028", "接口请求参数校验", "待执行"),
            ("CASE-APP-029", "异常返回码容错处理", "待执行"),
            ("CASE-APP-030", "数据本地缓存一致性", "待执行"),
        ]

        self.case_table.setRowCount(len(app_cases))
        for row, (case_id, desc, result) in enumerate(app_cases):
            # 序号单元格（居中）
            item1 = QTableWidgetItem(case_id)
            item1.setTextAlignment(Qt.AlignCenter)
            self.case_table.setItem(row, 0, item1)
            
            # 用例描述单元格（居中）
            item2 = QTableWidgetItem(desc)
            item2.setTextAlignment(Qt.AlignCenter)
            self.case_table.setItem(row, 1, item2)
            
            # 测试结果单元格（居中）
            item3 = QTableWidgetItem(result)
            item3.setTextAlignment(Qt.AlignCenter)
            self.case_table.setItem(row, 2, item3)

    # ✅ 新增：统计用例结果方法
    def count_case_results(self):
        """统计用例执行结果：成功、失败、跳过（待执行）"""
        success = 0
        failed = 0
        skipped = 0
        total = self.case_table.rowCount()
        
        for row in range(total):
            result_item = self.case_table.item(row, 2)
            if result_item:
                result = result_item.text()
                if result == "通过":
                    success += 1
                elif result == "失败":
                    failed += 1
                else:  # 待执行/跳过
                    skipped += 1
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "skipped": skipped,
            "success_rate": round((success / total) * 100, 2) if total > 0 else 0
        }

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 第一行：用例展示 + 日志展示 + 功能选项
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)

        # 1. 用例展示区域（占比5）
        case_box = FramedGroupBox("测试数据")
        self.case_table = QTableWidget()
        self.case_table.setColumnCount(3)
        self.case_table.setHorizontalHeaderLabels(["序号", "用例描述", "测试结果"])
        self.case_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.case_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.case_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # 设置表格行高（避免内容错位）
        self.case_table.verticalHeader().setDefaultSectionSize(35)
        case_box.content_layout.addWidget(self.case_table)
        row1_layout.addWidget(case_box, 5)

        # 2. 日志展示区域（占比3）
        log_box = FramedGroupBox("动态日志输出")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("拷贝")
        self.clear_btn = QPushButton("清理")
        self.save_btn = QPushButton("保存")
        self.copy_btn.setFixedHeight(32)
        self.clear_btn.setFixedHeight(32)
        self.save_btn.setFixedHeight(32)
        self.copy_btn.clicked.connect(self.copy_log)
        self.clear_btn.clicked.connect(self.clear_log)
        self.save_btn.clicked.connect(self.save_log)
        log_btn_layout.addWidget(self.copy_btn)
        log_btn_layout.addWidget(self.clear_btn)
        log_btn_layout.addWidget(self.save_btn)
        log_btn_layout.setSpacing(10)
        log_box.content_layout.addWidget(self.log_text)
        log_box.content_layout.addLayout(log_btn_layout)
        row1_layout.addWidget(log_box, 3)

        # 3. 功能选项区域（占比2）
        func_box = FramedGroupBox("功能选项")
        func_layout = QGridLayout()
        func_layout.setSpacing(15)
        # 操作间隔
        interval_label = QLabel("操作间隔:")
        interval_label.setFont(QFont("Microsoft YaHei", 12))
        interval_label.setStyleSheet("color: #475569;")
        func_layout.addWidget(interval_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["2s", "5s", "10s", "15s"])
        self.interval_combo.setFixedHeight(32)
        self.interval_combo.setMinimumWidth(100)
        func_layout.addWidget(self.interval_combo, 0, 1)
        # 测试次数
        count_label = QLabel("测试次数:")
        count_label.setFont(QFont("Microsoft YaHei", 12))
        count_label.setStyleSheet("color: #475569;")
        func_layout.addWidget(count_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.count_combo = QComboBox()
        self.count_combo.addItems(["10", "20", "30", "50", "100"])
        self.count_combo.setCurrentText("30")
        self.count_combo.setFixedHeight(32)
        self.count_combo.setMinimumWidth(100)
        func_layout.addWidget(self.count_combo, 1, 1)
        # 测试类型
        type_label = QLabel("测试类型:")
        type_label.setFont(QFont("Microsoft YaHei", 12))
        type_label.setStyleSheet("color: #475569;")
        func_layout.addWidget(type_label, 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.test_type_combo = QComboBox()
        self.test_type_combo.addItems(["基本功能", "Monkey"])
        self.test_type_combo.setFixedHeight(32)
        self.test_type_combo.setMinimumWidth(100)
        func_layout.addWidget(self.test_type_combo, 2, 1)
        # 空白拉伸
        func_layout.setRowStretch(3, 1)
        func_box.content_layout.addLayout(func_layout)
        row1_layout.addWidget(func_box, 2)

        # 第二行：测试结果（3） + 执行控制（7）
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)

        # 1. 测试结果区域（占比3）- 包含进度条+结论
        result_box = FramedGroupBox("测试结果")
        result_layout = QVBoxLayout()
        result_layout.setSpacing(15)
        result_layout.setAlignment(Qt.AlignCenter)
        
        # 测试进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0% (0/0)")  # 初始格式
        result_layout.addWidget(self.progress_bar)
        
        # 测试结论文字
        self.result_text = QLabel("等待测试...")
        self.result_text.setStyleSheet("border: none;")
        self.result_text.setObjectName("result-text-label")
        result_layout.addWidget(self.result_text)
        
        result_box.content_layout.addLayout(result_layout)
        row2_layout.addWidget(result_box, 7)

        # 2. 执行控制区域（占比7）
        exec_box = FramedGroupBox("执行控制")
        exec_layout = QHBoxLayout()
        exec_layout.setSpacing(20)
        self.start_btn = QPushButton("开始测试")
        self.stop_btn = QPushButton("结束测试")
        self.pause_btn = QPushButton("暂停/恢复测试")
        self.start_btn.setFixedSize(120, 40)
        self.stop_btn.setFixedSize(120, 40)
        self.pause_btn.setFixedSize(120, 40)
        self.start_btn.setFont(QFont("Microsoft YaHei", 12))
        self.stop_btn.setFont(QFont("Microsoft YaHei", 12))
        self.pause_btn.setFont(QFont("Microsoft YaHei", 12))
        self.start_btn.clicked.connect(self.start_test)
        self.stop_btn.clicked.connect(self.stop_test)
        self.pause_btn.clicked.connect(self.pause_test)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        exec_layout.addWidget(self.start_btn)
        exec_layout.addWidget(self.stop_btn)
        # exec_layout.addWidget(self.pause_btn)
        exec_layout.addStretch()
        exec_box.content_layout.addLayout(exec_layout)
        row2_layout.addWidget(exec_box, 3)

        # 组装主布局
        main_layout.addLayout(row1_layout)
        main_layout.addLayout(row2_layout)

    def init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        # 文件菜单
        file_menu = menubar.addMenu("文件(File)")
        load_script_action = QAction("脚本加载", self)
        export_report_action = QAction("输出报告", self)
        exit_action = QAction("退出", self)
        file_menu.addAction(load_script_action)
        file_menu.addAction(export_report_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # 配置菜单
        config_menu = menubar.addMenu("配置")
        open_config_action = QAction("打开配置文件", self)
        config_menu.addAction(open_config_action)

        # 选项菜单
        option_menu = menubar.addMenu("选项")
        theme_action = QAction("主题(Optional)", self)
        theme_action.triggered.connect(lambda: QMessageBox.information(self, "提示", "主题功能待实现"))
        option_menu.addAction(theme_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("版权及版本信息", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 绑定事件
        load_script_action.triggered.connect(self.load_script)
        export_report_action.triggered.connect(self.export_report)
        exit_action.triggered.connect(self.close)
        open_config_action.triggered.connect(self.open_config)

    # --- 日志操作方法 ---
    def append_log(self, text, color="#1E293B"):
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        format_ = self.log_text.currentCharFormat()
        format_.setForeground(QColor(color))
        cursor.insertText(text + "\n", format_)
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
        file_path, _ = QFileDialog.getSaveFileName(self, "保存日志", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.append_log(f"日志已保存到: {file_path}", "#10B981")

    # --- 测试控制方法 ---
    def start_test(self):
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "测试正在进行中")
            return

        test_type = self.test_type_combo.currentText()
        interval = int(self.interval_combo.currentText()[:-1])
        count = int(self.count_combo.currentText())
        case_count = self.case_table.rowCount()

        # 初始化进度条
        self.progress_bar.setRange(0, count)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0% (0/{})".format(count))
        # 恢复进度条默认样式
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                text-align: center;
                font-size: 12px;
                font-family: "Microsoft YaHei";
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 8px;
            }
        """)

        self.test_thread = TestThread(test_type, interval, count, case_count)
        self.test_thread.log_signal.connect(self.append_log)
        self.test_thread.result_signal.connect(self.on_test_finished)
        self.test_thread.case_result_signal.connect(self.update_case_result)
        self.test_thread.progress_signal.connect(self.update_progress)
        self.test_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.result_text.setText("测试进行中...")
        self.result_text.setStyleSheet("color: #F59E0B; border: none;")

    def update_progress(self, current):
        """更新进度条"""
        count = int(self.count_combo.currentText())
        progress_percent = int((current / count) * 100)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{progress_percent}% ({current}/{count})")

    # ✅ 核心修改：重写测试完成逻辑，改为统计用例结果
    def on_test_finished(self, result):
        """测试完成更新结果（统计用例成功/失败/跳过）"""
        # 统计用例结果
        case_stats = self.count_case_results()
        
        # 拼接统计结论
        if "终止" in result:
            conclusion = f"测试终止 | 总计{case_stats['total']}用例 | 成功{case_stats['success']} | 失败{case_stats['failed']} | 跳过{case_stats['skipped']}"
            self.result_text.setStyleSheet("color: #DC2626;border: none;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    text-align: center;
                    font-size: 12px;
                    font-family: "Microsoft YaHei";
                    height: 30px;
                }
                QProgressBar::chunk {
                    background-color: #DC2626;
                    border-radius: 8px;
                }
            """)
        else:
            conclusion = f"测试完成 | 总计{case_stats['total']}用例 | 成功{case_stats['success']} | 失败{case_stats['failed']} | 跳过{case_stats['skipped']} | 成功率{case_stats['success_rate']}%"
            # 根据成功率判断颜色
            if case_stats['failed'] == 0:
                self.result_text.setStyleSheet("color: #10B981;border: none;")
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #E2E8F0;
                        border-radius: 8px;
                        text-align: center;
                        font-size: 12px;
                        font-family: "Microsoft YaHei";
                        height: 30px;
                    }
                    QProgressBar::chunk {
                        background-color: #10B981;
                        border-radius: 8px;
                    }
                """)
            elif case_stats['failed'] > 0:
                self.result_text.setStyleSheet("color: #F59E0B;border: none;")
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #E2E8F0;
                        border-radius: 8px;
                        text-align: center;
                        font-size: 12px;
                        font-family: "Microsoft YaHei";
                        height: 30px;
                    }
                    QProgressBar::chunk {
                        background-color: #F59E0B;
                        border-radius: 8px;
                    }
                """)
        
        # 更新结果文本和日志
        self.result_text.setText(conclusion)
        self.append_log(f"\n【测试统计】{conclusion}", "#2563EB")
        
        # 更新进度条到100%
        count = int(self.count_combo.currentText())
        self.progress_bar.setValue(count)
        self.progress_bar.setFormat(f"100% ({count}/{count})")
        
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("暂停/恢复测试")

    def update_case_result(self, row, result):
        """更新用例测试结果"""
        item = QTableWidgetItem(result)
        item.setTextAlignment(Qt.AlignCenter)
        if result == "通过":
            item.setForeground(QColor("#10B981"))
        else:
            item.setForeground(QColor("#DC2626"))
        self.case_table.setItem(row, 2, item)

    def stop_test(self):
        """停止测试"""
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("暂停/恢复测试")

    def pause_test(self):
        """暂停/恢复测试"""
        if self.test_thread and self.test_thread.isRunning():
            if self.test_thread.is_paused:
                self.test_thread.resume()
                self.pause_btn.setText("暂停测试")
                self.append_log("测试已恢复", "#2563EB")
            else:
                self.test_thread.pause()
                self.pause_btn.setText("恢复测试")
                self.append_log("测试已暂停", "#2563EB")

    # --- 菜单功能实现 ---
    def load_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "Python Files (*.py)")
        if file_path:
            self.append_log(f"加载脚本: {file_path}", "#10B981")

    def export_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出报告", "", "HTML Files (*.html)")
        if file_path:
            # ✅ 导出报告时包含用例统计
            case_stats = self.count_case_results()
            report_content = f"""
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <title>APP自动化测试报告</title>
                <style>
                    body {{ font-family: "Microsoft YaHei", Arial; margin: 20px; color: #1E293B; }}
                    h1 {{ color: #2563EB; }}
                    pre {{ background-color: #F8FAFC; padding: 16px; border-radius: 8px; border: 1px solid #E2E8F0; }}
                    .conclusion {{ font-size: 16px; font-weight: bold; margin-top: 20px; }}
                    .success {{ color: #10B981; }}
                    .failed {{ color: #DC2626; }}
                    .stats {{ 
                        background-color: #EFF6FF; 
                        padding: 16px; 
                        border-radius: 8px; 
                        margin: 16px 0;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
            <h1>APP自动化测试报告</h1>
            <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="stats">
                <strong>用例统计：</strong><br>
                总计用例：{case_stats['total']} 个<br>
                成功：{case_stats['success']} 个 | 失败：{case_stats['failed']} 个 | 跳过：{case_stats['skipped']} 个<br>
                成功率：{case_stats['success_rate']}%
            </div>

            <h3>测试日志:</h3>
            <pre>{self.log_text.toPlainText()}</pre>
            <div class="conclusion {'success' if '通过' in self.result_text.text() else 'failed'}">
                测试结论: {self.result_text.text()}
            </div>
            </body>
            </html>
            """
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            self.append_log(f"报告已导出到: {file_path}", "#10B981")

    def open_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开配置文件", "", "Config Files (*.json *.ini)")
        if file_path:
            self.append_log(f"加载配置: {file_path}", "#10B981")

    def show_about(self):
        QMessageBox.information(self, "关于", """
            <div style='text-align:center; font-family:Microsoft YaHei;'>
                <h3 style='color:#2563EB; margin:0;'>APP自动化测试工具 v1.0</h3>
                <p style='color:#475569; margin:12px 0;'>基于PyQt5 QFrame实现嵌边框标题</p>
                <p style='color:#64748B; font-size:12px;'>© 2026 测试技术团队 版权所有</p>
            </div>
        """)


if __name__ == "__main__":
    # 高DPI适配
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 启动应用
    app = QApplication(sys.argv)
    window = AppTestWindow()
    window.show()
    sys.exit(app.exec_())