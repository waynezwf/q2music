# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：搜索列表面板

import thread
from TableGrid import *
from config.Config import *
from IconButton import IconButton
from protocol.TencentProtocol import TencentProtocol


class SearchPanel(QFrame):
    """
    歌曲列表面板，显示搜索到的歌曲，并提供上一页、下一页、加入播放列队等操作
    包括下列重要组件：
    1、tencent 腾讯协议，用于通过腾讯开放接口搜索歌曲信息
    """

    def __init__(self):
        QFrame.__init__(self)
        self.__init_layout()

        self.tencent = TencentProtocol()
        self.tencent.connect(SIGNAL('search_complete()'), self.search_complete)

        self.keyword = ''
        self.page_index = 1
        self.page_size = 20

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

        self.btn_add_playlist = IconButton(u"加入播放列表")
        self.btn_add_playlist.setProperty('class', 'highlight_button')
        control_layout.addWidget(self.btn_add_playlist)

        self.btn_download = IconButton(u"下载选择项")
        self.btn_download.setProperty('class', 'highlight_button')
        self.btn_download.connect(SIGNAL('clicked()'), self.action_download)
        control_layout.addWidget(self.btn_download)

        self.btn_previous = IconButton(u"上一页")
        self.btn_previous.setProperty('class', 'highlight_button')
        self.btn_previous.connect(SIGNAL('clicked()'), self.action_previous)
        control_layout.addWidget(self.btn_previous)

        self.btn_next = IconButton(u"下一页")
        self.btn_next.setProperty('class', 'highlight_button')
        self.btn_next.connect(SIGNAL('clicked()'), self.action_next)
        control_layout.addWidget(self.btn_next)

        self.song_table = SongTable()
        self.layout.addWidget(self.song_table)

    @property
    def search_list(self):
        return self.song_table.records

    def search(self):
        """
        通过关键字搜索歌曲
        注意会启动新的线程进行搜索，通过 tencent 对象的消息捕获搜索结果
        """
        self.emit(SIGNAL('before_search()'))
        self.tencent.keyword = self.keyword.encode('utf-8')
        self.tencent.page_index = self.page_index
        self.tencent.page_size = self.page_size
        self.tencent.start()

    def search_complete(self):
        """
        搜索线程执行完毕之后触发该消息
        清空表中内容，重新填充
        如果存在异常则清空数据，显示消息
        """
        if not self.tencent.has_exception:
            self.song_table.fill_data(self.tencent.song_list)
        else:
            self.song_table.fill_data([])
            txt = u'搜索错误'
            message = ''
            for e in self.tencent.exception_list:
                message += e.message
            QMessageBox.warning(self, txt, txt+u'。错误消息：'+message, QMessageBox.Ok)
        self.emit(SIGNAL('after_fill()'))

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

    def action_download(self):
        """
        下载选择的歌曲
        """
        if len(self.song_table.selected_rows) < 1:
            return

        for song in self.song_table.selected_rows:
            # 启动新的线程，开始下载音频数据
            thread.start_new_thread(self.tencent.download, (song, QM_DEFAULT_DOWNLOAD_PATH))

    def action_previous(self):
        """
        上一页，再次执行搜索
        """
        if self.page_index <= 1:
            self.page_index = 1
        else:
            self.page_index -= 1
        self.search()

    def action_next(self):
        """
        下一页，再次执行搜索
        :return:
        """
        if len(self.tencent.song_list) > 0:
            self.page_index += 1
        else:
            QMessageBox.information(self, u'消息', u'没有更多内容。', QMessageBox.Ok)
            self.page_index = 1
        self.search()
