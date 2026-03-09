import sys
import datetime
import random
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QAction, QLabel, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QFileDialog, QMessageBox,
    QComboBox, QGroupBox, QFormLayout, QDateTimeEdit, QApplication,
    QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDateTime, QPoint
from PyQt5.QtGui import QFont, QColor, QTextCursor, QPalette


# 统一的带嵌入标题的边框容器（和灵巧手工具完全一致）
class FramedGroupBox(QWidget):
    def __init__(self, title="标题", parent=None):
        super().__init__(parent)
        self.title = title

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

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


# 模型测试线程（优化暂停/恢复逻辑）
class ModelTestThread(QThread):
    log_signal = pyqtSignal(str, str)
    pr_matrix_signal = pyqtSignal(dict)
    result_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, age_filter, gender_filter, time_filter):
        super().__init__()
        self.age_filter = age_filter
        self.gender_filter = gender_filter
        self.time_filter = time_filter
        self.is_running = True
        self.is_paused = False
        self.test_categories = ["人脸检测", "行为识别", "情绪分析", "目标跟踪"]
        self.test_steps = 5

    def run(self):
        self.log_signal.emit(
            f"开始模型测试 | 筛选条件：年龄={self.age_filter}、性别={self.gender_filter}、时间={self.time_filter}", 
            "#2563EB"
        )
        for step in range(self.test_steps):
            if not self.is_running:
                self.log_signal.emit("测试被用户终止", "#DC2626")
                self.result_signal.emit("不通过")
                break
            while self.is_paused and self.is_running:
                self.msleep(500)  # 暂停时循环等待，减少资源占用
            self.msleep(1000)
            progress = int((step + 1) / self.test_steps * 100)
            self.progress_signal.emit(progress)

            # 生成随机P/R矩阵数据
            pr_matrix = {}
            for category in self.test_categories:
                pr_matrix[category] = {
                    "TP": random.randint(80, 99),
                    "FP": random.randint(0, 20),
                    "FN": random.randint(0, 15),
                    "Precision": round(random.uniform(0.85, 0.99), 4),
                    "Recall": round(random.uniform(0.80, 0.98), 4)
                }
            self.pr_matrix_signal.emit(pr_matrix)
            self.log_signal.emit(
                f"测试步骤{step+1}/{self.test_steps} | P/R矩阵已更新", 
                "#1E293B"
            )

        if self.is_running:
            self.log_signal.emit("模型测试完成，所有指标达标", "#10B981")
            self.result_signal.emit("通过")

    def stop(self):
        self.is_running = False

    def pause_resume(self):
        self.is_paused = not self.is_paused
        # 发送日志提示
        status = "暂停" if self.is_paused else "恢复"
        self.log_signal.emit(f"测试已{status}", "#F59E0B")


