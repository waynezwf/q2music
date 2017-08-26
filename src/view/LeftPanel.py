# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：窗口组件

from config.Config import *
from util.QtAdapter import *
from IconButton import IconButton


class LeftPanel(QFrame):
    """
    左侧面板组件，包含在不同页面之间切换的按钮
    """

    @classmethod
    def active_button(cls, button):
        """
        设置按钮为激活状态
        :param IconButton button: 按钮
        """
        if not isinstance(button, IconButton):
            return

        button.setProperty('class', 'active_highlight_button')
        button.to_white()
        button.enable_swap = False
        button.style().unpolish(button)
        button.style().polish(button)

    @classmethod
    def inactive_button(cls, button):
        """
        设置按钮为非激活状态
        :param IconButton button: 按钮
        """
        button.setProperty('class', 'highlight_button')
        button.to_gray()
        button.enable_swap = True
        button.style().unpolish(button)
        button.style().polish(button)

    def __init__(self):
        QFrame.__init__(self)
        self.__init_ui()

    def __init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 20, 10, 10)
        self.setLayout(self.layout)

        info_label = QLabel(u"在线音乐")
        info_label.setProperty('class', 'info_label')
        self.layout.addWidget(info_label)

        self.btn_playlist = IconButton(u"播放列表")
        self.btn_playlist.setProperty('class', 'highlight_button')
        self.btn_playlist.white_icon = QIcon(QM_ICON_PATH + 'playlist.svg')
        self.btn_playlist.gray_icon = QIcon(QM_ICON_PATH + 'playlist_gray.svg')
        self.btn_playlist.enable_swap = True
        self.btn_playlist.to_gray()
        self.layout.addWidget(self.btn_playlist)

        self.btn_search = IconButton(u"搜索结果")
        self.btn_search.setProperty('class', 'highlight_button')
        self.btn_search.white_icon = QIcon(QM_ICON_PATH + 'search_list.svg')
        self.btn_search.gray_icon = QIcon(QM_ICON_PATH + 'search_list_gray.svg')
        self.btn_search.enable_swap = True
        self.btn_search.to_gray()
        self.layout.addWidget(self.btn_search)

        self.btn_cache = IconButton(u"历史记录")
        self.btn_cache.setProperty('class', 'highlight_button')
        self.btn_cache.white_icon = QIcon(QM_ICON_PATH + 'cache_list.svg')
        self.btn_cache.gray_icon = QIcon(QM_ICON_PATH + 'cache_list_gray.svg')
        self.btn_cache.enable_swap = True
        self.btn_cache.to_gray()
        self.layout.addWidget(self.btn_cache)

        """
        self.btn_favorite = IconButton(u"我的收藏夹")
        self.btn_favorite.setProperty('class', 'highlight_button')
        self.btn_favorite.white_icon = QIcon(QM_ICON_PATH + 'favourite.svg')
        self.btn_favorite.gray_icon = QIcon(QM_ICON_PATH + 'favourite_gray.svg')
        self.btn_favorite.enable_swap = True
        self.btn_favorite.to_gray()
        self.layout.addWidget(self.btn_favorite)
        """

        info_label = QLabel(u"本地音乐")
        info_label.setProperty('class', 'info_label')
        self.layout.addWidget(info_label)

        self.btn_download = IconButton(u"下载歌曲")
        self.btn_download.setProperty('class', 'highlight_button')
        self.btn_download.white_icon = QIcon(QM_ICON_PATH + 'download.svg')
        self.btn_download.gray_icon = QIcon(QM_ICON_PATH + 'download_gray.svg')
        self.btn_download.enable_swap = True
        self.btn_download.to_gray()
        self.layout.addWidget(self.btn_download)

        self.layout.addStretch(1)
