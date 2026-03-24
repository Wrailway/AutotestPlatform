#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import time
from datetime import datetime

class RoHandLogger:
    """
    RoHand 日志管理器
    封装了日志的配置和打印功能
    """
    
    def __init__(self, log_text_edit=None):
        """
        初始化日志管理器
        :param log_text_edit: QTextEdit 组件，用于显示日志（可选）
        """
        self.log_text_edit = log_text_edit
        self.log_enable = 'y'  # 日志启用状态
        self.log_level = 'INFO'  # 默认日志级别
        
        # 设置根日志记录器的级别为最低，确保所有级别的日志都能被捕获
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        self._setup_file_logging()
        self._setup_gui_logging()
    
    def custom_logger(self, level='INFO', message=''):
        """
        自定义日志输出函数
        :param message: 要记录的日志消息内容
        :param level: 日志级别，可选值为 'DEBUG'、'INFO'、'WARNING'、'ERROR'、'CRITICAL'，默认是 'INFO'
        """
        level = level.upper()
        
        if self.log_enable == 'n':
            return
            
        logger = logging.getLogger("rohand")
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
        设置日志级别
        :param level: 日志级别，可选值为 'DEBUG'、'INFO'、'WARNING'、'ERROR'、'CRITICAL'
        """
        level = level.upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            raise ValueError("无效的日志级别，请选择 'DEBUG'、'INFO'、'WARNING'、'ERROR'、'CRITICAL' 之一")
        
        self.log_level = level
        # 更新文件 handler 的日志级别
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        current_level = level_map.get(level, logging.INFO)
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if getattr(handler, "_is_client_file_handler", False):
                handler.setLevel(current_level)
        
        # 重新设置 GUI 日志处理器，以应用新的日志级别
        self._setup_gui_logging()
    
    def _setup_file_logging(self):
        """
        设置文件日志
        """
        # 当前文件所在目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_folder = os.path.normpath(os.path.join(base_dir, "..", "log"))
        os.makedirs(log_folder, exist_ok=True)

        timestamp = str(int(time.time()))
        current_date = time.strftime("%Y-%m-%d", time.localtime())
        log_file_name = os.path.join(log_folder, f"ClientTest_log_{current_date}_{timestamp}.txt")

        file_handler = logging.FileHandler(log_file_name, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(log_format)
        setattr(file_handler, "_is_client_file_handler", True)

        root_logger = logging.getLogger()
        # 避免重复添加同类 handler
        for h in root_logger.handlers:
            if getattr(h, "_is_client_file_handler", False):
                return
        root_logger.addHandler(file_handler)
    
    def _setup_gui_logging(self):
        """
        设置 GUI 日志
        """
        if not self.log_text_edit:
            return
        
        from PyQt5.QtCore import QTimer
        
        class GuiLogHandler(logging.Handler):
            """将日志追加到 QTextEdit（线程安全投递到主线程）。"""

            def __init__(self, append_fn, logger_instance):
                super().__init__()
                self.append_fn = append_fn
                self.logger_instance = logger_instance
                self._is_rohand_gui_handler = True

            def emit(self, record):
                try:
                    # 根据当前设置的日志级别过滤
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
        
        handler = GuiLogHandler(self.log_text_edit.append, self)
        # 设置为最低级别，让处理器自己过滤
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        root_logger = logging.getLogger()
        # 移除旧的 GUI 处理器
        for h in root_logger.handlers:
            if getattr(h, "_is_rohand_gui_handler", False):
                root_logger.removeHandler(h)
        # 添加新的 GUI 处理器
        root_logger.addHandler(handler)
    
    def log(self, msg: str, level='INFO'):
        """
        打印日志
        :param msg: 日志消息
        :param level: 日志级别，默认是 'INFO'
        """
        self.custom_logger(level=level, message=msg)
        
        # 打印到控制台
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level.upper()}] {msg}"
        print(log_msg)
        
        # 打印到 GUI - 这里不再直接追加，而是通过 custom_logger 触发 logging 系统，由 GuiLogHandler 处理
    
    def set_log_text_edit(self, log_text_edit):
        """
        设置日志显示组件
        :param log_text_edit: QTextEdit 组件
        """
        self.log_text_edit = log_text_edit
        self._setup_gui_logging()