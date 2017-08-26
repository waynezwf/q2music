# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：QQMusic 主程序

import sys
from util.QtAdapter import *
from view.MainWindow import MainWindow


def main():
    qq_music = QApplication(sys.argv)
    win = MainWindow()
    win.center()
    win.show()
    sys.exit(qq_music.exec_())


if __name__ == '__main__':
    main()
