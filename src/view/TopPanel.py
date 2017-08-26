# -*- coding: utf-8 -*-
# 作者：wayne zhang
# 时间：2017-07-29
# 说明：窗口组件

from config.Config import *
from util.QtAdapter import *
from time import sleep


class WaitingAnimation(QThread):
    """
    等待动画
    """

    def __init__(self):
        QThread.__init__(self)
        self.waiting_images = []
        self.stop_waiting = False
        self.wait_times = 0
        self.__init_wait_flash()

    def __init_wait_flash(self):
        """
        载入用于显示等待动画的图片，并按照角度生成多张图片
        """
        image_width = 46.0                          # 缩放到 45px 的正方形
        img = QImage()                              # type: QImage
        img.load(QM_ICON_PATH + 'waiting.svg')
        img = img.scaled(image_width, image_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.waiting_images.append(QPixmap(img))

        rotates = [45, 90, 135, 180, 225, 270, 315]
        for rotate in rotates:
            transform = QTransform().rotate(rotate)
            t_img = img.transformed(transform, Qt.SmoothTransformation)  # type: QImage

            s = (t_img.width() - image_width) / 2
            if rotate == 45:
                t_img = t_img.copy(s, s, image_width, image_width)
            if rotate == 135:
                t_img = t_img.copy(s, s, image_width, image_width)
            if rotate == 225:
                t_img = t_img.copy(s, s, image_width, image_width)
            if rotate == 315:
                t_img = t_img.copy(s, s, image_width, image_width)

            self.waiting_images.append(QPixmap(t_img))

    def __del__(self):
        """
        退出时等待线程结束
        :return:
        """
        self.stop_waiting = True
        if not self.wait(500):
            self.terminate()
            self.wait()

    @property
    def waiting_image(self):
        """
        返回这次等待的图片数据
        :return: 当前等待次数对应的图片
        """
        return self.waiting_images[self.wait_times % len(self.waiting_images)]
        
    def run(self, *args, **kwargs):
        while True:
            if self.stop_waiting:
                break

            # 线程中的消息会有退出异常的现象
            # 继续等待即可，直到线程退出
            try:
                self.wait_times += 1
                self.emit(SIGNAL('waiting()'))
                sleep(0.1)
            except Exception as e:
                continue


class TopPanel(QFrame):
    """
    顶部面板，提供关键字输入和有关的按钮
    """

    def __init__(self):
        QFrame.__init__(self)
        self.__init_ui()

        self.is_waiting = False
        self.transform = QTransform()
        self.waiting_animation = WaitingAnimation()
        self.waiting_animation.connect(SIGNAL('waiting()'), self.show_waiting)
        self.waiting_animation.start()

    def __init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 10, 10, 10)
        self.setLayout(self.layout)

        self.qq_music = QLabel()
        qq_music_map = QPixmap()
        qq_music_map.loadFromData(QM_DEFAULT_ICON_DATA)
        qq_music_map = qq_music_map.scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.qq_music.setPixmap(qq_music_map)
        self.layout.addWidget(self.qq_music)
        self.layout.addStretch(1)

        self.waiting = QLabel()
        self.waiting.setAlignment(Qt.AlignCenter)
        self.waiting.setProperty('class', 'waiting')
        self.waiting.setVisible(False)

        waiting_layout = QHBoxLayout()
        waiting_layout.setSpacing(0)
        waiting_layout.setContentsMargins(0, 0, 30, 0)
        waiting_layout.addWidget(self.waiting)
        self.layout.addLayout(waiting_layout)

        self.edt_search = QLineEdit()
        self.edt_search.setProperty('class', 'search_editor')
        self.edt_search.setText(QM_SEARCH_KEYWORD)
        self.layout.addWidget(self.edt_search)

        self.btn_search = QToolButton()
        self.btn_search.setProperty('class', 'highlight_button')
        self.btn_search.setIcon(QIcon(QM_ICON_PATH + 'search.svg'))
        self.layout.addWidget(self.btn_search)

        self.btn_menu = QToolButton()
        self.btn_menu.setProperty('class', 'highlight_button')
        self.btn_menu.setIcon(QIcon(QM_ICON_PATH + 'menu.svg'))
        self.layout.addWidget(self.btn_menu)

    def show_waiting(self):
        """
        显示旋转等待的动画
        """
        if self.is_waiting:
            self.waiting.setVisible(True)
            self.waiting.setPixmap(self.waiting_animation.waiting_image)
        else:
            self.waiting.setVisible(False)
