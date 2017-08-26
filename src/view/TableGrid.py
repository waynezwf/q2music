# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：网格类

from util.QtAdapter import *
from protocol.SongInfo import SongInfo


class ColumnHeader(object):
    """
    列头声明类
    """
    def __init__(self, **kwargs):
        object.__init__(self)

        self.title = kwargs.get('title', None)                      # 网格标题
        self.width = kwargs.get('width', None)                      # 网格宽度
        self.field = kwargs.get('field', None)                      # 数据字段名称
        self.alignment = kwargs.get('alignment', Qt.AlignLeft)      # 网格标题对齐方式
        self.is_checkbox = kwargs.get('is_checkbox', False)         # 是否显示为 checkbox


class TableGrid(QTableWidget):
    """
    网格类，支持批量插入列和行数据
    """

    def __init__(self):
        QTableWidget.__init__(self)
        self.__mappings__ = []
        self.__records__ = []
        self.__selected_rows__ = []

        self.header_font = QFont()
        self.header_font.setPointSize(11)
        self.header_font.setBold(True)

    @property
    def selected_rows(self):
        """
        :return: 获取已经选择的行
        """
        return self.__selected_rows__

    @property
    def records(self):
        return self.__records__

    def add_column(self, header):
        """
        添加单列
        :param ColumnHeader header: 单列数据声明
        """
        column_index = self.columnCount()
        self.insertColumn(column_index)

        item = QTableWidgetItem(header.title)
        item.setFont(self.header_font)
        item.setForeground(QColor('#11A551'))
        item.setBackground(QColor('#000000'))
        item.setTextAlignment(header.alignment)

        self.setHorizontalHeaderItem(column_index, item)
        self.setColumnWidth(column_index, header.width)
        self.__mappings__ += [header]

    def add_columns(self, headers):
        """
        添加列
        :param ColumnHeader[] headers: 列头声明数据集合
        """
        for header in headers:
            self.add_column(header)

    def add_row(self, record):
        """
        添加一行数据
        :param SongInfo record: 行数据内容
        """
        row_index = self.rowCount()
        self.insertRow(row_index)

        for col_index, column_header in enumerate(self.__mappings__):

            # 遍历列头定义数据，根据列头声明显示每行数据
            if column_header.is_checkbox and column_header.field is None:
                # 要作为checkbox，但无字段设置的，作为首列选择按钮
                checkbox = QCheckBox()
                checkbox.row_index = row_index
                checkbox.row_data = record
                checkbox.connect(SIGNAL('stateChanged(int)'), self.row_selected)

                cell_widget = QWidget()
                lay_out = QHBoxLayout(cell_widget)
                lay_out.addWidget(checkbox)
                lay_out.setAlignment(Qt.AlignCenter)
                lay_out.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(lay_out)
                cell_widget.row_index = row_index
                cell_widget.row_data = record
                self.setCellWidget(row_index, col_index, cell_widget)
            else:
                if column_header.field in record:
                    column_value = record[column_header.field]
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
        self.__records__ = song_records
        for row_index, song_record in enumerate(song_records):
            self.add_row(song_record)

    def remove_all(self):
        """
        删除所有记录
        """
        while self.rowCount() > 0:
            self.removeRow(0)
        self.__selected_rows__ = []

    def update_row(self, song_record):
        """
        根据行号更新行中的数据，更新时会修改每一列的数据
        :param song_record: 数据内容
        :return:
        """
        if song_record not in self.records:
            return

        row_index = self.records.index(song_record)
        for col_index, column_header in enumerate(self.__mappings__):

            # 遍历列头定义数据，根据列头声明显示每行数据
            if column_header.is_checkbox and column_header.field is None:
                # 要作为checkbox，但无字段设置的，作为首列选择按钮
                checkbox = self.cellWidget(row_index, col_index).findChild(QCheckBox)
                checkbox.row_index = row_index
                checkbox.row_data = song_record
            else:
                if column_header.field in song_record:
                    column_value = song_record[column_header.field]
                    if column_value is None:
                        column_value = ''
                    label = self.cellWidget(row_index, col_index)
                    label.setText(column_value)

    def row_selected(self, value):
        """
        选择行时，向已选择的字典中加入一行数据
        :param value: 是否选中
        """
        checkbox = self.sender()
        if value:
            self.__selected_rows__.append(checkbox.row_data)
            self.emit(SIGNAL('row_selected()'))
        else:
            self.__selected_rows__.remove(checkbox.row_data)
            self.emit(SIGNAL('row_unselected()'))

    def select_all(self):
        """
        选择所有的记录
        :return:
        """
        for i in range(self.rowCount()):
            checkbox = self.cellWidget(i, 0).findChild(QCheckBox)       # type: QCheckBox
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(True)

    def unselect_all(self):
        """
        取消选择所有的记录
        :return:
        """
        for i in range(self.rowCount()):
            checkbox = self.cellWidget(i, 0).findChild(QCheckBox)       # type: QCheckBox
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(False)


class SongTable(TableGrid):
    """
    显示歌曲信息的表格类，这里已经初始化对应的信息列
    """

    def __init__(self):
        TableGrid.__init__(self)
        self.__init_columns__()
        self.__active_song_info = None

        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.connect(SIGNAL('cellDoubleClicked(int,int)'), self.cell_double_clicked)

    def __init_columns__(self):
        column_headers = []
        column_headers += [ColumnHeader(title=u'选择', width=50, is_checkbox=True, alignment=Qt.AlignCenter)]
        column_headers += [ColumnHeader(title=u'歌曲', width=300, field='name', alignment=Qt.AlignLeft)]
        column_headers += [ColumnHeader(title=u'歌手', width=160, field='singer_names', alignment=Qt.AlignLeft)]
        column_headers += [ColumnHeader(title=u'时长', width=80, field='length', alignment=Qt.AlignLeft)]
        column_headers += [ColumnHeader(title=u'专辑', width=400, field='album_name', alignment=Qt.AlignLeft)]
        self.add_columns(column_headers)

    @property
    def active_song_info(self):
        """
        当前活动歌曲信息
        :return: 活动歌曲
        """
        return self.__active_song_info

    def cell_double_clicked(self, r, c):
        """
        单元格双击之后，修改当前活动的歌曲信息
        :param int r: 行号
        :param int c: 列号
        """
        self.__active_song_info = self.cellWidget(r, 0).row_data
        self.emit(SIGNAL('cell_double_clicked()'))
