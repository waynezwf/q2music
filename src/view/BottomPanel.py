# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：窗口组件

from random import randint
from player.Player import Player
from player.AudioLoader import *
from util.Utilities import seconds2time
from IconButton import IconButton
from protocol.SongInfo import SongInfo


ORDER_SEQUENCE = 0x01       # 顺序播放
ORDER_RANDOM = 0x02         # 随机播放
ORDER_LOOP = 0x03           # 单曲循环


class BottomPanel(QFrame):
    """
    底部控制面板组件，包含个内部按钮及其控制动作
    内部还包含有下列的组件
    1、播放器组件
    2、播放列表
    3、播放控制按钮、播放进度、歌曲信息等组件
    可在播放列表内切换歌曲
    注意：对于每首歌曲，都要标注是网络来源还是本地文件来源
    """

    def __init__(self):
        QFrame.__init__(self)
        self.__init_ui()
        self.__init_loader()
        self.__init_player()
        self.__song_index = 0

        self.start_drag_slider = False              # slider 条拖动状态标志，用于确定是否允许播放器更新
        self.stop_play = False                      # 记录用户是否点击过停止按钮的操作，点击之后为 True，再次播放为 False
        self.play_model = ORDER_SEQUENCE            # type: int
        self.song_list = []                         # type: list
        self.swap_play_model(self.play_model)

    def __init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 5, 20, 5)
        self.setLayout(self.layout)

        self.btn_previous = IconButton()
        self.btn_previous.setProperty('class', 'highlight_button')
        self.btn_previous.white_icon = QIcon(QM_ICON_PATH + 'previous.svg')
        self.btn_previous.gray_icon = QIcon(QM_ICON_PATH + 'previous_gray.svg')
        self.btn_previous.to_white()
        self.btn_previous.setIconSize(QSize(35, 35))
        self.btn_previous.connect(SIGNAL('clicked()'), self.action_previous_song)
        self.layout.addWidget(self.btn_previous)

        self.btn_play = IconButton()
        self.btn_play.setProperty('class', 'highlight_button')
        self.btn_play.setProperty('play_button', 'play_button')
        self.btn_play.white_icon = QIcon(QM_ICON_PATH + 'play.svg')
        self.btn_play.gray_icon = QIcon(QM_ICON_PATH + 'pause.svg')
        self.btn_play.to_white()
        self.btn_play.setIconSize(QSize(40, 40))
        self.btn_play.connect(SIGNAL('clicked()'), self.action_play)
        self.layout.addWidget(self.btn_play)

        self.btn_next = IconButton()
        self.btn_next.setProperty('class', 'highlight_button')
        self.btn_next.white_icon = QIcon(QM_ICON_PATH + 'next.svg')
        self.btn_next.gray_icon = QIcon(QM_ICON_PATH + 'next_gray.svg')
        self.btn_next.to_white()
        self.btn_next.setIconSize(QSize(35, 35))
        self.btn_next.connect(SIGNAL('clicked()'), self.action_next_song)
        self.layout.addWidget(self.btn_next)

        self.btn_stop = IconButton()
        self.btn_stop.setProperty('class', 'highlight_button')
        self.btn_stop.white_icon = QIcon(QM_ICON_PATH + 'stop.svg')
        self.btn_stop.gray_icon = QIcon(QM_ICON_PATH + 'stop_gray.svg')
        self.btn_stop.to_white()
        self.btn_stop.setIconSize(QSize(35, 35))
        self.btn_stop.connect(SIGNAL('clicked()'), self.action_stop)
        self.layout.addWidget(self.btn_stop)

        song_info_layout = QHBoxLayout()
        song_info_layout.setSpacing(10)
        song_info_layout.setContentsMargins(30, 10, 30, 10)
        self.layout.addLayout(song_info_layout)

        self.song_image = QLabel()
        self.song_image.setProperty('class', 'song_image')
        song_info_layout.addWidget(self.song_image)

        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(0)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        song_info_layout.addLayout(slider_layout)

        song_name_layout = QHBoxLayout()
        song_name_layout.setSpacing(5)
        song_name_layout.setContentsMargins(10, 0, 10, 5)
        slider_layout.addLayout(song_name_layout)

        self.song_name = QLabel()
        self.song_name.setText(u"曲名")
        self.song_name.setProperty('class', 'song_name')
        song_name_layout.addWidget(self.song_name)

        self.song_singer = QLabel()
        self.song_singer.setText(u"歌手")
        self.song_singer.setProperty('class', 'song_singer')
        song_name_layout.addWidget(self.song_singer)
        song_name_layout.addStretch(1)

        self.play_time = QLabel()
        self.play_time.setProperty('class', 'play_time')
        self.play_time.setText(u"00:00:00")
        song_name_layout.addWidget(self.play_time)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.connect(SIGNAL('sliderPressed()'), self.slider_pressed)
        self.slider.connect(SIGNAL('sliderReleased()'), self.slider_released)
        slider_layout.addWidget(self.slider)

        self.layout.addStretch(1)

        self.btn_sequence = IconButton()
        self.btn_sequence.setProperty('class', 'highlight_button')
        self.btn_sequence.white_icon = QIcon(QM_ICON_PATH + 'sequence.svg')
        self.btn_sequence.gray_icon = QIcon(QM_ICON_PATH + 'sequence_gray.svg')
        self.btn_sequence.to_gray()
        self.btn_sequence.connect(SIGNAL('clicked()'), self.action_sequence_play)
        self.layout.addWidget(self.btn_sequence)

        self.btn_loop = IconButton()
        self.btn_loop.setProperty('class', 'highlight_button')
        self.btn_loop.white_icon = QIcon(QM_ICON_PATH + 'loop.svg')
        self.btn_loop.gray_icon = QIcon(QM_ICON_PATH + 'loop_gray.svg')
        self.btn_loop.to_gray()
        self.btn_loop.connect(SIGNAL('clicked()'), self.action_loop_play)
        self.layout.addWidget(self.btn_loop)

        self.btn_random = IconButton()
        self.btn_random.setProperty('class', 'highlight_button')
        self.btn_random.white_icon = QIcon(QM_ICON_PATH + 'random.svg')
        self.btn_random.gray_icon = QIcon(QM_ICON_PATH + 'random_gray.svg')
        self.btn_random.to_gray()
        self.btn_random.connect(SIGNAL('clicked()'), self.action_random_play)
        self.layout.addWidget(self.btn_random)

    def __init_loader(self):
        self.loader = AudioLoader()
        self.loader.connect(SIGNAL('caching()'), self.song_caching)
        self.loader.connect(SIGNAL('after_cache()'), self.after_cache)

    def __init_player(self):
        self.player = Player()
        self.player.connect(SIGNAL('before_play()'), self.player_before_play)
        self.player.connect(SIGNAL('playing()'), self.player_playing)
        self.player.connect(SIGNAL('pause()'), self.player_pause)
        self.player.connect(SIGNAL('proceed()'), self.player_proceed)
        self.player.connect(SIGNAL('play_finished()'), self.player_finished)
        self.player.connect(SIGNAL('stopped()'), self.player_stopped)

    def to_play_icon(self):
        """
        转换主播放按钮的图标为 播放
        """
        self.btn_play.to_white()

    def to_pause_icon(self):
        """
        转换主播放按钮的图标为 暂停
        """
        self.btn_play.to_gray()

    @property
    def song_count(self):
        """
        :return: 播放列表中待播放的歌曲数量
        """
        return len(self.song_list)

    @property
    def song_index(self):
        return self.__song_index

    @song_index.setter
    def song_index(self, value):
        if self.song_count < 1:
            return
        if value < 0 or value > self.song_count - 1:
            value = 0

        self.__song_index = value
        self.current_song = self.song_list[value]
        self.player.stop()
        self.loader.stop()
        self.load_song()

    @property
    def current_song(self):
        """
        :return: 取得当前正在播放的音乐信息
        """
        return self.loader.song_info

    @current_song.setter
    def current_song(self, value):
        """
        设置当前正在播放的音乐信息
        :param SongInfo value: 音乐信息对象
        """
        self.loader.song_info = value

    def swap_play_model(self, model):
        """
        切换播放模式，顺序播放、单曲循环、随机播放
        :param int model: 随机播放模式
        """
        self.play_model = model
        if self.play_model == ORDER_SEQUENCE:
            self.btn_sequence.to_white()
            self.btn_loop.to_gray()
            self.btn_random.to_gray()
        elif self.play_model == ORDER_LOOP:
            self.btn_sequence.to_gray()
            self.btn_loop.to_white()
            self.btn_random.to_gray()
        elif self.play_model == ORDER_RANDOM:
            self.btn_sequence.to_gray()
            self.btn_loop.to_gray()
            self.btn_random.to_white()

    def load_song(self):
        """
        装载歌曲
        """
        self.emit(SIGNAL('before_load()'))
        self.stop_play = False
        self.loader.start()

    def setup_song_info(self):
        """
        设置播放界面上的歌曲信息
        """
        pixel_map = QPixmap()
        pixel_map.loadFromData(self.loader.image_data)
        pixel_map = pixel_map.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.song_image.setPixmap(pixel_map)

        self.slider.setValue(0)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.current_song.interval)

        self.song_name.setText(self.current_song.name)
        self.song_singer.setText(self.current_song.singer_names)
        self.play_time.setText(seconds2time(self.player.duration))

    def song_caching(self):
        """
        歌曲缓存成功之后就开始播放
        """
        if self.loader.has_exception:
            txt = u'载入音频数据错误'
            message = ''
            for e in self.loader.exception_list:
                message += e.message + "\r\n"
            QMessageBox.warning(self, txt, txt + u'。错误消息：' + message, QMessageBox.Ok)
            self.emit(SIGNAL('load_error()'))
            return

        self.player.audio_segment = self.loader.audio_segment
        if not self.stop_play and not self.player.is_playing:
            self.setup_song_info()
            self.player.start_position = self.slider.value()
            self.player.start()

    def after_cache(self):
        self.loader.stop()

    def play_song(self):
        """
        调用播放器方法，开始播放音乐
        """
        self.player.stop()
        self.player.start_position = self.slider.value()
        self.player.start()
        self.stop_play = False

    def stop_song(self):
        """
        调用播放器方法，停止播放，并还原播放点
        :return:
        """
        self.player.stop()
        self.slider.setValue(0)
        self.stop_play = True

    def slider_pressed(self):
        """
        在进度条上按下鼠标按钮，修改拖动标志，暂停进度更新
        """
        self.start_drag_slider = True

    def slider_released(self):
        """
        在进度条上松开鼠标按钮，修改播放点为选择的播放点
        从选择的播放点重新开始播放
        """
        self.play_song()
        self.start_drag_slider = False

    def action_play(self):
        """
        播放按钮点击执行的动作，这里分为两部分动作
        1、载入音乐
        2、播放音乐，播放音乐又分为播放和暂停两种情况
        """
        if self.player.is_playing:
            if self.player.is_paused:
                self.player.proceed()
            else:
                self.player.pause()
        else:
            self.play_song()

    def action_stop(self):
        """
        停止播放按钮执行的动作，执行两项动作
        1、停止播放
        2、还原播放点
        """
        self.stop_song()

    def action_previous_song(self):
        """
        从播放列表中读取上一首歌曲
        """
        if self.play_model == ORDER_SEQUENCE:
            self.song_index -= 1
        elif self.play_model == ORDER_LOOP:
            self.song_index = self.song_index
        elif self.play_model == ORDER_RANDOM:
            self.song_index = randint(0, self.song_count - 1)

    def action_next_song(self):
        """
        从播放列表中读取下一首歌曲
        :return:
        """
        if self.play_model == ORDER_SEQUENCE:
            self.song_index += 1
        elif self.play_model == ORDER_LOOP:
            self.song_index = self.song_index
        elif self.play_model == ORDER_RANDOM:
            self.song_index = randint(0, self.song_count - 1)

    def action_sequence_play(self):
        """
        顺序播放动作，修改播放模式参数
        """
        self.play_model = ORDER_SEQUENCE
        self.swap_play_model(self.play_model)

    def action_loop_play(self):
        """
        单曲循环播放，修改播放模式参数
        """
        self.play_model = ORDER_LOOP
        self.swap_play_model(self.play_model)

    def action_random_play(self):
        """
        随机播放，修改播放模式参数
        """
        self.play_model = ORDER_RANDOM
        self.swap_play_model(self.play_model)

    def player_before_play(self):
        """
        当播放器进入播放状态时触发的消息
        这里是修改播放按钮为 暂停 图标
        """
        self.to_pause_icon()

    def player_playing(self):
        """
        播放进行中会不断触发的消息
        主要用来修改播放时间，和播放进度
        """
        if not self.start_drag_slider and self.player.is_playing:
            self.slider.setValue(self.player.current_time)
            self.play_time.setText(seconds2time(self.player.current_time))

    def player_pause(self):
        """
        当播放器进入暂定状态时触发的消息
        这里是修改播放按钮为 播放 图标
        """
        self.to_play_icon()

    def player_proceed(self):
        """
        当播放器恢复播放状态时触发的消息
        这里是修改播放按钮为 暂停 图标
        """
        self.to_pause_icon()

    def player_finished(self):
        """
        当播放结束触发的消息
        这里是修改播放按钮为 播放 图标
        继续播放下一首
        """
        self.to_play_icon()
        self.action_next_song()

    def player_stopped(self):
        """
        手工停止播放触发的消息
        """
        self.to_play_icon()
