import logging
import sys
import os
import importlib
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QAction, QMenu
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve  # 动画相关依赖
)
from PyQt5 import uic

# 初始化logger（如果没定义的话）
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

class AutoTestMain(QMainWindow):
    def __init__(self):
        super().__init__()
        # 纯加载UI，不修改任何样式
        uic.loadUi("mainwindow.ui", self)
        
        # 初始化中文菜单栏（核心新增）
        self._init_menubar()
        
        # 绑定按钮事件（匹配新的按钮名称）
        self._bind_button_events()
        # 窗口基础设置
        self._window_settings()

    def _init_menubar(self):
        """初始化中文菜单栏：文件 + 帮助"""
        # 获取菜单栏（清空原有内容，避免冲突）
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)  # 强制在窗口内显示（兼容Mac/Windows）
        
        # ---------------------- 1. 文件菜单（仅保留退出） ----------------------
        file_menu = QMenu("文件(&F)", self)
        
        # 退出程序（带快捷键）
        exit_action = QAction("退出(&E)", self)
        exit_action.setShortcut("Ctrl+Q")  # 快捷键Ctrl+Q
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ---------------------- 2. 帮助菜单（公司版权+版本介绍） ----------------------
        help_menu = QMenu("帮助(&H)", self)
        
        # 关于/版本版权信息
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_company_info)
        help_menu.addAction(about_action)
        
        # 将菜单添加到菜单栏
        menubar.addMenu(file_menu)
        menubar.addMenu(help_menu)

    def _show_company_info(self):
        """显示公司版权及版本介绍"""
        # 可根据你的实际信息修改以下内容
        company_info = """
        🚀 自动化测试平台 v1.0.0
        ==============================
        版权所有 © 2015-2025 上海傲意信息科技有限公司
        技术支持：021-63210200
        邮箱： info@oymotion.com
        官网：https://www.oymotion.com/
        
        本软件仅限公司内部使用，未经授权禁止传播
        """
        QMessageBox.about(self, "关于", company_info)

    # ---------------------- 原有功能完全保留 ----------------------
    def _bind_button_events(self):
        # 匹配UI里新的按钮名称：btn_app/btn_robot/btn_ai/btn_server
        self.btn_app.clicked.connect(lambda: self._open_module("应用程序测试"))
        self.btn_robot.clicked.connect(lambda: self._open_module("灵巧手测试"))
        self.btn_ai.clicked.connect(lambda: self._open_module("AI模型测试"))
        self.btn_server.clicked.connect(lambda: self._open_module("服务器测试"))

    def _window_settings(self):
        # 窗口居中
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        # 禁用最大化
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        
        try:
            # 从文件路径加载图标（修复核心错误：self.window → self）
            current_dir = os.getcwd()
            config_file_name = "icon/logo.png"
            config_file_path = os.path.join(current_dir, config_file_name)
            
            # 检查文件是否存在（增加容错）
            if os.path.exists(config_file_path):
                icon = QIcon(config_file_path)
                self.setWindowIcon(icon)  # 正确写法：self 直接调用setWindowIcon
            else:
                raise FileNotFoundError(f"图标文件不存在：{config_file_path}")
        except Exception as e:
            logger.error(f"加载窗口图标失败：{str(e)}")
            # 可选：弹窗提示（如果需要）
            # QMessageBox.warning(self, "提示", f"加载窗口图标失败：{str(e)}")

    def _open_module(self, module_name):
        self.statusBar().showMessage(f"🚀 正在启动 {module_name} 模块...", 2000)

        btn = self.sender()
        if btn:
            orig_h = btn.height()
            anim = QPropertyAnimation(btn, b"minimumHeight")
            anim.setDuration(120)
            anim.setStartValue(orig_h)
            anim.setEndValue(int(orig_h * 0.96))
            anim.setEasingCurve(QEasingCurve.OutQuad)
            anim.finished.connect(lambda: btn.setMinimumHeight(orig_h))
            anim.start()

        try:
            module_mapping = {
                "应用程序测试": {"module_path": "app_test_ui", "class_name": "AppTestWindow"},
                "灵巧手测试": {"module_path": "robot_hand_test_ui", "class_name": "RobotHandTestWindow"},
                "AI模型测试": {"module_path": "model_test_ui", "class_name": "ModelTestUI"},
                "服务器测试": {"module_path": "server_test_ui", "class_name": "ServerTestUI"}
            }
            info = module_mapping[module_name]
            mod = importlib.import_module(info["module_path"])
            cls = getattr(mod, info["class_name"])
            self.current_sub_window = cls()
            self.current_sub_window.show()
            self.statusBar().showMessage(f"✅ {module_name} 启动成功", 3000)
        except Exception as e:
            QMessageBox.critical(self, "启动失败", f"{module_name} 模块启动失败\n{str(e)}")
            self.statusBar().showMessage(f"❌ {module_name} 启动失败", 3000)

if __name__ == "__main__":
    # DPI适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = AutoTestMain()
    window.show()
    sys.exit(app.exec_())