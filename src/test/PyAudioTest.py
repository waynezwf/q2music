# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-03
# 说明：PyAudio 音频播放系统测试


import re
import sys
import json
import struct
import subprocess
from tempfile import NamedTemporaryFile
from urllib2 import Request, urlopen
from urllib import urlencode
from PySide.QtGui import QApplication
from pydub.utils import (
    _fd_or_path_or_tempfile,
    get_player_name
)


DEFAULT_TIMEOUT = 30
PLAYER = get_player_name()


def qq_music_searcher(keyword, page=1, page_count=30):
    """
    生成QQ音乐歌曲搜索地址
    :param str keyword: 要搜索的关键字
    :param int page: 页码
    :param int page_count: 页数
    :return: 组织好的搜索地址
    """
    __request_url = "http://s.music.qq.com/fcgi-bin/music_search_new_platform?t=0&aggr=1&cr=1&format=json" + \
                    "&inCharset=GB2312&outCharset=GB2312&notice=0&platform=jqminiframe.json&needNewCode=0" + \
                    "&catZhida=0&remoteplace=sizer.newclient.next_song&{0}"
    params = {
        'w': keyword,
        'p': page,
        'n': page_count,
        'loginUin': ''
    }
    return __request_url.format(urlencode(params))


def qq_music_play_key():
    """
    生成播放KEY请求地址
    :return: 播放KEY请求地址
    """
    __request_url = "http://base.music.qq.com/fcgi-bin/fcg_musicexpress.fcg?json=3&format=jsonp&" + \
                    "inCharset=GB2312&outCharset=GB2312&notice=0&platform=yqq&needNewCode=0&{0}"
    params = {
        'loginUin': ''
    }
    return __request_url.format(urlencode(params))


def strip_html(html_content):
    """
    最简单的过滤 html <> 标签的方法，注意必须是<任意字符>，而不能单纯是<>
    :param str html_content:
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', html_content)
    return clean_text


def json_request(request_url):
    """
    发起json请求，返回json字符串
    :param str request_url:
    :return: json 字符串
    """
    try:
        request = Request(request_url)
        pipe = urlopen(url=request, timeout=DEFAULT_TIMEOUT)
        response = ''
        while True:
            data = pipe.read(1024)
            if not len(data):
                break
            response += data

        return strip_html(response)
    except BaseException as e:
        raise e


def search_song(keyword):
    """
    搜索歌曲
    :param str keyword: 用于搜索的关键字
    :return: list 搜索结果列表，每个元素都是一个 dict 对象
    """
    _url = qq_music_searcher(keyword)
    json_string = json_request(_url)
    song_list_json = json.loads(json_string, encoding='gbk')
    song_list = []
    for song in song_list_json[u'data'][u'song'][u'list']:
        f = song[u'f'].split('|')
        song_info = {
            'pub_time': int(song[u'pubTime'])
        }
        for idx, value in enumerate(f):
            if idx == 0:
                song_info['lrc'] = value
            if idx == 1:
                song_info['name'] = value
            if idx == 2:
                song_info['singer_id'] = value
            if idx == 3:
                song_info['singer_name'] = value
            if idx == 4:
                song_info['album_id'] = value
            if idx == 5:
                song_info['album_name'] = value
            if idx == 20:
                song_info['id'] = value
            if idx == 21:
                song_info['singer_mid'] = value
            if idx == 22:
                song_info['img'] = value

        song_list += [song_info]
    return song_list


def get_play_key():
    """
    获取播放 KEY
    :return: 拥有 播放 KEY 的 dict 对象
    """
    _url = qq_music_play_key()
    json_string = json_request(_url)
    json_string = struct.unpack('13x'+str(len(json_string)-15)+'s2x', json_string)[0]
    play_key_json = json.loads(json_string)
    key_info = {
        'code': play_key_json[u'code'],
        'test_wifi': play_key_json[u'testfilewifi'],
        'key': play_key_json[u'key'],
        'sip': play_key_json[u'sip'],
    }
    return key_info


def get_song_address(song_info, key_info):
    """
    根据一个 song_info 和一个 key_info 生成最终播放地址
    :param song_info: 歌曲信息
    :param key_info: 播放 KEY 信息
    :return: 最终歌曲地址
    """
    return '{0}C100{1}.m4a?vkey={2}&fromtag=0'.format(key_info['sip'][1], song_info['id'], key_info['key'])


def play_from_url(song_url):
    """
    从一个 URL 地址播放一段音乐，这个方式还有一个缺点，就是缓存在本地再开始播放
    如果文件太大，缓存的时间就会很长，用户体验就会很差
    :param song_url: 可以播放的歌曲的地址
    """
    request = Request(song_url)
    pipe = urlopen(url=request, timeout=DEFAULT_TIMEOUT)
    with NamedTemporaryFile("w+b", suffix=".wav") as f:
        f.seek(0)
        f = _fd_or_path_or_tempfile(f, 'wb+')
        print f.name
        while True:
            data = pipe.read(1024)
            if not len(data):
                break
            f.write(data)
        subprocess.call([PLAYER, "-nodisp", "-autoexit", "-hide_banner", f.name])


def main():
    app = QApplication(sys.argv)
    song_list = search_song("周杰伦")
    play_key = get_play_key()
    song_url = get_song_address(song_list[0], play_key)
    play_from_url(song_url)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
