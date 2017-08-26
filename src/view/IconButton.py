# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：网格类

from util.QtAdapter import *


class IconButton(QPushButton):
    """
    网格类，支持批量插入列和行数据
    """
    ICON_WHITE = 0x01
    ICON_GRAY = 0x02

    def __init__(self, label=''):
        QPushButton.__init__(self, label)
        self.setFocusPolicy(Qt.NoFocus)
        self.white_icon = None      # type: QIcon
        self.gray_icon = None       # type: QIcon
        self.icon_value = 0
        self.enable_swap = False    # 是否启动交换按钮
        self.installEventFilter(self)

    def to_gray(self):
        self.icon_value = self.ICON_GRAY
        self.setIcon(self.gray_icon)

    def to_white(self):
        self.icon_value = self.ICON_WHITE
        self.setIcon(self.white_icon)

    def swap_icon(self):
        if self.enable_swap:
            if self.icon_value == self.ICON_GRAY:
                self.to_white()
            elif self.icon_value == self.ICON_WHITE:
                self.to_gray()

    def eventFilter(self, source, event):
        """
        鼠标滑过事件过滤器，用于切换按钮的图标
        :param source: 事件源
        :param event: 事件对象
        :return: 转交父类事件循环
        """
        if event.type() == QEvent.HoverEnter or event.type() == QEvent.HoverLeave:
            self.swap_icon()
        return QMainWindow.eventFilter(self, source, event)
