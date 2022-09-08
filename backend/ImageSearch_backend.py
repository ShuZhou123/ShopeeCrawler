import requests
from PyQt5.QtCore import pyqtSignal, QThread


class ImageSearcher(QThread):
    data = pyqtSignal(tuple, bool, str)

    def __init__(self, base_url):
        super(ImageSearcher, self).__init__()
        self.base_url = base_url
        self.is_running = False

    def search(self, image_ids):
        self.is_running = True
        for i in range(len(image_ids)):
            pass