# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-08-10
# 说明：播放器类

import os
import requests
from time import sleep
from config.Config import *
from util.QtAdapter import *
from util.Utilities import seconds2time
from urllib2 import Request, urlopen
from pydub.audio_segment import AudioSegment
from protocol.SongInfo import SongInfo
from protocol.TencentProtocol import TencentProtocol

AUDIO_FROM_INTERNET = 0x01       # 网络音乐
AUDIO_FROM_LOCAL = 0x02          # 本地音乐


class AudioLoader(QThread):
    """
    AudioLoader 音频文件装载器，负责从 URL 载入音频文件
    首先检查缓存目录中是否存在对应，并有效的音频文件
    如果有缓存，则从缓存中直接载入，否则从网络缓存
    audio_loader = AudioLoader()
    audio_loader.song_info = song_info
    audio_loader.start()
    """

    def __init__(self):
        QThread.__init__(self)
        self.__song_info = SongInfo                 # type: SongInfo

        self.exception_list = []                    # type: list
        self.is_stop = False                        # 退出

        self.source_type = AUDIO_FROM_INTERNET      # 默认来源设置为互联网
        self.audio_segment = None                   # type: AudioSegment
        self.image_data = ''                        # type: str

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
    def song_info(self):
        """
        :return: 需要载入的歌曲信息
        """
        return self.__song_info

    @song_info.setter
    def song_info(self, value):
        """
        :param SongInfo value: 需要载入的歌曲信息
        """
        self.__song_info = value

    def check_audio_cache(self):
        """
        检查缓存文件是否存在，且是否缓存完毕
        :return: False 或 AudioSegment 对象
        """
        cache_song = QM_DEFAULT_CACHE_PATH + str(self.song_info.filename)
        if not os.path.isfile(cache_song):
            return False
        if os.path.getsize(cache_song) < 1024:
            return False

        audio_seg = AudioSegment.from_file(cache_song)

        interval = int(self.song_info.interval) * 1000
        duration = audio_seg.duration_seconds * 1000
        if duration > interval:
            return audio_seg
        else:
            return False

    def check_image_cache(self):
        """
        检查封面缓存文件是否存在
        :return: False 或 image_data 图片数据
        """
        if self.song_info.image_path is None:
            return False

        image_path = self.song_info.image_path
        if not os.path.isfile(image_path):
            return False
        if os.path.getsize(image_path) == 0:
            return False

        image_data = open(image_path, 'rb').read()
        return image_data

    def cache_from_url(self):
        """
        从一个 URL 地址获取音乐数据，并缓存在临时目录中
        实际装载的过程是首先检查缓存目录中是否存在有效的音乐副本和封面图片副本
        如果有，就直接从缓存播放，否则从网络下载，并缓存
        :return: 返回缓存的临时文件对象
        """
        self.emit(SIGNAL('before_cache()'))
        self.is_stop = False
        self.exception_list = []
        try:
            if self.song_info.song_url is None:
                tencent = TencentProtocol()
                tencent.get_play_key(self.song_info)
                tencent.get_song_address(self.song_info)
                tencent.get_image_address(self.song_info)
                if tencent.has_exception:
                    self.exception_list += tencent.exception_list
                    raise tencent.exception_list[0]

            # 首先尝试从本地缓存中载入封面图片，未找到则下载并缓存
            self.image_data = self.check_image_cache()
            if not self.image_data:
                """
                从网络读取专辑封面，并写入本地缓存文件
                """
                self.image_data = requests.get(self.song_info.image_url).content
                cache_image_path = QM_DEFAULT_CACHE_PATH + str(self.song_info.mid) + '.jpg'
                if os.path.isfile(cache_image_path):
                    os.remove(cache_image_path)
                with open(cache_image_path, 'wb') as cover_file:
                    cover_file.write(self.image_data)

            # 首先尝试从本地缓存中载入音频文件，未找到则下载并缓存
            cache_audio = self.check_audio_cache()
            if isinstance(cache_audio, AudioSegment):
                """
                从缓存载入音频
                """
                self.audio_segment = cache_audio
                self.emit(SIGNAL('caching()'))
            else:
                """
                从网络缓存音频，并写入本地缓存
                """
                request = Request(self.song_info.song_url)
                pipe = urlopen(url=request, timeout=QM_TIMEOUT)

                cache_file = QM_DEFAULT_CACHE_PATH + str(self.song_info.filename)
                if os.path.isfile(cache_file):
                    os.remove(cache_file)
                with open(cache_file, 'wb') as audio_file:
                    while True:
                        data = pipe.read(QM_BUFFER_SIZE)

                        if self.is_stop or data is None or len(data) == 0:
                            audio_file.close()
                            break

                        # print 'wirte >>> ' + str(self.song_info.name) + ' >>> ' + filename
                        audio_file.write(data)
                        sleep(0.01)
                        self.audio_segment = AudioSegment.from_file(audio_file.name)
                        self.emit(SIGNAL('caching()'))
                    audio_file.close()
        except RuntimeError as e:
            e.message += u"运行时错误。"
            self.exception_list.append(e)
        except BaseException as e:
            e.message += u"获取音乐数据错误。"
            self.exception_list.append(e)

        self.is_stop = True
        self.emit(SIGNAL('after_cache()'))

    def cache_from_local(self):
        """
        从本地载入音频数据
        发送消息必须与 cache_from_url 一致，以便外部程序获取消息进行后续操作
        其中专辑封面图片文件如果没有找到，则使用默认的封面图片 LOGO
        同时需要补充音频的时间长度数据
        """
        self.emit(SIGNAL('before_cache()'))
        if self.song_info is None:
            self.stop()
            return

        self.image_data = self.check_image_cache()
        if not self.image_data:
            self.image_data = QM_DEFAULT_ICON_DATA
        self.audio_segment = AudioSegment.from_file(self.song_info.song_path)

        # 下面是补充两项属性，音频的秒数和转换为时间格式的时长
        self.song_info.interval = int(round(self.audio_segment.duration_seconds))
        self.song_info.length = seconds2time(self.audio_segment.duration_seconds)

        self.emit(SIGNAL('caching()'))
        self.is_stop = True
        self.emit(SIGNAL('after_cache()'))

    def stop(self):
        """
        停止继续下载，进行线程等待结束
        """
        self.is_stop = True

    def run(self, *args, **kwargs):
        if self.source_type == AUDIO_FROM_INTERNET:
            self.cache_from_url()
        elif self.source_type == AUDIO_FROM_LOCAL:
            # 从本地缓存读取音频文件时要求 song_info 必须具有 file_path 键值
            self.cache_from_local()
