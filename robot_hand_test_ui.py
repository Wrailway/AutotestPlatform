import sys
import time
import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QAction,
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QFrame, QHeaderView, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QFont, QColor, QTextCursor, QPalette


# 统一你APP窗口的标题框样式：带边框 + 标题嵌在边框左上角
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


# 模拟测试线程
class TestThread(QThread):
    log_signal = pyqtSignal(str, str)
    progress_signal = pyqtSignal(str, int)
    result_signal = pyqtSignal(str, str)

    def __init__(self, device_id, aging_time, ports):
        super().__init__()
        self.device_id = device_id
        self.aging_time = aging_time
        self.ports = ports
        self.is_running = True
        self.is_paused = False

    def run(self):
        self.log_signal.emit(f"开始对设备 {self.device_id} 进行 {self.aging_time} 老化测试", "#2563EB")
        total_steps = 10
        for i in range(total_steps):
            if not self.is_running:
                self.log_signal.emit(f"设备 {self.device_id} 测试被用户终止", "#DC2626")
                break
            while self.is_paused and self.is_running:
                time.sleep(0.1)
            time.sleep(1)
            progress = int((i + 1) / total_steps * 100)
            self.progress_signal.emit(self.device_id, progress)
            self.log_signal.emit(f"设备 {self.device_id} 测试进度: {progress}%", "#1E293B")
        result = "通过" if self.is_running else "终止"
        self.result_signal.emit(self.device_id, result)
        self.log_signal.emit(f"设备 {self.device_id} 老化测试完成: {result}", "#10B981" if result == "通过" else "#DC2626")

    def stop(self):
        self.is_running = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False


class RobotHandTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("灵巧手测试工具 | AutoTest Pro")

        # 1080p 自适应 + 居中
        self._setup_1080p_layout()

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
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-family: "Microsoft YaHei", Arial;
                font-size: 12px;
                background-color: white;
            }
            QListWidget::item:selected {
                background-color: #EFF6FF;
                color: #2563EB;
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
                color: #475698;
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
            QMenu::item:selected {
                background-color: #EFF6FF;
                color: #2563EB;
            }
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

        self.test_thread = None
        self.devices = {
            "DEV-001": {"name": "灵巧手A", "version": "v1.2", "status": "已连接", "progress": 0, "result": "-"},
            "DEV-002": {"name": "灵巧手B", "version": "v1.3", "status": "未连接", "progress": 0, "result": "-"}
        }

        self.init_ui()
        self.init_menu_bar()
        self.update_case_table()
        self._center_window()

    def _setup_1080p_layout(self):
        screen_geo = QApplication.primaryScreen().geometry()
        self.setMaximumSize(int(screen_geo.width() * 0.9), int(screen_geo.height() * 0.9))
        init_w = int(screen_geo.width() * 0.85)
        init_h = int(screen_geo.height() * 0.85)
        self.setGeometry(0, 0, init_w, init_h)

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

        # ===================== 第一行 =====================
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        # 设备表格
        case_box = FramedGroupBox("测试数据")
        self.case_table = QTableWidget()
        self.case_table.setColumnCount(6)
        self.case_table.setHorizontalHeaderLabels(
            ["设备名称", "软件版本", "设备ID", "连接状态", "测试进展", "测试结果"]
        )
        self.case_table.verticalHeader().setDefaultSectionSize(28)
        self.case_table.setColumnWidth(0, 160)
        self.case_table.setColumnWidth(1, 90)
        self.case_table.setColumnWidth(2, 90)
        self.case_table.setColumnWidth(3, 90)
        self.case_table.setColumnWidth(4, 90)
        self.case_table.setColumnWidth(5, 90)
        case_box.content_layout.addWidget(self.case_table)
        row1.addWidget(case_box, 5)

        # 日志
        log_box = FramedGroupBox("动态日志输出")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_btns = QHBoxLayout()
        self.copy_btn = QPushButton("拷贝")
        self.clear_btn = QPushButton("清理")
        self.save_btn = QPushButton("保存")
        self.copy_btn.setFixedHeight(32)
        self.clear_btn.setFixedHeight(32)
        self.save_btn.setFixedHeight(32)
        log_btns.addWidget(self.copy_btn)
        log_btns.addWidget(self.clear_btn)
        log_btns.addWidget(self.save_btn)
        log_btns.setSpacing(10)
        log_box.content_layout.addWidget(self.log_text)
        log_box.content_layout.addLayout(log_btns)
        row1.addWidget(log_box, 3)

        # 功能选项
        func_box = FramedGroupBox("功能选项")
        func_layout = QGridLayout()
        func_layout.setSpacing(15)

        func_layout.addWidget(QLabel("老化时间:"), 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.aging_combo = QComboBox()
        self.aging_combo.addItems(["30min", "1H", "2H", "4H", "8H", "16H", "24H", "48H", "72H", "168H"])
        self.aging_combo.setFixedHeight(32)
        func_layout.addWidget(self.aging_combo, 0, 1)

        func_layout.addWidget(QLabel("端口列表:"), 1, 0, Qt.AlignRight | Qt.AlignTop)
        self.port_list = QListWidget()
        self.port_list.setMinimumHeight(120)
        func_layout.addWidget(self.port_list, 1, 1, 3, 1)

        self.refresh_btn = QPushButton("端口刷新")
        self.refresh_btn.setFixedHeight(32)
        func_layout.addWidget(self.refresh_btn, 4, 1)
        func_layout.setRowStretch(5, 1)
        func_box.content_layout.addLayout(func_layout)
        row1.addWidget(func_box, 2)

        main_layout.addLayout(row1)

        # ===================== 第二行 位置已互换 =====================
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        # 左边：测试结果（带进度条）
        result_box = FramedGroupBox("测试结果")
        result_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        self.result_text = QLabel("等待测试...")
        self.result_text.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        self.result_text.setAlignment(Qt.AlignCenter)
        self.result_text.setStyleSheet("padding: 8px;border: none;")
        
        result_layout.addWidget(self.progress_bar)
        result_layout.addWidget(self.result_text)
        result_box.content_layout.addLayout(result_layout)
        row2.addWidget(result_box, 7)

        # 右边：执行控制
        exec_box = FramedGroupBox("执行控制")
        exec_layout = QHBoxLayout()
        exec_layout.setSpacing(20)
        self.start_btn = QPushButton("开始测试")
        self.stop_btn = QPushButton("结束测试")
        self.pause_btn = QPushButton("暂停/恢复测试")
        self.start_btn.setFixedSize(120, 40)
        self.stop_btn.setFixedSize(120, 40)
        self.pause_btn.setFixedSize(120, 40)
        exec_layout.addWidget(self.start_btn)
        exec_layout.addWidget(self.stop_btn)
        exec_layout.addWidget(self.pause_btn)
        exec_layout.addStretch()
        exec_box.content_layout.addLayout(exec_layout)
        row2.addWidget(exec_box, 3)

        main_layout.addLayout(row2)

        # 绑定
        self.copy_btn.clicked.connect(self.copy_log)
        self.clear_btn.clicked.connect(self.clear_log)
        self.save_btn.clicked.connect(self.save_log)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.start_btn.clicked.connect(self.start_test)
        self.stop_btn.clicked.connect(self.stop_test)
        self.pause_btn.clicked.connect(self.pause_test)

        self.refresh_ports()

    def init_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件(File)")
        file_menu.addAction("脚本加载").triggered.connect(self.load_script)
        file_menu.addAction("输出报告").triggered.connect(self.export_report)
        file_menu.addSeparator()
        file_menu.addAction("退出").triggered.connect(self.close)

        config_menu = menubar.addMenu("配置")
        config_menu.addAction("打开配置文件").triggered.connect(self.open_config)

        option_menu = menubar.addMenu("选项")
        option_menu.addAction("主题(Optional)").triggered.connect(
            lambda: QMessageBox.information(self, "提示", "主题功能待实现")
        )

        help_menu = menubar.addMenu("帮助")
        help_menu.addAction("版权及版本信息").triggered.connect(self.show_about)

    def load_script(self):
        fp, _ = QFileDialog.getOpenFileName(self, "加载脚本", "", "*.py")
        if fp:
            self.append_log(f"加载脚本: {fp}", "#10B981")

    def export_report(self):
        fp, _ = QFileDialog.getSaveFileName(self, "导出报告", "", "*.html")
        if fp:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(f"""
<!DOCTYPE html>
<html>
<meta charset="utf-8">
<title>灵巧手测试报告</title>
<body>
<h1>灵巧手测试报告</h1>
<p>时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<h3>日志</h3>
<pre>{self.log_text.toPlainText()}</pre>
<h3>结果：{self.result_text.text()}</h3>
</body>
</html>
                """)
            self.append_log(f"报告已导出: {fp}", "#10B981")

    def open_config(self):
        fp, _ = QFileDialog.getOpenFileName(self, "打开配置", "", "*.json *.ini")
        if fp:
            self.append_log(f"加载配置: {fp}", "#10B981")

    def show_about(self):
        QMessageBox.about(self, "关于", "灵巧手测试工具 v1.0")

    def append_log(self, text, color="#1E293B"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = self.log_text.currentCharFormat()
        fmt.setForeground(QColor(color))
        cursor.insertText(f"[{ts}] {text}\n", fmt)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def copy_log(self):
        self.log_text.selectAll()
        self.log_text.copy()
        self.append_log("日志已拷贝", "#10B981")

    def clear_log(self):
        self.log_text.clear()
        self.append_log("日志已清空", "#10B981")

    def save_log(self):
        fp, _ = QFileDialog.getSaveFileName(self, "保存日志", "", "*.txt")
        if fp:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(self.log_text.toPlainText())
            self.append_log(f"日志已保存: {fp}", "#10B981")

    def refresh_ports(self):
        self.port_list.clear()
        self.port_list.addItems(["COM1", "COM2", "COM3"])
        self.append_log("端口已刷新", "#2563EB")

    def update_case_table(self):
        self.case_table.setRowCount(len(self.devices))
        font = QFont("Microsoft YaHei", 11)
        for r, (did, d) in enumerate(self.devices.items()):
            self.case_table.setItem(r, 0, QTableWidgetItem(d["name"]))
            self.case_table.setItem(r, 1, QTableWidgetItem(d["version"]))
            self.case_table.setItem(r, 2, QTableWidgetItem(did))
            self.case_table.setItem(r, 3, QTableWidgetItem(d["status"]))
            self.case_table.setItem(r, 4, QTableWidgetItem(f"{d['progress']}%"))
            self.case_table.setItem(r, 5, QTableWidgetItem(d["result"]))
            for c in range(6):
                item = self.case_table.item(r, c)
                if item:
                    item.setFont(font)

    def start_test(self):
        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "测试正在运行")
            return
        did = list(self.devices.keys())[0]
        t = self.aging_combo.currentText()
        ports = [i.text() for i in self.port_list.selectedItems()] or ["COM1"]
        self.test_thread = TestThread(did, t, ports)
        self.test_thread.log_signal.connect(self.append_log)
        self.test_thread.progress_signal.connect(self.update_progress)
        self.test_thread.result_signal.connect(self.on_finish)
        self.test_thread.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        self.result_text.setText("测试进行中...")
        self.result_text.setStyleSheet("color: #F59E0B;border: none;")

    def stop_test(self):
        if self.test_thread and self.test_thread.isRunning():
            self.test_thread.stop()
            self.test_thread.wait()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)

    def pause_test(self):
        if not self.test_thread or not self.test_thread.isRunning():
            QMessageBox.warning(self, "警告", "未运行")
            return
        if self.test_thread.is_paused:
            self.test_thread.resume()
            self.pause_btn.setText("暂停/恢复测试")
            self.append_log("已恢复", "#2563EB")
        else:
            self.test_thread.pause()
            self.pause_btn.setText("恢复测试")
            self.append_log("已暂停", "#2563EB")

    def update_progress(self, did, val):
        if did in self.devices:
            self.devices[did]["progress"] = val
            self.progress_bar.setValue(val)
            self.update_case_table()

    def on_finish(self, did, res):
        self.devices[did]["result"] = res
        self.devices[did]["progress"] = 100
        self.progress_bar.setValue(100)
        self.update_case_table()
        self.result_text.setText(f"结果：{res}")
        color = "#10B981" if res == "通过" else "#DC2626"
        self.result_text.setStyleSheet(f"color: {color};border: none;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    w = RobotHandTestWindow()
    w.show()
    sys.exit(app.exec_())