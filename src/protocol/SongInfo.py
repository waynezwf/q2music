# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-08-10
# 说明：SongInfo 歌曲信息类


class SongInfoTag(object):
    """
    音乐信息 Tag 属性项
    """
    pass


class SongMetaclass(type):
    """
    用元类的方式初始化音乐信息类，自动增加对应的属性
    """

    @classmethod
    def __new__(mcs, *more):
        class_name = more[1]                    # type: str
        super_classes = more[2]                 # type: tuple
        attributes = more[3]                    # type: dict
        mappings = dict()

        for k, v in attributes.items():
            if isinstance(v, SongInfoTag):
                mappings[k] = v
                attributes.pop(k)
        attributes['__mappings__'] = mappings
        return type.__new__(mcs, class_name, super_classes, attributes)


class SongInfo(dict):
    """
    歌曲信息类
    使用元类初始化下面的属性，便于动态增加删除属性
    如果有属性需要修改，只要增加或删除下面的某一行即可

    同时具有 dict 类的所有属性，而且可以通过属性的方式操作 SongInfo 的实例对象
    """
    album_id = SongInfoTag()
    album_mid = SongInfoTag()
    album_name = SongInfoTag()
    id = SongInfoTag()
    mid = SongInfoTag()
    name = SongInfoTag()
    interval = SongInfoTag()
    length = SongInfoTag()
    pub_time = SongInfoTag()
    url = SongInfoTag()
    nt = SongInfoTag()
    singer = SongInfoTag()
    singer_names = SongInfoTag()
    filename = SongInfoTag()
    vkey = SongInfoTag()

    song_url = SongInfoTag()
    image_url = SongInfoTag()

    song_path = SongInfoTag()
    image_path = SongInfoTag()

    __metaclass__ = SongMetaclass

    def __init__(self, **kwargs):
        super(SongInfo, self).__init__(**kwargs)
        for k, v in self.__mappings__.iteritems():
            self[k] = None

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            dict.__getitem__(self, key)

    def __setattr__(self, key, value):
        if key in self:
            self[key] = value
        else:
            dict.__setattr__(self, key, value)


def main():
    si = SongInfo()
    si.name = []
    print 'name' in si


if __name__ == '__main__':
    main()
