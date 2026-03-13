#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试平台主程序
=====================
功能：加载主界面，提供各测试模块入口，支持基础窗口配置、交互反馈
版权所有 © 2015-2025 上海傲意信息科技有限公司
"""

import logging
import sys
import os
import importlib
import traceback
from typing import Dict, Optional

from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QAction, QMenu, QWidget
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtSlot
)
from PyQt5 import uic

# ==============================
# 常量配置
# ==============================
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

UI_FILE_PATH = "ui/mainwindow.ui"
ICON_FILE_NAME = "icon/logo.png"

APP_TITLE = "自动化测试平台"
MENU_FILE = "文件(&F)"
MENU_EXIT = "退出(&E)"
MENU_HELP = "帮助(&H)"
MENU_ABOUT = "关于(&A)"
SHORTCUT_EXIT = "Ctrl+Q"

ABOUT_CONTENT = """
🚀 自动化测试平台 v1.0.0
==============================
版权所有 © 2015-2025 上海傲意信息科技有限公司
技术支持：021-63210200
邮箱： info@oymotion.com
官网：https://www.oymotion.com/

本软件仅限公司内部使用，未经授权禁止传播
"""

MODULE_MAPPING: Dict[str, Dict[str, str]] = {
    "应用程序测试": {
        "module_path": "app_test_ui",
        "class_name": "AppTestWindow"
    },
    "灵巧手测试": {
        "module_path": "rohand.rohand_test",
        "class_name": "RoHandTestWindow"
    },
    "AI模型测试": {
        "module_path": "model_test_ui",
        "class_name": "ModelTestUI"
    },
    "服务器测试": {
        "module_path": "server_test_ui",
        "class_name": "ServerTestUI"
    }
}

BUTTON_MODULE_MAP: Dict[str, str] = {
    "btn_app": "应用程序测试",
    "btn_robot": "灵巧手测试",
    "btn_ai": "AI模型测试",
    "btn_server": "服务器测试"
}

BUTTON_ANIM_DURATION = 150
BUTTON_ANIM_SCALE = 0.95
BUTTON_ANIM_CURVE = QEasingCurve.OutBounce

STATUS_STARTING = "🚀 正在启动 {module} 模块..."
STATUS_SUCCESS = "✅ {module} 启动成功"
STATUS_ALREADY_OPEN = "ℹ️ {module} 已打开，正在激活窗口..."
STATUS_FAILED = "❌ {module} 启动失败"
STATUS_DURATION = 3000

ERR_ICON_LOAD = "加载窗口图标失败：{msg}"
ERR_MODULE_START = "{module} 模块启动失败\n{msg}\n详细错误：{trace}"
ERR_ICON_NOT_FOUND = "图标文件不存在：{path}"
ERR_LOAD_UI_FAILED = "加载UI文件失败：{msg}"
ERR_MAIN_WINDOW_LOAD_FAILED = "加载主界面失败：{msg}"
ERR_BUTTON_BIND_FAILED = "绑定按钮事件失败：{msg}"
ERR_MODULE_CONFIG_NOT_FOUND = "未找到模块配置：{module}"
LOG_WINDOW_CLOSED = "{module} 窗口已关闭，移除记录"

DLG_TITLE_ERROR = "错误"
DLG_TITLE_START_FAILED = "启动失败"
DLG_TITLE_ABOUT = "关于"

# ==============================
# 工具函数
# ==============================
def init_logger() -> logging.Logger:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def get_absolute_path(relative_path: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

def center_window(window: QWidget) -> None:
    screen_geo = QApplication.primaryScreen().availableGeometry()
    window_geo = window.frameGeometry()
    center_point = screen_geo.center()
    window_geo.moveCenter(center_point)
    window.move(window_geo.topLeft())

# ==============================
# 核心主窗口类
# ==============================
class AutoTestMainWindow(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = init_logger()
        self.opened_windows: Dict[str, QWidget] = {}
        
        self._load_ui()
        self._init_menubar()
        self._bind_button_events()
        self._setup_window()

    def _load_ui(self) -> None:
        ui_path = get_absolute_path(UI_FILE_PATH)
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            err_msg = ERR_LOAD_UI_FAILED.format(msg=str(e))
            self.logger.error(err_msg)
            QMessageBox.critical(self, DLG_TITLE_ERROR, ERR_MAIN_WINDOW_LOAD_FAILED.format(msg=str(e)))
            sys.exit(1)

    def _init_menubar(self) -> None:
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        
        file_menu = QMenu(MENU_FILE, self)
        exit_action = QAction(MENU_EXIT, self)
        exit_action.setShortcut(SHORTCUT_EXIT)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = QMenu(MENU_HELP, self)
        about_action = QAction(MENU_ABOUT, self)
        about_action.triggered.connect(self._show_about_info)
        help_menu.addAction(about_action)
        
        menubar.addMenu(file_menu)
        menubar.addMenu(help_menu)

    def _bind_button_events(self) -> None:
        for btn_name, module_name in BUTTON_MODULE_MAP.items():
            try:
                btn = getattr(self, btn_name)
                btn.clicked.connect(lambda checked, m=module_name: self._open_module(m))
            except AttributeError as e:
                err_msg = ERR_BUTTON_BIND_FAILED.format(msg=str(e))
                self.logger.error(err_msg)

    def _setup_window(self) -> None:
        center_window(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self._set_window_icon()

    def _set_window_icon(self) -> None:
        icon_path = get_absolute_path(ICON_FILE_NAME)
        try:
            if not os.path.exists(icon_path):
                raise FileNotFoundError(ERR_ICON_NOT_FOUND.format(path=icon_path))
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            err_msg = ERR_ICON_LOAD.format(msg=str(e))
            self.logger.error(err_msg)

    @pyqtSlot()
    def _show_about_info(self) -> None:
        QMessageBox.about(self, DLG_TITLE_ABOUT, ABOUT_CONTENT)

    def _play_button_anim(self, btn: QWidget) -> None:
        orig_width = btn.width()
        orig_height = btn.height()
        
        anim_width = QPropertyAnimation(btn, b"minimumWidth")
        anim_width.setDuration(BUTTON_ANIM_DURATION)
        anim_width.setStartValue(orig_width)
        anim_width.setEndValue(int(orig_width * BUTTON_ANIM_SCALE))
        anim_width.setEasingCurve(BUTTON_ANIM_CURVE)
        
        anim_height = QPropertyAnimation(btn, b"minimumHeight")
        anim_height.setDuration(BUTTON_ANIM_DURATION)
        anim_height.setStartValue(orig_height)
        anim_height.setEndValue(int(orig_height * BUTTON_ANIM_SCALE))
        anim_height.setEasingCurve(BUTTON_ANIM_CURVE)
        
        def reset_size():
            btn.setMinimumWidth(orig_width)
            btn.setMinimumHeight(orig_height)
        
        anim_height.finished.connect(reset_size)
        anim_width.start()
        anim_height.start()

    def _open_module(self, module_name: str) -> None:
        self.statusBar().showMessage(
            STATUS_STARTING.format(module=module_name),
            STATUS_DURATION
        )
        
        btn = self.sender()
        if btn and isinstance(btn, QWidget):
            self._play_button_anim(btn)
        
        try:
            # 注册模块路径
            main_dir = os.path.dirname(os.path.abspath(__file__))
            rohand_module_dir = os.path.join(main_dir, "rohand")
            if rohand_module_dir not in sys.path:
                sys.path.insert(0, rohand_module_dir)
                self.logger.debug(f"已添加路径到sys.path: {rohand_module_dir}")
            
            # 检查已打开窗口
            if module_name in self.opened_windows:
                sub_window = self.opened_windows[module_name]
                if sub_window.isVisible():
                    sub_window.activateWindow()
                    sub_window.raise_()
                    self.statusBar().showMessage(
                        STATUS_ALREADY_OPEN.format(module=module_name),
                        STATUS_DURATION
                    )
                    return
                else:
                    del self.opened_windows[module_name]
            
            if module_name not in MODULE_MAPPING:
                raise ValueError(ERR_MODULE_CONFIG_NOT_FOUND.format(module=module_name))
            
            module_config = MODULE_MAPPING[module_name]
            mod = importlib.import_module(module_config["module_path"])
            cls = getattr(mod, module_config["class_name"])
            
            # 实例化子窗口
            sub_window = cls()
            center_window(sub_window)
            
            # 规范绑定关闭事件
            sub_window.destroyed.connect(lambda: self._on_sub_window_closed(module_name))
            
            sub_window.show()
            self.opened_windows[module_name] = sub_window
            
            self.statusBar().showMessage(
                STATUS_SUCCESS.format(module=module_name),
                STATUS_DURATION
            )
        
        except Exception as e:
            trace_msg = traceback.format_exc()
            self.logger.error(f"模块启动错误：{trace_msg}")
            err_msg = ERR_MODULE_START.format(module=module_name, msg=str(e), trace=trace_msg[:500])
            QMessageBox.critical(self, DLG_TITLE_START_FAILED, err_msg)
            self.statusBar().showMessage(
                STATUS_FAILED.format(module=module_name),
                STATUS_DURATION
            )
    
    def _on_sub_window_closed(self, module_name: str) -> None:
        if module_name in self.opened_windows:
            del self.opened_windows[module_name]
            self.logger.info(LOG_WINDOW_CLOSED.format(module=module_name))

# ==============================
# 主程序入口
# ==============================
def main() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    
    main_window = AutoTestMainWindow()
    main_window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())