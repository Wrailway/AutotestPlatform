#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any


def cache_default_style(window: Any) -> None:
    """
    缓存窗口进入程序时的默认 QSS（用于"默认主题"还原）。
    """
    window._default_qss = window.styleSheet() or ""


def blue_style() -> str:
    """
    蓝色主题样式（默认主题）
    """
    return """
        /* 主窗口基础样式 */
        QMainWindow {background-color: #f9fafb;}

        /* 分组框样式 */
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            border: 2px solid #e5e7eb;
            border-top-color: #f3f4f6;
            border-left-color: #f3f4f6;
            border-radius: 8px;
            margin-top: 12px;
            background-color: #ffffff;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px;
            color: #2563eb;
            font-size: 17px;
            font-weight: 700;
        }

        /* 按钮样式 */
        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4d9eff,stop:1 #3b82f6);
            color: white;
            border: 3px solid;
            border-color: #73b6ff #3b82f6 #3b82f6 #73b6ff;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 15px;
            font-weight: 500;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #73b6ff,stop:1 #4d9eff);
            border-color: #99ccff #4d9eff #4d9eff #99ccff;
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #2563eb,stop:1 #1e40af);
            border-color: #2563eb #4d9eff #4d9eff #2563eb;
            padding-left: 8px;
            padding-top: 8px;
        }
        QPushButton#start_test_btn, QPushButton#pause_test_btn, QPushButton#stop_test_btn {
            font-size: 20px;
            font-weight: 600;
        }

        /* 标签样式 */
        QLabel {
            font-size: 15px;
            color: #374151;
        }
        QLabel#total_case_label, QLabel#total_case_value {color: #4b5563; font-weight: 600;}
        QLabel#success_case_label, QLabel#success_case_value {color: #10b981; font-weight: 600;}
        QLabel#fail_case_label, QLabel#fail_case_value {color: #ef4444; font-weight: 600;}
        QLabel#skip_case_label, QLabel#skip_case_value {color: #f59e0b; font-weight: 600;}

        /* 下拉框样式 */
        QComboBox {
            border: 3px solid;
            border-color: #f3f4f6 #d1d5db #d1d5db #f3f4f6;
            border-radius: 6px;
            padding: 4px 8px;
            background-color: white;
            min-height: 28px;
            font-size: 15px;
        }
        QComboBox::drop-down {border: none;}
        QComboBox::down-arrow {width: 14px; height: 14px;}
        QComboBox QAbstractItemView {
            border: 3px solid #3b82f6;
            border-color: #73b6ff #3b82f6 #3b82f6 #73b6ff;
            border-radius: 6px;
            background-color: white;
            selection-background-color: #e6f2ff;
            selection-color: #2563eb;
            font-size: 15px;
        }

        /* 复选框样式 */
        QCheckBox {
            font-size: 15px;
            color: #374151;
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 6px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 3px solid;
            border-color: #f3f4f6 #d1d5db #d1d5db #f3f4f6;
            border-radius: 4px;
            background-color: white;
            margin-right: 8px;
        }
        QCheckBox::indicator:checked {background-color: #3b82f6;}
        QCheckBox::indicator:hover {
            border-color: #d1d5db #9ca3af #9ca3af #d1d5db;
        }
        /* 端口列表复选框特殊样式 */
        QCheckBox#port_checkbox {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
        }
        QCheckBox#port_checkbox:hover {
            background-color: #f9fafb;
            border-color: #d1d5db;
        }

        /* 表格样式 */
        QTableWidget {
            border: 3px solid;
            border-color: #f3f4f6 #d1d5db #d1d5db #f3f4f6;
            border-radius: 6px;
            background-color: white;
            gridline-color: #e5e7eb;
            font-size: 15px;
            stretch: 1;
        }
        QTableWidget::item {padding: 20px;}
        QTableWidget::item:selected {
            background-color: #e6f2ff;
            color: #2563eb;
        }
        QHeaderView::section {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f3f4f6,stop:1 #e5e7eb);
            border: none;
            border-bottom: 2px solid #d1d5db;
            padding: 8px;
            font-weight: 600;
            color: #2563eb;
            border-radius: 4px;
            font-size: 15px;
        }

        /* 日志框样式 */
        QTextEdit#log_text_edit {
            border: 3px solid;
            border-color: #f3f4f6 #d1d5db #d1d5db #f3f4f6;
            border-radius: 6px;
            background-color: #ffffff;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 14px;
            color: #1f2937;
        }

        /* 进度条样式 */
        QProgressBar {
            border: 3px solid;
            border-color: #f3f4f6 #d1d5db #d1d5db #f3f4f6;
            border-radius: 6px;
            text-align: center;
            background-color: #f3f4f6;
            font-size: 15px;
            color: #ffffff;
            font-weight: 600;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4d9eff,stop:1 #3b82f6);
            border-radius: 4px;
            border: 1px solid #3b82f6;
        }

        /* 菜单栏样式 */
        QMenuBar {
            background-color: #f9fafb;
            border-bottom: 2px solid #e5e7eb;
            font-size: 15px;
            font-weight: 500;
            color: #1f2937;
        }
        QMenuBar::item {
            padding: 8px 18px;
            margin: 2px;
            border-radius: 6px;
            color: #1f2937;
            background-color: transparent;
            border: 2px solid transparent;
        }
        QMenuBar::item:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4d9eff,stop:1 #3b82f6);
            color: white;
            border-color: #73b6ff #3b82f6 #3b82f6 #73b6ff;
        }
        QMenu {
            background-color: #ffffff;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 8px 0;
            font-size: 15px;
            color: #1f2937;
        }
        QMenu::item {
            padding: 8px 28px;
            margin: 0 4px;
            border-radius: 6px;
            color: #1f2937;
            border: 2px solid transparent;
        }
        QMenu::item:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4d9eff,stop:1 #3b82f6);
            color: white;
            border-color: #73b6ff #3b82f6 #3b82f6 #73b6ff;
        }
        QMenu::separator {
            height: 2px;
            background-color: #e5e7eb;
            margin: 6px 10px;
        }

        /* 端口列表滚动区域样式 */
        QScrollArea#port_scroll_area {
            border: none;
            background-color: transparent;
        }
        QScrollArea#port_scroll_area QWidget#scroll_content_widget {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            background-color: #ffffff;
            padding: 10px;
        }
        QScrollBar:vertical {
            width: 8px;
            background-color: #f3f4f6;
            border-radius: 4px;
            margin: 0 2px;
        }
        QScrollBar::handle:vertical {
            background-color: #d1d5db;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #9ca3af;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
    """


