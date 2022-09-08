from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from frontend import AboutDialog
from config.config import __APPNAME__
from images import get_img_path


class About(QDialog, AboutDialog):
    def __init__(self, parent):
        super(About, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(__APPNAME__ + ' - About')
        self.set_image()

    def set_image(self):
        img_path = get_img_path('about')
        if img_path is None:
            return
        self.label.setPixmap(QPixmap(img_path))
        self.label.setScaledContents(True)
