# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-08-10
# 说明：

from util.Utilities import get_main_dir

QM_TIMEOUT = 30
QM_BUFFER_SIZE = 1024*200
QM_ICON_PATH = get_main_dir() + "res/icons/"                        # 以相对路径方式载入 ICON 图标
QM_QSS_PATH = get_main_dir() + "res/css/WRadio.css"                 # 以绝对路径方式载入 QSS 样式表
QM_USER_AGENT = "Linux LQQ Music Ver.1.0.0 Contact by zwf2005@gmail.com"


QM_DEFAULT_CACHE_PATH = get_main_dir() + 'cache/'                   # 默认的缓存目录
QM_DEFAULT_DOWNLOAD_PATH = get_main_dir() + 'download/'             # 默认的下载目录
QM_DEFAULT_IMAGE_ICON = QM_ICON_PATH + 'qq_music.png'               # 默认图标路径
QM_DEFAULT_ICON_DATA = open(QM_DEFAULT_IMAGE_ICON, 'rb').read()


QM_SEARCH_KEYWORD = u"李宗盛"

# 下面是高质量音乐搜索地址
# {0}: p，从 1 开始的页码
# {1}: n，每页显示的记录数量
# {2}: w，搜索关键字
QM_SEARCH_URL = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?t=0&aggr=1&cr=1&lossless=0&flag_qc=0&" \
                "loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&" \
                "needNewCode=0&p={0}&n={1}&w={2}"

# 下面这个参数是每首歌都要读取一次才能获得高品质的音乐（100kbps或以上）。
# {0}: song_mid，如：000ERLS42TAqgE
# {1}: file_extension，文件扩展名，默认是m4a，可以修改为mp3或者ape、flac等
# {2}: guid，标识获取key的唯一ID，可以是任意数字，不能丢弃，后面播放的时候还要用到
QM_PLAY_KEY_URL = "https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?loginUin=0&" \
                  "hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&cid=205361747&" \
                  "callback=MusicJsonCallback&uin=0&songmid={0}&filename=C400{0}.{1}&guid={2}"

# 高质量音乐播放地址
# {0}: filename，文件名，如：C400000ERLS42TAqgE.m4a，由上一步确定扩展名
# {1}: vkey，在上一步中获得的播放key
# {2}: guid，标识获取key的唯一ID，可以是任意数字，不能丢弃，后面播放的时候还要用到
QM_SONG_URL = "http://dl.stream.qqmusic.qq.com/{0}?vkey={1}&guid={2}&fromtag=66"

# 高质量音乐下载地址，这个没有测试
# {0}: songid，如：101803854，转换为整数之后，+ 3e7
QM_SONG_DOWNLOAD_URL = "http://stream17.qqmusic.qq.com/{0}.mp3"

# 高品质音乐封面地址，关于图片的尺寸，目前测试可得：90x90 180x180 300x300
# {0}: width 和 height 两个值相同
# {1}: album_mid，如：002xOmp62kqSic
QM_IMG_URL = "https://y.gtimg.cn/music/photo_new/T002R{0}x{0}M000{1}.jpg?max_age=2592000"