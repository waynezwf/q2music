# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：缓存窗口面板

import os
from TableGrid import *
from config.Config import *
from IconButton import IconButton
from pydub.utils import mediainfo
from protocol.SongInfo import SongInfo


class DownloadPanel(QFrame):
    """
    播放列表面板，显示等待播放的歌曲
    """

    def __init__(self):
        QFrame.__init__(self)
        self.__init_layout()
        self.__init_download()

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

        self.btn_delete = IconButton(u"删除")
        self.btn_delete.setProperty('class', 'highlight_button')
        self.btn_delete.connect(SIGNAL('clicked()'), self.action_delete)
        control_layout.addWidget(self.btn_delete)

        self.song_table = SongTable()
        self.layout.addWidget(self.song_table)

    def __init_download(self):
        """
        从本地下载目录中读取缓存记录，并读取出描述数据，显示在表格中
        """
        download_list = []
        names = [name for name in os.listdir(QM_DEFAULT_DOWNLOAD_PATH)
                 if name.endswith('.m4a')]
        for name in names:
            song_path = QM_DEFAULT_DOWNLOAD_PATH + name
            tag_info = mediainfo(song_path).get('TAG', None)

            song_info = SongInfo()
            song_info.song_path = song_path
            song_info.name = tag_info[u'title']
            song_info.singer_names = tag_info[u'artist']
            song_info.album_name = tag_info[u'album']
            song_info.length = '00:00:00'
            song_info.mid = name[0:len(name)-4]
            song_info.image_path = QM_DEFAULT_DOWNLOAD_PATH + song_info['mid'] + '.jpg'
            download_list.append(song_info)
        self.song_table.fill_data(download_list)

    @property
    def download_list(self):
        return self.song_table.records

    @download_list.setter
    def download_list(self, value):
        if not isinstance(value, list):
            raise Exception(u'下载列表数据类型错误')
        self.song_table.remove_all()
        self.song_table.fill_data(value)

    def has_song(self, song_info):
        """
        检查下载列表中是否已经存在歌曲
        :param SongInfo song_info:
        :return:
        """
        return song_info in self.download_list

    def append_song(self, song_info):
        """
        向列表中增加歌曲信息，刷新表格
        增加音乐之前首先判断是否已经存在相同的音乐
        :param SongInfo song_info: 歌曲信息
        """
        if self.has_song(song_info):
            return

        self.download_list.append(song_info)
        self.song_table.add_row(song_info)

    def action_select_all(self):
        """
        全选
        """
        self.song_table.select_all()

    def action_unselect_all(self):
        """
        取消全选
        """
        self.song_table.unselect_all()

    def action_delete(self):
        for song in self.song_table.selected_rows:          # type: SongInfo
            if song.song_path is not None:
                os.remove(song.song_path)
            if song.image_path is not None:
                os.remove(song.image_path)
            self.song_table.records.remove(song)
        self.song_table.remove_all()
        self.song_table.fill_data(self.song_table.records)
