# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-08-10
# 说明：杂项方法

import imp
import os
import sys


def main_is_frozen():
    """
    执行环境判断
    :return:
    """
    return (hasattr(sys, "frozen") or       # new py2exe
            hasattr(sys, "importers") or    # old py2exe
            imp.is_frozen("__main__"))      # tools/freeze


def get_main_dir():
    """
    获取主程序的执行目录
    :return:
    """
    if main_is_frozen():
        return os.path.abspath(os.path.dirname(sys.executable))
    _file_path = os.path.dirname(os.path.abspath(__file__)).decode('utf-8')
    return u"{0}/../../".format(_file_path)


def which(program):
    """
    查找指定程序的所在位置
    :param program:
    :return:
    """

    def is_exe(fpath):
        """
        路径指定的是否是可执行程序
        :param fpath:
        :return:
        """
        if os.name == 'nt':
            return os.path.isfile(fpath) or os.path.isfile(fpath + ".exe") or os.path.isfile(fpath + ".bat")
        else:
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        program = os.path.realpath(program)
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            exe_file = os.path.realpath(exe_file)
            if is_exe(exe_file):
                return exe_file

    return None


def seconds2time(seconds):
    """
    秒数转换单位时间
    :param float seconds:
    :return: str
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def main():
    print main_is_frozen()
    print get_main_dir()
    print which("ffmpeg")


if __name__ == '__main__':
    main()