def apply_default_style(window: Any) -> None:
    """
    应用默认蓝色主题
    """
    window.setStyleSheet(blue_style())



def black_style() -> str:
    return """
        QMainWindow { background-color: #0b1220; }

        QWidget { color: #e5e7eb; font-size: 15px; }

        QGroupBox {
            background-color: #0f172a;
            border: 2px solid #243047;
            border-radius: 10px;
            margin-top: 12px;
            padding-top: 8px;
            font-weight: 600;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px;
            color: #93c5fd;
            font-size: 17px;
            font-weight: 700;
        }

        QLabel { color: #cbd5e1; }
        QLabel#success_case_label, QLabel#success_case_value { color: #34d399; font-weight: 700; }
        QLabel#fail_case_label, QLabel#fail_case_value { color: #fb7185; font-weight: 700; }
        QLabel#skip_case_label, QLabel#skip_case_value { color: #fbbf24; font-weight: 700; }
        QLabel#total_case_label, QLabel#total_case_value { color: #94a3b8; font-weight: 700; }

        QPushButton {
            background-color: #1f2a44;
            color: #e5e7eb;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #263455;
            border-color: #60a5fa;
        }
        QPushButton:pressed {
            background-color: #16213a;
            border-color: #93c5fd;
            padding-left: 8px;
            padding-top: 8px;
        }
        QPushButton#start_test_btn, QPushButton#pause_test_btn, QPushButton#stop_test_btn {
            font-size: 20px;
            font-weight: 700;
        }

        QComboBox {
            background-color: #0b1220;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 4px 8px;
            min-height: 28px;
            color: #e5e7eb;
        }
        QComboBox:hover { border-color: #60a5fa; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            background-color: #0f172a;
            border: 2px solid #334155;
            border-radius: 8px;
            selection-background-color: #1d4ed8;
            selection-color: #ffffff;
        }


        QCheckBox { 
            color: #cbd5e1; 
            padding: 8px 12px; 
            margin: 4px 0; 
            border-radius: 8px;
            background-color: transparent;
        }
        QCheckBox#port_checkbox { 
            background-color: #0b1220; 
            border: 1px solid #243047; 
        }

        QCheckBox#port_checkbox:hover { background-color: #0f172a; border-color: #334155; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #334155;
            border-radius: 4px;
            background-color: #0b1220;
            margin-right: 8px;
        }
        QCheckBox::indicator:checked { background-color: #60a5fa; border-color: #93c5fd; }

        QTableWidget {
            background-color: #0b1220;
            border: 2px solid #243047;
            border-radius: 10px;
            gridline-color: #1f2a44;
            selection-background-color: #1d4ed8;
        }
        QTableWidget::item {
            padding: 10px;
            background-color: #0b1220;
            color: #e5e7eb;
        }
        QTableWidget::item:selected {
            background-color: #1d4ed8;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #0f172a;
            border: none;
            border-bottom: 2px solid #243047;
            padding: 8px;
            font-weight: 700;
            color: #93c5fd;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        QHeaderView::section:vertical {
            background-color: #0b1220;
            border: none;
            padding: 8px;
            font-weight: 700;
            color: #93c5fd;
        }
        QTableWidget QHeaderView::section:vertical {
            background-color: #0b1220;
            color: #93c5fd;
            border: none;
            min-width: 30px;
        }
        QTableWidget QHeaderView::vertical {
            background-color: #0b1220;
            border: none;
        }
        QTableWidget::corner {
            background-color: #0b1220;
            border: none;
        }
        QTextEdit#log_text_edit {
            background-color: #0b1220;
            border: 2px solid #243047;
            border-radius: 10px;
            color: #e5e7eb;
            selection-background-color: #1d4ed8;
            selection-color: #ffffff;
        }

        QProgressBar {
            border: 2px solid #243047;
            border-radius: 10px;
            text-align: center;
            background-color: #0f172a;
            color: #e5e7eb;
            font-weight: 700;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #60a5fa, stop:1 #2563eb);
            border-radius: 8px;
            margin: 1px;
        }

        QMenuBar {
            background-color: #0f172a;
            border-bottom: 2px solid #243047;
            color: #e5e7eb;
            font-weight: 600;
        }
        QMenuBar::item {
            padding: 8px 18px;
            margin: 2px;
            border-radius: 8px;
            background-color: transparent;
            border: 2px solid transparent;
        }
        QMenuBar::item:selected {
            background-color: #1f2a44;
            border-color: #60a5fa;
        }
        QMenu {
            background-color: #0f172a;
            border: 2px solid #243047;
            border-radius: 10px;
            padding: 8px 0;
        }
        QMenu::item {
            padding: 8px 28px;
            margin: 0 4px;
            border-radius: 8px;
            border: 2px solid transparent;
        }
        QMenu::item:selected {
            background-color: #1f2a44;
            border-color: #60a5fa;
        }
        QMenu::separator {
            height: 2px;
            background-color: #243047;
            margin: 6px 10px;
        }

        QScrollArea#port_scroll_area { border: none; background-color: transparent; }
        QScrollArea#port_scroll_area QWidget#scroll_content_widget {
            border: 2px solid #243047;
            border-radius: 10px;
            background-color: #0f172a;
            padding: 10px;
        }
        QScrollBar:vertical {
            width: 8px;
            background-color: #0f172a;
            border-radius: 4px;
            margin: 0 2px;
        }
        QScrollBar::handle:vertical {
            background-color: #334155;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background-color: #60a5fa; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        
        QMenu::separator {
            height: 2px;
            background-color: #243047;
            margin: 6px 10px;
        }

        QScrollArea#port_scroll_area { 
            border: none; 
            background-color: transparent; 
        }
        QScrollArea#port_scroll_area QWidget#scroll_content_widget {
            border: 2px solid #243047;
            border-radius: 10px;
            background-color: #0b1220;
            padding: 10px;
        }


        /* 关于对话框样式 */
        QMessageBox { background-color: white; color: #333333; }
        QMessageBox QLabel { color: #333333; font-weight: normal; }
        QMessageBox QPushButton {
            background-color: #1f2a44;
            color: #e5e7eb;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 600;
        }
        QMessageBox QPushButton:hover {
            background-color: #263455;
            border-color: #60a5fa;
        }
        """


