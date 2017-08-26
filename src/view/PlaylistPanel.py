# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：播放列表

from TableGrid import *
from IconButton import IconButton
from protocol.SongInfo import SongInfo


class PlaylistPanel(QFrame):
    """
    播放列表面板，显示等待播放的歌曲
    """

    def __init__(self):
        QFrame.__init__(self)
        self.__init_layout()

    def __init_layout(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(0, 10, 10, 10)
        self.layout.addLayout(control_layout)

        self.btn_select_all = IconButton(u"全选")
        self.btn_select_all.setProperty('class', 'highlight_button')
        self.btn_select_all.connect(SIGNAL('clicked()'), self.action_select_all)
        control_layout.addWidget(self.btn_select_all)

        self.btn_unselect_all = IconButton(u"取消")
        self.btn_unselect_all.setProperty('class', 'highlight_button')
        self.btn_unselect_all.connect(SIGNAL('clicked()'), self.action_unselect_all)
        control_layout.addWidget(self.btn_unselect_all)
        control_layout.addStretch(1)

        self.btn_delete = IconButton(u"从播放列表删除")
        self.btn_delete.setProperty('class', 'highlight_button')
        self.btn_delete.connect(SIGNAL('clicked()'), self.action_delete_from_playlist)
        control_layout.addWidget(self.btn_delete)

        self.song_table = SongTable()
        self.layout.addWidget(self.song_table)

    @property
    def play_list(self):
        return self.song_table.records

    @play_list.setter
    def play_list(self, value):
        if not isinstance(value, list):
            raise Exception(u'播放列表数据类型错误')
        self.song_table.remove_all()
        self.song_table.fill_data(value)

    def has_song(self, song_info):
        """
        检查播放列表中是否已经存在歌曲
        :param SongInfo song_info:
        :return:
        """
        return song_info in self.play_list

    def append_song(self, song_info):
        """
        向列表中增加歌曲信息，刷新表格
        增加音乐之前首先判断是否已经存在相同的音乐
        :param SongInfo song_info: 歌曲信息
        """
        if self.has_song(song_info):
            return

        self.play_list.append(song_info)
        self.song_table.add_row(song_info)

    def remove_song(self, song_info):
        """
        从播放列表中删除歌曲信息，刷新表格
        :param SongInfo song_info: 歌曲信息
        """
        self.play_list.remove(song_info)
        self.song_table.remove_all()
        self.song_table.fill_data(self.play_list)

    def clear(self):
        """
        从播放列表中清除所有的歌曲信息
        :return:
        """
        self.play_list = []
        self.song_table.remove_all()
        self.song_table.fill_data(self.play_list)

    def action_select_all(self):
        self.song_table.select_all()

    def action_unselect_all(self):
        self.song_table.unselect_all()

    def action_delete_from_playlist(self):
        for song in self.song_table.selected_rows:
            self.play_list.remove(song)
        self.song_table.remove_all()
        self.song_table.fill_data(self.play_list)
