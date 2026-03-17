"""
@File    : auto_test_app.py
@Author  : 梁宗豪
@Date    : 2026-03-17
@Version : 1.0.0
@Desc    : APP自动化测试业务控制层 (Controller)。
           处理测试脚本的加载、解析、测试用例排队、执行以及测试报告/日志的实时渲染。
"""

from PyQt5.QtWidgets import QMainWindow

from app.app_test_ui import Ui_AppTestWindow


class AppTestWindow(QMainWindow, Ui_AppTestWindow):
    """
    APP 自动化测试业务窗口类。
    """
    def __init__(self, parent = None):
        """
        初始化 APP 测试窗口
        :param parent: 父窗口指针，用于管理窗口生命周期
        """
        super().__init__(parent)
        # 初始化界面组件
        self.setupUi(self)