# 模型测试主界面（最终版）
class ModelTestUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("模型测试界面 | AutoTest Pro")
        self._setup_1080p_layout()

        self.test_thread = None
        self.test_categories = ["人脸检测", "行为识别", "情绪分析", "目标跟踪"]
        self.pr_matrix = {
            cat: {"TP": 0, "FP": 0, "FN": 0, "Precision": 0.0, "Recall": 0.0} 
            for cat in self.test_categories
        }

        # 样式表：进度条完全对齐灵巧手工具
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
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                gridline-color: #F1F5F9;
                font-family: "Microsoft YaHei", Arial;
                font-size: 11px;
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
                font-size: 12px;
            }
            QDateTimeEdit {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 6px 8px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
                background-color: white;
            }

            /* ========== 灵巧手工具同款进度条（100%一致） ========== */
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
        self.update_pr_matrix_table()
        self._center_window()

    def _setup_1080p_layout(self):
        """1080p自适应布局 + 窗口最大化限制"""
        screen_geo = QApplication.primaryScreen().geometry()
        self.setMaximumSize(
            int(screen_geo.width() * 0.9), 
            int(screen_geo.height() * 0.9)
        )
        init_w = int(screen_geo.width() * 0.85)
        init_h = int(screen_geo.height() * 0.85)
        self.setGeometry(0, 0, init_w, init_h)

    def _center_window(self):
        """窗口居中显示"""
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

        # ===================== 第一行：测试数据区域（完全不动） =====================
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)

        # 测试数据表格
        case_box = FramedGroupBox("测试数据")
        self.pr_table = QTableWidget()
        self.pr_table.setRowCount(len(self.test_categories))
        self.pr_table.setColumnCount(5)
        self.pr_table.setHorizontalHeaderLabels(["TP", "FP", "FN", "P", "R"])
        self.pr_table.setVerticalHeaderLabels(self.test_categories)
        self.pr_table.verticalHeader().setDefaultSectionSize(28)
        self.pr_table.setColumnWidth(0, 80)
        self.pr_table.setColumnWidth(1, 80)
        self.pr_table.setColumnWidth(2, 80)
        self.pr_table.setColumnWidth(3, 100)
        self.pr_table.setColumnWidth(4, 100)
        case_box.content_layout.addWidget(self.pr_table)
        row1_layout.addWidget(case_box, 5)

        # 动态日志输出
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
        log_box.content_layout.addWidget(self.log_text)
        log_box.content_layout.addLayout(log_btn_layout)
        row1_layout.addWidget(log_box, 3)

        # 功能选项（筛选条件）
        func_box = FramedGroupBox("功能选项")
        filter_group = QGroupBox("筛选条件")
        filter_layout = QFormLayout(filter_group)
        self.age_combo = QComboBox()
        self.age_combo.addItems(["全部", "18-25", "26-35", "36-45", "45+"])
        self.age_combo.setFixedHeight(32)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["全部", "男", "女"])
        self.gender_combo.setFixedHeight(32)
        self.time_edit = QDateTimeEdit()
        self.time_edit.setDateTime(QDateTime.currentDateTime())
        self.time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.time_edit.setFixedHeight(32)
        filter_layout.addRow("按年龄筛选：", self.age_combo)
        filter_layout.addRow("按性别筛选：", self.gender_combo)
        filter_layout.addRow("按时间筛选：", self.time_edit)
        func_box.content_layout.addWidget(filter_group)
        row1_layout.addWidget(func_box, 2)

        main_layout.addLayout(row1_layout)

        # ===================== 第二行：测试结果 + 执行区域（已互换） =====================
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)

        # 左侧：测试结果（占7份，带进度条）
        result_box = FramedGroupBox("测试结果")
        result_layout = QVBoxLayout()
        
        # 灵巧手同款进度条
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
        row2_layout.addWidget(result_box, 7)

        # 右侧：执行区域（占3份）
        exec_box = FramedGroupBox("执行区域")
        exec_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始测试")
        self.stop_btn = QPushButton("结束测试")
        self.pause_resume_btn = QPushButton("暂停/恢复测试")
        # 按钮尺寸统一
        self.start_btn.setFixedSize(120, 40)
        self.stop_btn.setFixedSize(120, 40)
        self.pause_resume_btn.setFixedSize(120, 40)
        # 按钮字体
        self.start_btn.setFont(QFont("Microsoft YaHei", 12))
        self.stop_btn.setFont(QFont("Microsoft YaHei", 12))
        self.pause_resume_btn.setFont(QFont("Microsoft YaHei", 12))
        # 初始状态：只有开始按钮可用
        self.stop_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        # 绑定事件
        self.start_btn.clicked.connect(self.start_test)
        self.stop_btn.clicked.connect(self.stop_test)
        self.pause_resume_btn.clicked.connect(self.pause_resume_test)
        
        exec_layout.addWidget(self.start_btn)
        exec_layout.addWidget(self.stop_btn)
        exec_layout.addWidget(self.pause_resume_btn)
        exec_box.content_layout.addLayout(exec_layout)
        row2_layout.addWidget(exec_box, 3)

        main_layout.addLayout(row2_layout)

        # 日志操作绑定
        self.copy_log_btn.clicked.connect(self.copy_log)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.save_log_btn.clicked.connect(self.save_log)

    def init_menu_bar(self):
        """初始化菜单栏（绑定实际功能）"""
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
        open_config_action.triggered.connect(self.open_config)
        config_menu.addAction(open_config_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("版权及版本信息", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    # ===================== 核心功能实现 =====================
    def append_log(self, text, color="#1E293B"):
        """添加日志信息（带时间戳和颜色）"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        char_format = self.log_text.currentCharFormat()
        char_format.setForeground(QColor(color))
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        cursor.insertText(f"[{timestamp}] {text}\n", char_format)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def copy_log(self):
        """拷贝日志到剪贴板"""
        self.log_text.selectAll()
        self.log_text.copy()
        self.append_log("日志已拷贝到剪贴板", "#10B981")

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.append_log("日志已清空", "#10B981")

    def save_log(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "", "文本文件 (*.txt)"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.append_log(f"日志已保存到：{file_path}", "#10B981")

    def update_pr_matrix_table(self):
        """更新P/R矩阵表格数据"""
        table_font = QFont("Microsoft YaHei")
        table_font.setPointSize(11)
        for row, category in enumerate(self.test_categories):
            data = self.pr_matrix[category]
            # 设置表格内容并统一字体
            self.pr_table.setItem(row, 0, QTableWidgetItem(str(data["TP"])))
            self.pr_table.setItem(row, 1, QTableWidgetItem(str(data["FP"])))
            self.pr_table.setItem(row, 2, QTableWidgetItem(str(data["FN"])))
            self.pr_table.setItem(row, 3, QTableWidgetItem(str(data["Precision"])))
            self.pr_table.setItem(row, 4, QTableWidgetItem(str(data["Recall"])))
            # 统一设置字体
            for col in range(5):
                item = self.pr_table.item(row, col)
                if item:
                    item.setFont(table_font)

    def start_test(self):
        """启动测试"""
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "测试已在运行中！")
            return
        
        # 获取筛选条件
        age_filter = self.age_combo.currentText()
        gender_filter = self.gender_combo.currentText()
        time_filter = self.time_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        
        # 创建并启动测试线程
        self.test_thread = ModelTestThread(age_filter, gender_filter, time_filter)
        self.test_thread.log_signal.connect(self.append_log)
        self.test_thread.pr_matrix_signal.connect(self.update_pr_matrix)
        self.test_thread.result_signal.connect(self.update_test_result)
        self.test_thread.progress_signal.connect(self.update_progress)
        self.test_thread.start()

        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_resume_btn.setEnabled(True)
        self.result_text.setText("测试进行中...")
        self.result_text.setStyleSheet("color: #F59E0B; padding: 16px;border: none;")
        self.progress_bar.setValue(0)

    def stop_test(self):
        """停止测试"""
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        
        # 更新UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        self.result_text.setText("测试已终止")
        self.result_text.setStyleSheet("color: #DC2626; padding: 16px;border: none;")

    def pause_resume_test(self):
        """暂停/恢复测试"""
        if not self.test_thread or not self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "暂无运行中的测试！")
            return
        
        # 切换暂停/恢复状态
        self.test_thread.pause_resume()
        if self.test_thread.is_paused:
            self.pause_resume_btn.setText("恢复测试")
            self.result_text.setText("测试已暂停")
            self.result_text.setStyleSheet("color: #9333EA; padding: 16px;")
        else:
            self.pause_resume_btn.setText("暂停/恢复测试")
            self.result_text.setText("测试进行中...")
            self.result_text.setStyleSheet("color: #F59E0B; padding: 16px;border: none;")

    def update_progress(self, progress):
        """更新进度条"""
        self.progress_bar.setValue(progress)

    def update_pr_matrix(self, pr_data):
        """更新P/R矩阵数据"""
        self.pr_matrix = pr_data
        self.update_pr_matrix_table()

    def update_test_result(self, result):
        """更新测试结果"""
        self.result_text.setText(f"测试结论：{result}")
        color = "#10B981" if result == "通过" else "#DC2626"
        self.result_text.setStyleSheet(f"color: {color}; padding: 16px;border: none;")
        # 恢复按钮状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_resume_btn.setEnabled(False)
        # 进度条拉满
        self.progress_bar.setValue(100)

    # ===================== 菜单功能实现 =====================
    def load_script(self):
        """加载脚本文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载脚本", "", "Python文件 (*.py)"
        )
        if file_path:
            self.append_log(f"已加载脚本：{file_path}", "#2563EB")

    def open_config(self):
        """打开配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开配置文件", "", "配置文件 (*.ini *.json)"
        )
        if file_path:
            self.append_log(f"已加载配置：{file_path}", "#2563EB")

    def export_test_report(self):
        """导出测试报告"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出测试报告", "", "HTML文件 (*.html)"
        )
        if file_path:
            # 生成简单的HTML报告
            report_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>模型测试报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: "Microsoft YaHei", Arial; margin: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .filter {{ margin: 20px 0; padding: 10px; background: #F8FAFC; border-radius: 6px; }}
        .log {{ margin: 20px 0; padding: 10px; background: #F1F5F9; border-radius: 6px; white-space: pre-wrap; }}
        .result {{ font-size: 18px; font-weight: bold; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>模型测试报告</h1>
        <p>生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="filter">
        <h3>筛选条件</h3>
        <p>年龄：{self.age_combo.currentText()}</p>
        <p>性别：{self.gender_combo.currentText()}</p>
        <p>时间：{self.time_edit.dateTime().toString('yyyy-MM-dd HH:mm')}</p>
    </div>
    <div class="result">
        测试结果：{self.result_text.text().replace('测试结论：', '')}
    </div>
    <div class="log">
        <h3>测试日志</h3>
        {self.log_text.toPlainText().replace('\n', '<br>')}
    </div>
</body>
</html>
            """
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            self.append_log(f"测试报告已导出：{file_path}", "#10B981")

    def show_about(self):
        """显示关于信息"""
        QMessageBox.about(
            self, 
            "关于", 
            "模型自动化测试工具 v1.0\n\n基于PyQt5开发\n兼容灵巧手测试工具样式规范"
        )


if __name__ == "__main__":
    # 高DPI适配（解决模糊问题）
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    window = ModelTestUI()
    window.show()
    sys.exit(app.exec_())