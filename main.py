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
from typing import Dict, Optional

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QAction, QMenu, QWidget
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtSlot
)
from PyQt5 import uic

# ==============================
# 常量配置（所有字符串/硬编码值集中管理）
# ==============================
# 日志配置
LOG_LEVEL = logging.ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 路径配置
UI_FILE_PATH = "mainwindow.ui"
ICON_FILE_NAME = "icon/logo.png"

# 界面文本配置
APP_TITLE = "自动化测试平台"
MENU_FILE = "文件(&F)"
MENU_EXIT = "退出(&E)"
MENU_HELP = "帮助(&H)"
MENU_ABOUT = "关于(&A)"
SHORTCUT_EXIT = "Ctrl+Q"

# 关于弹窗内容
ABOUT_CONTENT = """
🚀 自动化测试平台 v1.0.0
==============================
版权所有 © 2015-2025 上海傲意信息科技有限公司
技术支持：021-63210200
邮箱： info@oymotion.com
官网：https://www.oymotion.com/

本软件仅限公司内部使用，未经授权禁止传播
"""

# 模块映射配置
MODULE_MAPPING: Dict[str, Dict[str, str]] = {
    "应用程序测试": {
        "module_path": "app_test_ui",
        "class_name": "AppTestWindow"
    },
    "灵巧手测试": {
        "module_path": "robot_hand_test_ui",
        "class_name": "RobotHandTestWindow"
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

# 按钮名称与模块名映射（提取为常量）
BUTTON_MODULE_MAP: Dict[str, str] = {
    "btn_app": "应用程序测试",
    "btn_robot": "灵巧手测试",
    "btn_ai": "AI模型测试",
    "btn_server": "服务器测试"
}

# 动画配置
BUTTON_ANIM_DURATION = 120  # 动画时长（毫秒）
BUTTON_ANIM_SCALE = 0.96    # 按钮按压缩放比例
BUTTON_ANIM_CURVE = QEasingCurve.OutQuad

# 状态栏提示文本（提取为常量）
STATUS_STARTING = "🚀 正在启动 {module} 模块..."
STATUS_SUCCESS = "✅ {module} 启动成功"
STATUS_ALREADY_OPEN = "ℹ️ {module} 已打开，正在激活窗口..."
STATUS_FAILED = "❌ {module} 启动失败"
STATUS_DURATION = 3000  # 提示显示时长（毫秒）

# 错误提示文本（提取为常量）
ERR_ICON_LOAD = "加载窗口图标失败：{msg}"
ERR_MODULE_START = "{module} 模块启动失败\n{msg}"
ERR_ICON_NOT_FOUND = "图标文件不存在：{path}"
ERR_LOAD_UI_FAILED = "加载UI文件失败：{msg}"
ERR_MAIN_WINDOW_LOAD_FAILED = "加载主界面失败：{msg}"
ERR_BUTTON_BIND_FAILED = "绑定按钮事件失败：{msg}"
ERR_MODULE_CONFIG_NOT_FOUND = "未找到模块配置：{module}"
LOG_WINDOW_CLOSED = "{module} 窗口已关闭，移除记录"

# 弹窗标题常量
DLG_TITLE_ERROR = "错误"
DLG_TITLE_START_FAILED = "启动失败"
DLG_TITLE_ABOUT = "关于"

# ==============================
# 工具函数
# ==============================
def init_logger() -> logging.Logger:
    """初始化日志配置"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def get_absolute_path(relative_path: str) -> str:
    """获取文件绝对路径（基于当前工作目录）"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

def center_window(window: QWidget) -> None:
    """
    通用窗口居中函数
    将任意QWidget窗口居中显示在屏幕中央
    
    Args:
        window: 需要居中的窗口实例
    """
    # 获取屏幕几何信息
    screen_geo = QApplication.primaryScreen().availableGeometry()
    # 获取窗口几何信息
    window_geo = window.frameGeometry()
    # 计算居中坐标
    center_point = screen_geo.center()
    window_geo.moveCenter(center_point)
    # 移动窗口到居中位置
    window.move(window_geo.topLeft())

# ==============================
# 核心主窗口类
# ==============================
class AutoTestMainWindow(QMainWindow):
    """自动化测试平台主窗口类"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.logger = init_logger()
        # 存储已打开的子窗口（模块名 -> 窗口实例）
        self.opened_windows: Dict[str, QWidget] = {}
        
        # 初始化流程
        self._load_ui()
        self._init_menubar()
        self._bind_button_events()
        self._setup_window()

    def _load_ui(self) -> None:
        """加载UI文件"""
        ui_path = get_absolute_path(UI_FILE_PATH)
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            err_msg = ERR_LOAD_UI_FAILED.format(msg=str(e))
            self.logger.error(err_msg)
            QMessageBox.critical(self, DLG_TITLE_ERROR, ERR_MAIN_WINDOW_LOAD_FAILED.format(msg=str(e)))
            sys.exit(1)

    def _init_menubar(self) -> None:
        """初始化菜单栏"""
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)  # 跨平台兼容
        
        # 文件菜单
        file_menu = QMenu(MENU_FILE, self)
        exit_action = QAction(MENU_EXIT, self)
        exit_action.setShortcut(SHORTCUT_EXIT)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = QMenu(MENU_HELP, self)
        about_action = QAction(MENU_ABOUT, self)
        about_action.triggered.connect(self._show_about_info)
        help_menu.addAction(about_action)
        
        # 添加到菜单栏
        menubar.addMenu(file_menu)
        menubar.addMenu(help_menu)

    def _bind_button_events(self) -> None:
        """绑定按钮点击事件"""
        for btn_name, module_name in BUTTON_MODULE_MAP.items():
            try:
                btn = getattr(self, btn_name)
                btn.clicked.connect(lambda checked, m=module_name: self._open_module(m))
            except AttributeError as e:
                err_msg = ERR_BUTTON_BIND_FAILED.format(msg=str(e))
                self.logger.error(err_msg)

    def _setup_window(self) -> None:
        """配置窗口基础属性"""
        # 调用通用居中函数让主窗口居中
        center_window(self)
        
        # 禁用最大化按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        
        # 设置窗口图标
        self._set_window_icon()

    def _set_window_icon(self) -> None:
        """设置窗口图标"""
        icon_path = get_absolute_path(ICON_FILE_NAME)
        try:
            if not os.path.exists(icon_path):
                raise FileNotFoundError(ERR_ICON_NOT_FOUND.format(path=icon_path))
            
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            err_msg = ERR_ICON_LOAD.format(msg=str(e))
            self.logger.error(err_msg)
            # 非致命错误，仅日志提示，不弹窗

    @pyqtSlot()
    def _show_about_info(self) -> None:
        """显示关于信息弹窗"""
        QMessageBox.about(self, DLG_TITLE_ABOUT, ABOUT_CONTENT)

    def _play_button_anim(self, btn: QWidget) -> None:
        """播放按钮点击动画"""
        orig_height = btn.height()
        anim = QPropertyAnimation(btn, b"minimumHeight")
        anim.setDuration(BUTTON_ANIM_DURATION)
        anim.setStartValue(orig_height)
        anim.setEndValue(int(orig_height * BUTTON_ANIM_SCALE))
        anim.setEasingCurve(BUTTON_ANIM_CURVE)
        anim.finished.connect(lambda: btn.setMinimumHeight(orig_height))
        anim.start()

    def _open_module(self, module_name: str) -> None:
        """
        打开指定测试模块（确保单实例+子窗口居中）
        
        Args:
            module_name: 模块名称（需匹配MODULE_MAPPING）
        """
        # 状态栏提示
        self.statusBar().showMessage(
            STATUS_STARTING.format(module=module_name),
            STATUS_DURATION
        )
        
        # 播放按钮动画
        btn = self.sender()
        if btn and isinstance(btn, QWidget):
            self._play_button_anim(btn)
        
        # 加载模块
        try:
            # 检查模块是否已打开
            if module_name in self.opened_windows:
                sub_window = self.opened_windows[module_name]
                # 检查窗口是否被手动关闭（若已关闭则移除记录）
                if sub_window.isVisible():
                    # 激活并置顶已打开的窗口
                    sub_window.activateWindow()
                    sub_window.raise_()  # 置顶窗口
                    self.statusBar().showMessage(
                        STATUS_ALREADY_OPEN.format(module=module_name),
                        STATUS_DURATION
                    )
                    return
                else:
                    # 窗口已关闭，移除记录
                    del self.opened_windows[module_name]
            
            if module_name not in MODULE_MAPPING:
                raise ValueError(ERR_MODULE_CONFIG_NOT_FOUND.format(module=module_name))
            
            module_config = MODULE_MAPPING[module_name]
            # 动态导入模块
            mod = importlib.import_module(module_config["module_path"])
            cls = getattr(mod, module_config["class_name"])
            
            # 实例化子窗口
            sub_window = cls()
            
            # 子窗口创建后先居中再显示
            center_window(sub_window)
            
            # 绑定窗口关闭事件，移除记录
            sub_window.destroyed.connect(lambda: self._on_sub_window_closed(module_name))
            sub_window.show()
            
            # 存储已打开的窗口
            self.opened_windows[module_name] = sub_window
            
            # 更新状态栏
            self.statusBar().showMessage(
                STATUS_SUCCESS.format(module=module_name),
                STATUS_DURATION
            )
        
        except Exception as e:
            err_msg = ERR_MODULE_START.format(module=module_name, msg=str(e))
            self.logger.error(err_msg)
            QMessageBox.critical(self, DLG_TITLE_START_FAILED, err_msg)
            self.statusBar().showMessage(
                STATUS_FAILED.format(module=module_name),
                STATUS_DURATION
            )
    
    def _on_sub_window_closed(self, module_name: str) -> None:
        """子窗口关闭时移除记录"""
        if module_name in self.opened_windows:
            del self.opened_windows[module_name]
            self.logger.info(LOG_WINDOW_CLOSED.format(module=module_name))

# ==============================
# 主程序入口
# ==============================
def main() -> int:
    """主程序入口函数"""
    # 高DPI适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    
    # 启动主窗口
    main_window = AutoTestMainWindow()
    main_window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())