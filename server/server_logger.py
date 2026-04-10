#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵巧手测试工具 - 日志管理模块
支持文件日志 + GUI界面日志输出，可动态调整日志级别
"""
import logging
import os
import time
from datetime import datetime


class ServerHandLogger:
    """
    日志管理器类
    封装日志配置、文件输出、GUI界面输出、日志级别控制功能
    """

    def __init__(self, log_text_edit=None):
        """
        初始化日志管理器
        :param log_text_edit: PyQt5 QTextEdit 组件，用于界面日志展示（可选）
        """
        # 日志输出组件与基础配置
        self.log_text_edit = log_text_edit
        self.log_enable = 'y'  # 日志总开关：y=启用，n=禁用
        self.log_level = 'INFO'  # 默认日志级别

        # 设置根日志器级别为最低，确保所有日志均可被捕获
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        # 初始化日志处理器
        self._setup_file_logging()
        self._setup_gui_logging()

    def custom_logger(self, level='INFO', message=''):
        """
        自定义日志输出核心方法
        :param message: 日志消息内容
        :param level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        """
        level = level.upper()

        # 日志总开关关闭则不输出
        if self.log_enable == 'n':
            return

        logger = logging.getLogger("APP")
        if level == 'DEBUG':
            logger.debug(message)
        elif level == 'INFO':
            logger.info(message)
        elif level == 'WARNING':
            logger.warning(message)
        elif level == 'ERROR':
            logger.error(message)
        elif level == 'CRITICAL':
            logger.critical(message)
        else:
            raise ValueError("无效的日志级别，请选择 'DEBUG'、'INFO'、'WARNING'、'ERROR'、'CRITICAL' 之一")

    def set_log_level(self, level):
        """
        动态设置日志输出级别
        :param level: 目标级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        """
        level = level.upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        if level not in valid_levels:
            raise ValueError("无效的日志级别，请选择 'DEBUG'、'INFO'、'WARNING'、'ERROR'、'CRITICAL' 之一")

        self.log_level = level

        # 日志级别映射
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        current_level = level_map.get(level, logging.INFO)

        # 更新文件日志处理器级别
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if getattr(handler, "_is_client_file_handler", False):
                handler.setLevel(current_level)

        # 重新初始化GUI日志，应用新级别
        self._setup_gui_logging()

    def _setup_file_logging(self):
        """配置文件日志输出：自动创建日志目录、按日期生成日志文件"""
        # 日志目录路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_folder = os.path.normpath(os.path.join(base_dir, "..", "log"))
        os.makedirs(log_folder, exist_ok=True)

        # 日志文件名
        timestamp = str(int(time.time()))
        current_date = time.strftime("%Y-%m-%d", time.localtime())
        log_file_name = os.path.join(log_folder, f"Rohand_ClientTest_log_{current_date}_{timestamp}.txt")

        # 文件处理器配置
        file_handler = logging.FileHandler(log_file_name, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(log_format)
        setattr(file_handler, "_is_client_file_handler", True)

        # 避免重复添加handler
        root_logger = logging.getLogger()
        for h in root_logger.handlers:
            if getattr(h, "_is_client_file_handler", False):
                return
        root_logger.addHandler(file_handler)

    def _setup_gui_logging(self):
        """配置GUI界面日志输出：线程安全输出到QTextEdit"""
        if not self.log_text_edit:
            return

        from PyQt5.QtCore import QTimer

        class GuiLogHandler(logging.Handler):
            """
            自定义GUI日志处理器
            将日志安全投递到主线程QTextEdit，避免跨线程崩溃
            """

            def __init__(self, append_fn, logger_instance):
                super().__init__()
                self.append_fn = append_fn
                self.logger_instance = logger_instance
                self._is_rohand_gui_handler = True

            def emit(self, record):
                try:
                    # 日志级别过滤
                    level_map = {
                        'DEBUG': logging.DEBUG,
                        'INFO': logging.INFO,
                        'WARNING': logging.WARNING,
                        'ERROR': logging.ERROR,
                        'CRITICAL': logging.CRITICAL
                    }
                    current_level = level_map.get(self.logger_instance.log_level, logging.INFO)

                    if record.levelno >= current_level:
                        msg = self.format(record)
                        QTimer.singleShot(0, lambda m=msg: self.append_fn(m))
                except Exception:
                    pass

        # 创建并配置GUI处理器
        handler = GuiLogHandler(self.log_text_edit.append, self)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        # 移除旧GUI处理器
        root_logger = logging.getLogger()
        for h in root_logger.handlers:
            if getattr(h, "_is_rohand_gui_handler", False):
                root_logger.removeHandler(h)

        root_logger.addHandler(handler)

    def log(self, msg: str, level='INFO'):
        """
        外部调用的日志输出方法
        :param msg: 日志内容
        :param level: 日志级别，默认INFO
        """
        self.custom_logger(level=level, message=msg)

        # 控制台输出
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level.upper()}] {msg}"
        print(log_msg)

    def set_log_text_edit(self, log_text_edit):
        """
        动态设置日志展示组件
        :param log_text_edit: QTextEdit实例
        """
        self.log_text_edit = log_text_edit
        self._setup_gui_logging()