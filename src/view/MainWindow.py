# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：主窗口程序

from player.AudioLoader import *
from TopPanel import TopPanel
from LeftPanel import LeftPanel
from SearchPanel import SearchPanel
from PlaylistPanel import PlaylistPanel
from CachePanel import CachePanel
from DownloadPanel import DownloadPanel
from BottomPanel import BottomPanel
from protocol.SongInfo import SongInfo


class MainWindow(QMainWindow):
    """
    主窗口程序，构建主界面，载入样式表文件并应用
    关联各面板之间的行为
    """

    @classmethod
    def load_qss(cls, file_path):
        with open(file_path) as f:
            txt = f.readlines()
            txt = ''.join(txt).strip("\r\n")
        return txt

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__init_ui()
        qss = self.load_qss(QM_QSS_PATH)
        self.setStyleSheet(qss)
        app_icon = QIcon(QM_ICON_PATH + 'qq_music_sm.png')
        self.setWindowIcon(app_icon)

    def __init_ui(self):
        self.setGeometry(200, 200, 1024, 700)
        self.setWindowTitle(u'QQ音乐民间(Linux)版')

        central_layout = QVBoxLayout()
        central_layout.setSpacing(0)
        central_layout.setContentsMargins(0, 0, 0, 0)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.top_panel = TopPanel()
        self.top_panel.edt_search.connect(SIGNAL('returnPressed()'), self.action_search)
        self.top_panel.btn_search.connect(SIGNAL('clicked()'), self.action_search)
        central_layout.addWidget(self.top_panel)

        wrap_layout = QHBoxLayout()
        wrap_layout.setSpacing(0)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addLayout(wrap_layout)

        self.left_panel = LeftPanel()
        self.left_panel.btn_search.connect(SIGNAL('clicked()'), self.action_show_search_panel)
        self.left_panel.btn_playlist.connect(SIGNAL('clicked()'), self.action_show_playlist_panel)
        self.left_panel.btn_cache.connect(SIGNAL('clicked()'), self.action_show_cache_panel)
        self.left_panel.btn_download.connect(SIGNAL('clicked()'), self.action_show_download_panel)
        wrap_layout.addWidget(self.left_panel)

        self.stacked = QStackedWidget()
        wrap_layout.addWidget(self.stacked)

        self.search_panel = SearchPanel()
        self.search_panel.connect(SIGNAL('before_search()'), self.open_waiting)
        self.search_panel.connect(SIGNAL('after_fill()'), self.close_waiting)
        self.search_panel.song_table.connect(SIGNAL('cell_double_clicked()'), self.play_search_table)
        self.search_panel.btn_add_playlist.connect(SIGNAL('clicked()'), self.action_add_playlist)
        self.search_panel.tencent.connect(SIGNAL('after_download(PyObject)'), self.after_download)
        self.stacked.addWidget(self.search_panel)

        self.playlist_panel = PlaylistPanel()
        self.playlist_panel.song_table.connect(SIGNAL('cell_double_clicked()'), self.play_list_table)
        self.stacked.addWidget(self.playlist_panel)

        self.cache_panel = CachePanel()
        self.cache_panel.song_table.connect(SIGNAL('cell_double_clicked()'), self.play_cache_table)
        self.stacked.addWidget(self.cache_panel)

        self.download_panel = DownloadPanel()
        self.download_panel.song_table.connect(SIGNAL('cell_double_clicked()'), self.play_download_table)
        self.stacked.addWidget(self.download_panel)

        self.bottom_panel = BottomPanel()
        self.bottom_panel.connect(SIGNAL('before_load()'), self.open_waiting)
        self.bottom_panel.connect(SIGNAL('load_error()'), self.close_waiting)
        self.bottom_panel.loader.connect(SIGNAL('after_cache()'), self.after_cache)
        self.bottom_panel.player.connect(SIGNAL('before_play()'), self.close_waiting)
        self.bottom_panel.btn_stop.connect(SIGNAL('clicked()'), self.close_waiting)
        central_layout.addWidget(self.bottom_panel)

    def center(self):
        """
        移动窗口到屏幕的中间
        """
        q_rect = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        q_rect.moveCenter(center_point)
        self.move(q_rect.topLeft())

    def open_waiting(self):
        """
        打开等待图标
        """
        self.top_panel.is_waiting = True

    def close_waiting(self):
        """
        关闭等待图标
        """
        self.top_panel.is_waiting = False

    def set_active_panel(self, panel):
        """
        设置中间的活动面板
        :return:
        """
        self.stacked.setCurrentWidget(panel)
        if panel == self.search_panel:
            self.left_panel.active_button(self.left_panel.btn_search)
            self.left_panel.inactive_button(self.left_panel.btn_playlist)
            self.left_panel.inactive_button(self.left_panel.btn_cache)
            self.left_panel.inactive_button(self.left_panel.btn_download)
        elif panel == self.playlist_panel:
            self.left_panel.active_button(self.left_panel.btn_playlist)
            self.left_panel.inactive_button(self.left_panel.btn_search)
            self.left_panel.inactive_button(self.left_panel.btn_cache)
            self.left_panel.inactive_button(self.left_panel.btn_download)
        elif panel == self.cache_panel:
            self.left_panel.active_button(self.left_panel.btn_cache)
            self.left_panel.inactive_button(self.left_panel.btn_search)
            self.left_panel.inactive_button(self.left_panel.btn_playlist)
            self.left_panel.inactive_button(self.left_panel.btn_download)
        elif panel == self.download_panel:
            self.left_panel.active_button(self.left_panel.btn_download)
            self.left_panel.inactive_button(self.left_panel.btn_cache)
            self.left_panel.inactive_button(self.left_panel.btn_search)
            self.left_panel.inactive_button(self.left_panel.btn_playlist)

    def after_cache(self):
        """
        缓存执行完毕之后执行的动作
        主要工作：
        1、如果音乐尚未出现在缓存列表中，则首先加入缓存列表
        2、如果音乐已经在缓存列表或下载列表中，则更新缓存列表或下载列表中的音频信息
          主要更新的就是音乐文件的时间长度
        """
        if self.bottom_panel.current_song not in self.cache_panel.song_table.records:
            self.cache_panel.append_song(self.bottom_panel.current_song)

        self.cache_panel.song_table.update_row(self.bottom_panel.current_song)
        self.download_panel.song_table.update_row(self.bottom_panel.current_song)

    def action_search(self):
        """
        搜索事件，设置搜索关键字，执行搜索
        这个事件同时对搜索按钮和关键字文本框有效
        """
        self.search_panel.page_index = 1
        self.search_panel.keyword = self.top_panel.edt_search.text()
        self.search_panel.search()
        self.set_active_panel(self.search_panel)

    def action_show_search_panel(self):
        """
        显示搜索列表面板
        """
        self.set_active_panel(self.search_panel)

    def action_show_playlist_panel(self):
        """
        显示播放列表面板
        """
        self.set_active_panel(self.playlist_panel)

    def action_show_cache_panel(self):
        """
        显示缓存列表
        """
        self.set_active_panel(self.cache_panel)

    def action_show_download_panel(self):
        """
        显示缓存列表
        """
        self.set_active_panel(self.download_panel)

    def action_add_playlist(self):
        """
        添加到播放列表
        """
        for song_info in self.search_panel.song_table.selected_rows:
            self.playlist_panel.append_song(song_info)

    def after_download(self, song_info):
        """
        下载完成之后执行的动作，将已经下载的音乐加入下载列表
        :param SongInfo song_info: 已经下载成功的音乐文件
        """
        if not self.download_panel.has_song(song_info):
            self.download_panel.append_song(song_info)

    def play_search_table(self):
        """
        搜索列表上歌曲双击动作，执行下面的动作：
        1、如果歌曲补在不妨列表中，则将活动歌曲插入播放列表
        2、立即开始播放选择的歌曲
        """
        song_info = self.search_panel.song_table.active_song_info
        if not self.playlist_panel.has_song(song_info):
            self.playlist_panel.play_list = [song_info] + self.playlist_panel.play_list

        self.open_waiting()
        self.bottom_panel.loader.source_type = AUDIO_FROM_INTERNET
        self.bottom_panel.song_list = self.search_panel.search_list
        self.bottom_panel.song_index = self.bottom_panel.song_list.index(song_info)

    def play_list_table(self):
        """
        从播放列表的当前音乐开始播放
        """
        song_info = self.playlist_panel.song_table.active_song_info
        self.open_waiting()
        self.bottom_panel.loader.source_type = AUDIO_FROM_INTERNET
        self.bottom_panel.song_list = self.playlist_panel.song_table.records
        self.bottom_panel.song_index = self.bottom_panel.song_list.index(song_info)

    def play_cache_table(self):
        """
        播放本地缓存列表中的音乐
        """
        song_info = self.cache_panel.song_table.active_song_info
        self.open_waiting()
        self.bottom_panel.loader.source_type = AUDIO_FROM_LOCAL
        self.bottom_panel.song_list = self.cache_panel.song_table.records
        self.bottom_panel.song_index = self.bottom_panel.song_list.index(song_info)

    def play_download_table(self):
        """
        播放下载列表中的音乐
        """
        song_info = self.download_panel.song_table.active_song_info
        self.open_waiting()
        self.bottom_panel.loader.source_type = AUDIO_FROM_LOCAL
        self.bottom_panel.song_list = self.download_panel.song_table.records
        self.bottom_panel.song_index = self.bottom_panel.song_list.index(song_info)
