# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：窗口测试程序

import os
import thread
from PySide.QtCore import *
from PySide.QtGui import *
from PyAudioTest import *
from protocol.TencentProtocol import TencentProtocol

ICON_PATH = "../../res/icons/"


class ColumnHeader(QObject):
    """
    列头声明类
    """
    def __init__(self, **kwargs):
        QObject.__init__(self)

        self.title = kwargs.get('title', None)
        self.width = kwargs.get('width', None)
        self.field = kwargs.get('field', None)
        self.is_checkbox = kwargs.get('is_checkbox', False)
        self.alignment = kwargs.get('alignment', Qt.AlignLeft)


class TopPanel(QFrame):

    def __init__(self):
        QFrame.__init__(self)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.layout)

        self.qq_music = QToolButton()
        self.qq_music.setProperty('class', 'qq_music')
        self.layout.addWidget(self.qq_music)

        self.search_editor = QLineEdit()
        self.search_editor.setProperty('class', 'search_editor')
        self.search_editor.setText(u"周华健")
        self.layout.addWidget(self.search_editor)

        self.search_button = QToolButton()
        self.search_button.setProperty('class', 'top_highlight_button')
        self.search_button.setIcon(QIcon(ICON_PATH + 'search.svg'))
        self.layout.addWidget(self.search_button)

        self.play_button = QToolButton()
        self.play_button.setProperty('class', 'top_highlight_button')
        self.play_button.setIcon(QIcon(ICON_PATH + 'play.svg'))
        self.layout.addWidget(self.play_button)


class LeftPanel(QFrame):

    def __init__(self):
        QFrame.__init__(self)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 20, 10, 10)
        self.setLayout(self.layout)

        info_label = QLabel(u"在线音乐")
        info_label.setProperty('class', 'info_label')
        self.layout.addWidget(info_label)

        self.button1 = QPushButton(u"试听列表")
        self.button1.setProperty('class', 'left_highlight_button')
        self.button1.setIcon(QIcon(ICON_PATH + 'list_gray.svg'))
        self.button1.hide_icon = QIcon(ICON_PATH + 'list.svg')
        self.button1.installEventFilter(self)
        self.layout.addWidget(self.button1)

        self.button2 = QPushButton(u"下载的歌曲")
        self.button2.setProperty('class', 'left_highlight_button')
        self.button2.setIcon(QIcon(ICON_PATH + 'download_gray.svg'))
        self.button2.hide_icon = QIcon(ICON_PATH + 'download.svg')
        self.button2.installEventFilter(self)
        self.layout.addWidget(self.button2)

        info_label = QLabel(u"播放列表")
        info_label.setProperty('class', 'info_label')
        self.layout.addWidget(info_label)

        self.button3 = QPushButton(u"我的收藏")
        self.button3.setProperty('class', 'left_highlight_button')
        self.button3.setIcon(QIcon(ICON_PATH + 'favourite_gray.svg'))
        self.button3.hide_icon = QIcon(ICON_PATH + 'favourite.svg')
        self.button3.installEventFilter(self)
        self.layout.addWidget(self.button3)

        self.layout.addStretch(1)

    def swap_icon(self, button):
        """
        :param QPushButton button:
        """
        if not hasattr(button, 'hide_icon'):
            return
        icon = button.hide_icon
        button.hide_icon = button.icon()
        button.setIcon(icon)

    def eventFilter(self, source, event):
        if event.type() == QEvent.HoverEnter or event.type() == QEvent.HoverLeave:
            self.swap_icon(source)
        return QMainWindow.eventFilter(self, source, event)


