# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-08-10
# 说明：TencentProtocol 解析腾讯音乐数据的协议对象

import os
import json
import re
import requests
from config.Config import *
from util.QtAdapter import *
from urllib import quote
from urllib2 import Request, urlopen
from util.Utilities import seconds2time
from protocol.SongInfo import SongInfo


class TencentProtocol(QThread):
    """
    腾讯音乐协议
    """

    @classmethod
    def qq_play_key(cls, song_mid, guid, file_extension='m4a'):
        """
        生成播放KEY请求地址，高质量音乐播放每首歌都必须请求一次播放键
        :param str song_mid: 歌曲mid
        :param str guid: guid
        :param str file_extension: 文件扩展名
        :return: 播放KEY请求地址
        """
        return QM_PLAY_KEY_URL.format(song_mid, file_extension, guid)

    @classmethod
    def qq_searcher(cls, keyword, page_index, page_size):
        """
        生成QQ音乐歌曲搜索地址
        :param int page_index: 页码
        :param int page_size: 每页显示的数据量
        :param str keyword: 搜索关键字
        :return: 组织好的搜索地址
        """
        keyword = quote(keyword)
        return QM_SEARCH_URL.format(page_index, page_size, keyword)

    @classmethod
    def qq_image(cls, album_mid, width=90):
        """
        生成QQ音乐歌曲搜索地址
        :param str album_mid: 专辑ID
        :param int width: 图片宽度，支持90、180、300
        :return: 组织好的图片地址
        """
        return QM_IMG_URL.format(width, album_mid)

    @classmethod
    def json_request(cls, request_url):
        """
        发起json请求，返回json字符串
        :param str request_url:
        :return: json 字符串
        """
        try:
            request = Request(request_url)
            request.headers['user-agent'] = QM_USER_AGENT
            pipe = urlopen(url=request, timeout=QM_TIMEOUT)
            response = ''
            while True:
                data = pipe.read(1024)
                if not len(data):
                    break
                response += data
            return response
        except BaseException as e:
            e.message += u"获取 JSON 数据错误。"
            raise e

    @classmethod
    def strip_html(cls, html_content):
        """
        最简单的过滤 html <> 标签的方法，注意必须是<任意字符>，而不能单纯是<>
        :param str html_content:
        """
        clean = re.compile('<.*?>')
        clean_text = re.sub(clean, '', html_content)
        return clean_text

    @classmethod
    def decode_korean(cls, string, prefix='&#', postfix=';'):
        """
        韩文解码函数
        :param str string: 需要解码的韩文 Unicode 数据
        :param str prefix: 韩文 Unicode 编码的开始符号
        :param str postfix: 韩文 Unicode 编码的结束符号
        :return: 解码后的 UTF-8 文本内容
        """
        exp = prefix + r"(\d{5}?)" + postfix
        code_list = re.findall(exp, string)
        for code in code_list:
            u_code = u'{0}'.format('\u' + hex(int(code))[2:6])
            word = u_code.decode('unicode-escape')
            string = string.replace(prefix + code + postfix, word)
            string = string.decode('utf-8')
        return string

    def __init__(self):
        QThread.__init__(self)
        self.exception_list = []        # type: list
        self.song_list = []             # type: list
        self.play_key = {}              # type: dict

        self.keyword = ''               # type: str
        self.page_index = 1             # type: int
        self.page_size = 20             # type: int

    @property
    def has_exception(self):
        """
        :return: 是否存在异常
        """
        return len(self.exception_list) > 0

    def search_song(self):
        """
        搜索歌曲
        """
        song_list = []
        self.exception_list = []
        try:
            _url = self.qq_searcher(self.keyword, self.page_index, self.page_size)
            json_string = self.json_request(_url)
            json_string = json_string[9:len(json_string) - 1]
            song_list_json = json.loads(json_string)
            # print json.dumps(song_list_json, indent=4, sort_keys=True)

            for song in song_list_json[u'data'][u'song'][u'list']:
                song_info = SongInfo()
                song_info.album_id = int(song[u'albumid'])
                song_info.album_mid = song[u'albummid']
                song_info.album_name = self.decode_korean(song[u'albumname'])
                song_info.id = int(song[u'songid'])
                song_info.mid = song[u'songmid']
                song_info.name = self.decode_korean(song[u'songname'])
                song_info.interval = int(song[u'interval'])
                song_info.length = seconds2time(int(song[u'interval']))
                song_info.pub_time = int(song[u'pubtime'])
                song_info.url = song[u'songurl'] if u'songurl' in song else ''
                song_info.nt = int(song[u'nt'])
                song_info.singer = []
                song_info.singer_names = ''

                singer_names = []
                for sg in song[u'singer']:
                    name = self.decode_korean(sg[u'name'])
                    singer = {
                        'id': int(sg[u'id']),
                        'mid': sg[u'mid'],
                        'name': name
                    }
                    singer_names.append(name)
                    song_info.singer += [singer]
                song_info.singer_names = u'，'.join(singer_names)

                song_list += [song_info]
        except BaseException as e:
            e.message += u"搜索音乐信息错误。"
            self.exception_list.append(e)

        self.song_list = song_list
        self.emit(SIGNAL('search_complete()'))

    def get_play_key(self, song_info):
        """
        获取播放 KEY
        :param SongInfo song_info: 歌曲信息
        """
        try:
            url = self.qq_play_key(str(song_info.mid), str(song_info.nt))
            json_string = self.json_request(url)
            json_string = json_string[18:len(json_string) - 1]
            play_key_json = json.loads(json_string)
            play_key_item = play_key_json[u'data'][u'items'][0]

            song_info.filename = play_key_item[u'filename']
            song_info.vkey = play_key_item[u'vkey']
        except BaseException as e:
            self.exception_list.append(e)

        self.emit(SIGNAL('after_play_key()'))

    def get_song_address(self, song_info):
        """
        根据每首歌的 song_info 和 play_key 生成最终播放地址
        这里推荐在搜索歌曲之前，首先取得播放键信息，然后同步生成地址
        :param SongInfo song_info: 歌曲信息
        :return: 歌曲地址
        """
        if song_info.id is None:
            e = Exception(u"音乐信息不完整无法获取歌曲地址。")
            self.exception_list.append(e)
            raise e

        url = QM_SONG_URL.format(
            song_info.filename,
            song_info.vkey,
            song_info.nt,
        )
        song_info.song_url = url
        self.emit(SIGNAL('song_address_complete()'))
        return url

    def get_image_address(self, song_info):
        """
        根据每首歌的 song_info 和 获取图片的地址
        这里推荐在搜索歌曲之前，首先取得播放键信息，然后同步生成地址
        :param SongInfo song_info: 歌曲信息
        :return: 歌曲地址
        """
        if song_info.id is None:
            e = Exception(u"音乐信息不完整无法获取歌曲图片地址。")
            self.exception_list.append(e)
            raise e

        url = self.qq_image(str(song_info.album_mid))
        song_info.image_url = url
        self.emit(SIGNAL('image_address_complete()'))
        return url

    def download(self, song_info, download_path=QM_DEFAULT_DOWNLOAD_PATH):
        """
        下载高品质音乐
        :param SongInfo song_info: 歌曲信息
        :param str download_path: 保存下载歌曲的路径
        """
        if song_info.song_url is None:
            self.get_play_key(song_info)
            self.get_image_address(song_info)
            self.get_song_address(song_info)

        try:
            filename = song_info.name + '-' + song_info.singer_names

            image_data = requests.get(song_info.image_url).content
            image_file = download_path + filename + '.jpg'
            if os.path.isfile(image_file):
                os.remove(image_file)
            with open(image_file, 'wb') as cover_file:
                cover_file.write(image_data)
                song_info.image_path = cover_file.name

            ext_name = song_info.filename[len(str(song_info.filename)) - 3: len(str(song_info.filename))]
            audio_file = download_path + filename + '.' + ext_name

            request = Request(song_info.song_url)
            pipe = urlopen(url=request, timeout=QM_TIMEOUT)
            if os.path.isfile(audio_file):
                os.remove(audio_file)
            with open(audio_file, 'w+b') as f:
                f.seek(0)
                while True:
                    data = pipe.read(QM_BUFFER_SIZE)
                    if data is None or not len(data):
                        break
                    f.write(data)
                song_info.song_path = f.name
        except Exception as e:
            self.exception_list.append(e)

        self.emit(SIGNAL('after_download(PyObject)'), song_info)

    def run(self, *args, **kwargs):
        self.search_song()
