from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap


class ImageLabel(QLabel):
    def __init__(self, parent):
        super(ImageLabel, self).__init__(parent)

        self.cur_image = None
        self.fit_type = 'width'

    def set_image(self, image):
        self.cur_image = image
        # 转换为QImage格式
        # show_image = QImage(image.copy(), image.shape[1], image.shape[0],
        #                     QImage.Format_RGB888)
        show_image = image

        # 图像适应QLabel控件的大小
        label_width, label_height = (self.width(), self.height())
        # image_height, image_width = image.shape[:2]
        image_height = show_image.height()
        image_width = show_image.width()

        border = 0
        if self.fit_type == 'width':
            # 转为 label_image 大小
            width_ratio = label_width / image_width
            height_ratio = label_height / image_height
            if width_ratio < height_ratio:
                zoom_ratio = width_ratio
                width_border = border
                height_border = int(width_border * (image_height / image_width))
            else:
                zoom_ratio = height_ratio
                height_border = border
                width_border = int(height_border * (image_width / image_height))
            visual_size = QSize(int(zoom_ratio * image_width) - width_border,
                                int(zoom_ratio * image_height - height_border))
        else:
            width_border = border
            # height_border = int(width_border * (label_height / label_width))
            height_border = width_border
            visual_size = QSize(label_width - width_border, label_height - height_border)

        show_image = show_image.scaled(visual_size, Qt.IgnoreAspectRatio)
        self.setPixmap(QPixmap.fromImage(show_image))

    def fit_width(self):
        self.fit_type = 'width'
        if self.cur_image is not None:
            self.set_image(self.cur_image)

    def fit_window(self):
        self.fit_type = 'window'
        if self.cur_image is not None:
            self.set_image(self.cur_image)

    def clear(self):
        self.cur_image = None
        super(ImageLabel, self).clear()

    def resizeEvent(self, event):
        if self.cur_image is not None:
            self.set_image(self.cur_image)
        super(ImageLabel, self).resizeEvent(event)