class SongTable(QTableWidget):

    def __init__(self):
        QTableWidget.__init__(self)
        self.__mappings__ = []
        self.__selected_rows__ = []
        self.__init_columns__()

    def __init_columns__(self):
        column_headers = []
        column_headers += [ColumnHeader(title=u'选择', width=50, is_checkbox=True, alignment=Qt.AlignCenter)]
        column_headers += [ColumnHeader(title=u'歌曲', width=300, field='name', alignment=Qt.AlignLeft)]
        column_headers += [ColumnHeader(title=u'专辑', width=200, field='album_name', alignment=Qt.AlignLeft)]
        column_headers += [ColumnHeader(title=u'歌手', width=200, field='singer_name', alignment=Qt.AlignLeft)]
        self.add_columns(column_headers)

    def add_column(self, header):
        """
        添加单列
        :param header: 单列数据声明
        """
        col_count = self.columnCount()
        self.insertColumn(col_count)

        item = QTableWidgetItem()
        item.setTextAlignment(header.alignment)
        item.setText(header.title)
        self.setHorizontalHeaderItem(col_count, item)
        self.setColumnWidth(col_count, header.width)
        self.__mappings__ += [header]

    def add_columns(self, headers):
        """
        添加列
        :param headers: 列头声明数据集合
        """
        for header in headers:
            self.add_column(header)

    def remove_all(self):
        """
        删除所有记录
        """
        i = 0
        while i < self.rowCount():
            self.removeRow(0)

    def add_row(self, song_record):
        """
        添加一行数据
        :param dict song_record: 行数据内容
        """
        row_index = self.rowCount()
        self.insertRow(row_index)

        for col_index, column_header in enumerate(self.__mappings__):

            # 遍历列头定义数据，根据列头声明显示每行数据
            if column_header.is_checkbox and column_header.field is None:
                # 要作为checkbox，但无字段设置的，作为首列选择按钮
                checkbox = QCheckBox()
                checkbox.row_index = row_index
                checkbox.row_data = song_record
                checkbox.connect(SIGNAL('stateChanged(int)'), self.row_selected)

                cell_widget = QWidget()
                lay_out = QHBoxLayout(cell_widget)
                lay_out.addWidget(checkbox)
                lay_out.setAlignment(Qt.AlignCenter)
                lay_out.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(lay_out)

                self.setCellWidget(row_index, col_index, cell_widget)
            else:
                if column_header.field in song_record:
                    column_value = song_record[column_header.field]
                    if column_value is None:
                        column_value = ''
                    label = QLabel(column_value)
                    label.setProperty('class', 'grid_label')
                    self.setCellWidget(row_index, col_index, label)

    def fill_data(self, song_records):
        """
        按记录集填充表格
        :param list song_records: 记录集
        """
        self.remove_all()
        for row_index, song_record in enumerate(song_records):
            self.add_row(song_record)

    def row_selected(self, value):
        """
        选择行时，向已选择的字典中加入一行数据
        :param value: 是否选中
        """
        checkbox = self.sender()
        if value:
            self.__selected_rows__.append(checkbox.row_data)
        else:
            self.__selected_rows__.remove(checkbox.row_data)

    @property
    def selected_rows(self):
        """
        :return: 获取已经选择的行
        """
        return self.__selected_rows__


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()
        self.play_key = None

    def init_ui(self):
        self.statusBar().showMessage(u'就绪')
        self.setGeometry(200, 200, 1024, 700)
        self.setWindowTitle(u'QQ 音乐 Fedora（Linux） 版')

        central_layout = QVBoxLayout()
        central_layout.setSpacing(0)
        central_layout.setContentsMargins(0, 0, 0, 0)

        central_widget = QWidget()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.top_panel = TopPanel()
        central_layout.addWidget(self.top_panel)
        self.top_panel.search_button.connect(SIGNAL('clicked()'), self.search)
        self.top_panel.play_button.connect(SIGNAL('clicked()'), self.play)

        wrap_layout = QHBoxLayout()
        wrap_layout.setSpacing(0)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addLayout(wrap_layout)

        left_panel = LeftPanel()
        wrap_layout.addWidget(left_panel)

        self.song_table = SongTable()
        wrap_layout.addWidget(self.song_table)

    def search(self):
        keywords = self.top_panel.search_editor.text()
        song_list = search_song(keywords.encode('utf-8'))
        self.song_table.fill_data(song_list)

    def play(self):
        thread.start_new_thread(self.thread_play, ())

    def thread_play(self):
        if self.play_key is None:
            self.play_key = get_play_key()
        song_list = self.song_table.selected_rows
        if len(song_list) > 0:
            song_url = get_song_address(song_list[0], self.play_key)
            play_from_url(song_url)

    def state_changed(self, value):
        cb = self.sender()
        if value:
            self.statusBar().showMessage(cb.text())
        else:
            self.statusBar().showMessage(u'就绪')

    def center(self):
        """
        移动窗口到屏幕的中间
        """
        q_rect = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        q_rect.moveCenter(center_point)
        self.move(q_rect.topLeft())


def load_qss(file_path):
    path = os.path.dirname(os.path.realpath(__file__))
    path += file_path
    with open(path) as f:
        txt = f.readlines()
        txt = ''.join(txt).strip("\r\n")
    return txt


def main():
    """
    app = QApplication(sys.argv)
    qss = load_qss("/../../res/css/WRadio.css")
    app.setStyleSheet(qss)

    ex = MainWindow()
    ex.center()
    ex.show()
    sys.exit(app.exec_())
    # """

    """
    print "= 汉语 ============"
    # \u6211 \u7231 \u4F60
    print repr(u"123汉字编码".encode('UTF-8').decode('GBK'))
    print u"中文\ub458"

    print "= 韩文 ============"
    vl = [47168, 51060, 49436, 51339, 50500, 0x6211, 0x7231, 0x4F60]
    txt = ''
    for v in vl:
        code = u'{0}'.format('\u'+hex(v)[2:6])
        txt += code.decode('unicode-escape')
    print txt

    print "= 韩文 ============"
    string = u'&#48148;&#48372;&#52376;&#47100; &#51339;&#50500;&#54644;或许还有点中文呢'
    code_list = re.findall(r"&#(\d{5}?);", string)
    txt = ''
    for code in code_list:
        u_code = u'{0}'.format('\u'+hex(int(code))[2:6])
        word = u_code.decode('unicode-escape')
        string = string.replace("&#"+code+";", word)
        txt += word
    print txt
    print string
    # """

    string = u'&#48148;&#48372;&#52376;&#47100; &#51339;&#50500;&#54644;或许还有点中文呢'
    print "= 韩文转换 ========"
    print TencentProtocol.decode_korean(string)


if __name__ == '__main__':
    main()