def green_style() -> str:
    return """
        QMainWindow { background-color: #f6fbf8; }

        QWidget { color: #0f172a; font-size: 15px; }

        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            color: #0f172a;
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            margin-top: 12px;
            background-color: #ffffff;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px;
            color: #16a34a;
            font-size: 17px;
            font-weight: 800;
        }

        QPushButton {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #22c55e, stop:1 #16a34a);
            color: #ffffff;
            border: 2px solid #16a34a;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 700;
        }
        QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4ade80, stop:1 #22c55e); }
        QPushButton:pressed { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #15803d, stop:1 #166534); padding-left: 8px; padding-top: 8px; }
        QPushButton#start_test_btn, QPushButton#pause_test_btn, QPushButton#stop_test_btn { font-size: 20px; font-weight: 800; }

        QComboBox {
            border: 2px solid #bbf7d0;
            border-radius: 8px;
            padding: 4px 8px;
            background-color: #ffffff;
            min-height: 28px;
        }
        QComboBox:hover { border-color: #22c55e; }
        QComboBox::drop-down { border: none; }
        QComboBox QAbstractItemView {
            border: 2px solid #22c55e;
            border-radius: 8px;
            background-color: #ffffff;
            selection-background-color: #dcfce7;
            selection-color: #166534;
        }

        QCheckBox { padding: 8px 12px; margin: 4px 0; border-radius: 8px; }
        QCheckBox#port_checkbox { background-color: #ffffff; border: 1px solid #dcfce7; }
        QCheckBox#port_checkbox:hover { background-color: #f0fdf4; border-color: #bbf7d0; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 2px solid #bbf7d0;
            border-radius: 4px;
            background-color: #ffffff;
            margin-right: 8px;
        }
        QCheckBox::indicator:checked { background-color: #22c55e; border-color: #16a34a; }

        QTableWidget {
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            background-color: #ffffff;
            gridline-color: #dcfce7;
        }
        QTableWidget::item { padding: 10px; }
        QTableWidget::item:selected { background-color: #dcfce7; color: #166534; }
        QHeaderView::section {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ecfdf5, stop:1 #dcfce7);
            border: none;
            border-bottom: 2px solid #bbf7d0;
            padding: 8px;
            font-weight: 800;
            color: #16a34a;
            border-radius: 6px;
        }

        QTextEdit#log_text_edit {
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            background-color: #ffffff;
            color: #0f172a;
            selection-background-color: #dcfce7;
            selection-color: #166534;
        }

        QProgressBar {
            border: 2px solid #bbf7d0;
            border-radius: 10px;
            text-align: center;
            background-color: #ecfdf5;
            font-size: 15px;
            color: #0f172a;
            font-weight: 800;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4ade80, stop:1 #16a34a);
            border-radius: 8px;
            margin: 1px;
        }

        QMenuBar {
            background-color: #f6fbf8;
            border-bottom: 2px solid #dcfce7;
            font-size: 15px;
            font-weight: 600;
            color: #0f172a;
        }
        QMenuBar::item {
            padding: 8px 18px;
            margin: 2px;
            border-radius: 8px;
            background-color: transparent;
            border: 2px solid transparent;
        }
        QMenuBar::item:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4ade80, stop:1 #22c55e);
            color: #ffffff;
            border-color: #22c55e;
        }

        QMenu {
            background-color: #ffffff;
            border: 2px solid #dcfce7;
            border-radius: 10px;
            padding: 8px 0;
            color: #0f172a;
        }
        QMenu::item {
            padding: 8px 28px;
            margin: 0 4px;
            border-radius: 8px;
            border: 2px solid transparent;
        }
        QMenu::item:selected {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4ade80, stop:1 #22c55e);
            color: #ffffff;
            border-color: #22c55e;
        }
        QMenu::separator { height: 2px; background-color: #dcfce7; margin: 6px 10px; }

        QScrollArea#port_scroll_area { border: none; background-color: transparent; }
        QScrollArea#port_scroll_area QWidget#scroll_content_widget {
            border: 2px solid #dcfce7;
            border-radius: 10px;
            background-color: #ffffff;
            padding: 10px;
        }
        QScrollBar:vertical {
            width: 8px;
            background-color: #ecfdf5;
            border-radius: 4px;
            margin: 0 2px;
        }
        QScrollBar::handle:vertical {
            background-color: #bbf7d0;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background-color: #22c55e; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

        /* 关于对话框样式 */
        QMessageBox { background-color: white; color: #333333; }
        QMessageBox QLabel { color: #333333; font-weight: normal; }
        QMessageBox QPushButton {
            background-color: #1f2a44;
            color: #e5e7eb;
            border: 2px solid #334155;
            border-radius: 8px;
            padding: 6px 12px;
            font-weight: 600;
        }
        QMessageBox QPushButton:hover {
            background-color: #263455;
            border-color: #60a5fa;
        }
        """


def apply_black_style(window: Any) -> None:
    window.setStyleSheet(black_style())


def apply_green_style(window: Any) -> None:
    window.setStyleSheet(green_style())

