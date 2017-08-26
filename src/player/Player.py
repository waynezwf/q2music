# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-08-10
# 说明：播放器类

from time import sleep
from pydub.playback import *
from util.QtAdapter import *
from pyaudio import PyAudio
from pydub.audio_segment import AudioSegment


class Player(QThread):
    """
    播放器
    """

    def __init__(self):
        """
        初始化播放器
        """
        QThread.__init__(self)
        self.__audio_segment = None             # type: AudioSegment
        self.__start_position = 0               # 开始播放位值

        self.audio = PyAudio()                  # type: PyAudio
        self.exception_list = []                # type: list

        self.chunks = []                        # 要播放的块
        self.loaded_length = 0                  # 已经载入的长度
        self.chunk_duration = 50 / 1000.0       # 块大小，按照时间长度截取，即 0.05 秒每块
        self.time = 0                           # 当前播放时间
        self.volume = 100                       # 播放音量

        self.is_playing = False                 # 是否在播放
        self.is_paused = False                  # 是否已经暂停

    def __del__(self):
        self.stop()
        if not self.wait(500):
            self.terminate()
            self.wait()

    @property
    def has_exception(self):
        """
        :return: 判断是否存在异常
        """
        return len(self.exception_list) > 0

    @property
    def audio_segment(self):
        """
        :return: 音频剪辑对象
        """
        return self.__audio_segment

    @audio_segment.setter
    def audio_segment(self, value):
        """
        设置音频剪辑对象，同时从剪辑中读取 chunks 数据，替换正在播放的 chunks
        在缓存进行过程中，每次发出缓存消息，写入文件之后，都要更新正在播放的 chunks
        必须载入最新缓存的数据再能持续不断的向后播放
        :param value: 音频剪辑对象
        """
        self.__audio_segment = value
        self.setup_chunks_for_cache()

    @property
    def start_position(self):
        """
        :return: 开始播放音乐的位值
        """
        return self.__start_position

    @start_position.setter
    def start_position(self, value):
        """
        更新开始播放音乐的位值，也就是更新正在播放的 chunks 数据
        :param value: 开始播放音乐的位值
        """
        self.__start_position = value
        self.setup_chunks_for_start()

    @property
    def is_valid(self):
        """
        :return: 音频剪辑对象是否已经设置，有效
        """
        return self.audio_segment is not None

    @property
    def duration(self):
        """
        音乐的总时间长度
        :return: 时间长度
        """
        if not self.is_valid:
            return 0
        return self.audio_segment.duration_seconds

    @property
    def current_time(self):
        """
        :return: 当前播放时间
        """
        if not self.is_playing:
            return 0
        return self.time

    def rms_amplitude(self, time, sample_dur):
        """
        音频振幅
        :param float time: 时间
        :param sample_dur: 采样时间
        :return:
        """
        if not self.is_valid:
            return None
        return self.audio_segment[time * 1000.0:(time + sample_dur) * 1000.0].rms

    def setup_chunks_for_cache(self):
        """
        从文件缓冲中载入要播放的 chunks
        由于缓存文件在不停的变化，因此要记录下累计从缓存中载入了多少数据
        下次缓存消息发出的时候，从已经载入的数据位置开始继续载入
        :return: 缓存载入的状态
        """
        if not self.is_valid:
            return False

        start = self.loaded_length
        length = self.duration - self.loaded_length
        self.loaded_length += length

        # 创建要播放的 chunk
        play_chunk = self.audio_segment[start * 1000.0: (start+length) * 1000.0] - \
                     (60 - (60 * (self.volume / 100.0)))
        self.chunks += make_chunks(play_chunk, self.chunk_duration * 1000)
        return True

    def setup_chunks_for_start(self):
        """
        从指定的点开始播放，设置要播放的 chunks
        一般是在用户拉动播放进度条的时候发生，需要整体重新改写所有要播放的 chunks
        会与缓存载入发生冲突，即数据尚未载入，但从 song_info 参数上看，音乐的长度数据是已经存在的。
        :return:
        """
        if not self.is_valid:
            return False

        length = self.duration - self.start_position

        # 创建要播放的 chunk
        play_chunk = self.audio_segment[self.start_position * 1000.0: (self.start_position + length) * 1000.0] - \
                     (60 - (60 * (self.volume / 100.0)))
        self.chunks = make_chunks(play_chunk, self.chunk_duration * 1000)
        return True

    def play(self):
        """
        从 self.start_position 时间开始播放音乐
        """
        if not self.is_valid:
            return False

        self.is_playing = True
        self.emit(SIGNAL('before_play()'))                  # 发出准备播放的消息
        self.time = self.start_position

        audio_stream = self.audio.open(
            format=self.audio.get_format_from_width(self.audio_segment.sample_width),
            channels=self.audio_segment.channels,
            rate=self.audio_segment.frame_rate,
            output=True
        )

        index = 0
        # for chunk in self.chunks:
        while True:
            if not self.is_playing:                         # 停止播放，退出播放循环
                break

            while self.is_paused:                           # 暂停播放，进入阻塞循环
                sleep(0.5)
                continue

            if self.time >= self.duration:                  # 播放完毕，退出播放循环
                self.emit(SIGNAL('play_finished()'))        # 发出播放完毕的消息
                break
            self.time += self.chunk_duration

            if index < len(self.chunks):                    # 将 chunk 数据写入声卡，播放
                audio_stream.write(self.chunks[index].raw_data)
                index += 1

            # 线程中的消息会有退出异常的现象
            # 继续等待即可，直到线程退出
            try:
                self.emit(SIGNAL('playing()'))              # 发出正在播放的消息
            except Exception as e:
                continue

        audio_stream.close()
        self.is_playing = False
        self.emit(SIGNAL('stopped()'))                      # 发出停止播放的消息

    def stop(self):
        """
        停止播放，进行线程等待结束
        """
        self.is_playing = False
        self.start_position = 0

    def pause(self):
        """
        停止播放
        """
        self.is_paused = True
        self.emit(SIGNAL('pause()'))                        # 发出播放暂停的消息

    def proceed(self):
        """
        继续播放，即退出暂停状态
        """
        self.is_paused = False
        self.emit(SIGNAL('proceed()'))                      # 发出恢复播放的消息

    def run(self, *args, **kwargs):
        """
        开始播放
        """
        self.play()
