import os
import cv2
import requests
import pyperclip  # 复制内容到粘贴板
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
from skimage.metrics import structural_similarity as SSIM


from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, \
    QMessageBox, QTableWidgetItem, QLineEdit, QProgressBar, \
    QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap

from frontend import MainWindow
from backend import About
from images import get_img_path
from config.config import __APPNAME__, __VERSION__,\
    CATEGORY_ID_MAP, SORT_MAP, BASE_URL, CRAWL_PARAMS, \
    LOCATION_MAP, FILTER_MAP, IMAGE_BASE_URL


class Main(QMainWindow, MainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.craw_params = CRAWL_PARAMS.copy()
        self.item_page = []
        self.item_id = []
        self.shop_id = []

        self.imagetab_result = []

        self.titletab_item_links = []
        self.titletab_item_titles = []

        self._ui_init_()

    def _ui_init_(self):
        self.setupUi(self)

        self.setWindowTitle(__APPNAME__ + ' v' + __VERSION__)

        # 禁用当前未完成功能
        # self.actionReset.setEnabled(False)
        self.actionSetting.setEnabled(False)
        self.actionReleaseNotes.setEnabled(False)
        self.titletab_save_button.setEnabled(False)
        self.titletab_filepath_edit.setEnabled(False)
        self.titletab_selectfile_button.setEnabled(False)
        self.titletab_autosave_checkbox.setEnabled(False)

        # 初始化界面
        self.update_ui('init')

        # 设置图标
        logo_path = get_img_path('logo')
        print(logo_path)
        self.setWindowIcon(QIcon(logo_path))

        # 使窗口在屏幕居中
        geo = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

        # 添加Category选项
        for cat in CATEGORY_ID_MAP.keys():
            self.category_box.addItem(cat)
            self.imagetab_category_box.addItem(cat)  # 以图搜图界面的cat
        # 设置显示的选项
        self.category_box.setCurrentText('Deportes y Fitness')
        self.imagetab_category_box.setCurrentText('Deportes y Fitness')  # 以图搜图界面的cat
        # 显示居中
        temp = QLineEdit()
        temp.setReadOnly(True)
        temp.setAlignment(Qt.AlignCenter)
        self.category_box.setLineEdit(temp)

        # 添加Filter选项
        for t in FILTER_MAP.keys():
            self.filter_box.addItem(t)
        # 设置显示的选项并居中显示
        self.filter_box.setCurrentText('Precio')
        temp = QLineEdit()
        temp.setReadOnly(True)
        temp.setAlignment(Qt.AlignCenter)
        self.filter_box.setLineEdit(temp)
        # 添加排序选项
        for t in SORT_MAP.keys():
            self.sort_box.addItem(t)
        # 设置显示的选项并居中显示
        self.sort_box.setCurrentText('Ascending')
        temp = QLineEdit()
        temp.setReadOnly(True)
        temp.setAlignment(Qt.AlignCenter)
        self.sort_box.setLineEdit(temp)
        # 添加进度条与信息栏
        self.progress_bar = QProgressBar()
        self.message_label = QLabel()
        self.statusbar.addPermanentWidget(self.progress_bar, stretch=4)
        self.statusbar.addPermanentWidget(self.message_label, stretch=2)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.progress_bar.hide()
        self.message_label.setText('准备就绪')
        # self.progress_bar.setRange(0, 100)
        # self.progress_bar.setValue(20)
        # self.message_label.setText('正在爬取第1页')

        # 绑定事件
        # 菜单栏
        self.actionReset.triggered.connect(self.reset_ui)
        self.actionAbout.triggered.connect(lambda: self.open_window('about'))
        self.actionMaximize.triggered.connect(lambda: self.switch_window_mode('max'))
        self.actionMinimize.triggered.connect(lambda: self.switch_window_mode('min'))
        self.actionNormal.triggered.connect(lambda: self.switch_window_mode('normal'))
        self.actionFullScreen.triggered.connect(lambda: self.switch_window_mode('full'))
        self.actionExit.triggered.connect(self.close)

        # Search Tab
        self.search_button.clicked.connect(self.search)
        self.clear_button.clicked.connect(self.clear_table)
        self.save_button.clicked.connect(lambda: self.save_data('user'))
        self.filter_box.currentTextChanged.connect(self.switch_filter)

        # Image Tab
        self.imagetab_search_button.clicked.connect(self.image_search_click)
        self.imagetab_save_button.clicked.connect(lambda: self.imagetab_save_data('user'))

        # Title Tab
        self.titletab_start_button.clicked.connect(self.title_start)
        self.titletab_copy_button.clicked.connect(self.copy_titles)

    def search(self):
        # 更新ui
        self.update_ui('running')

        # 清空当前表格
        self.clear_table()
        self.result_title_label.setText('结  果')

        cat_name = self.category_box.currentText()
        cat_id = CATEGORY_ID_MAP[cat_name]
        filter_name = self.filter_box.currentText()
        filter_id = FILTER_MAP[filter_name]
        order_name = self.sort_box.currentText()
        order_id = SORT_MAP[order_name]
        keyword = self.keyword_edit.text()
        page = int(self.page_box.text())
        location = self.get_location()

        # 初始化progress bar
        self.progress_bar.show()
        self.progress_bar.setRange(0, page)

        # 构造请求参数
        self.craw_params['keyword'] = keyword
        self.craw_params['limit'] = 60
        self.craw_params['match_id'] = cat_id
        self.craw_params['by'] = filter_id
        self.craw_params['order'] = order_id
        self.craw_params['locations'] = location

        # 请求
        res = []
        for i in range(page):
            # 更新message
            self.message_label.setText('正在爬取第%d页' % (i + 1))

            start_index = i * 60
            self.craw_params['newest'] = start_index
            print('Page', (i + 1))
            print(self.craw_params)
            try:
                response = requests.get(BASE_URL, params=self.craw_params).json()
                item_info = response['items']
                print('Number of Data:', len(item_info))
                if len(item_info) == 0:
                    if i == 0:
                        QMessageBox.warning(self, 'Warning', '未查询到对应信息！')
                        self.progress_bar.setValue(0)
                        self.progress_bar.hide()
                        self.message_label.setText('搜索异常结束: 无有效数据')
                        self.update_ui('stopped')
                        return
                    else:
                        break
            except Exception as e:
                print('Error')
                print(str(e))
                QMessageBox.warning(self, 'Warning', 'Crawler failed\n' + str(e))
                self.progress_bar.setValue(0)
                self.progress_bar.hide()
                self.message_label.setText('搜索异常结束')
                self.update_ui('init')
                return
            else:
                for item in item_info:
                    self.item_page.append(i + 1)
                    self.item_id.append(item['itemid'])
                    self.shop_id.append(item['shopid'])

            # 更新progress bar
            self.progress_bar.setValue(i + 1)
        print('Number of items:', len(res))

        # 添加内容
        # for item in res:
        for i in range(len(self.item_page)):
            row_count = self.result_table.rowCount()
            self.result_table.insertRow(row_count)
            item_page = QTableWidgetItem(str(self.item_page[i]))
            item_id = QTableWidgetItem(str(self.item_id[i]))
            shop_id = QTableWidgetItem(str(self.shop_id[i]))
            self.result_table.setItem(row_count, 0, item_page)
            self.result_table.setItem(row_count, 1, item_id)
            self.result_table.setItem(row_count, 2, shop_id)

        self.update_ui('stopped')

        # 搜索完成
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.message_label.setText('搜索完成')

        # 更新页数和数据计数
        self.total_page_label.setText(str(max(self.item_page)))
        self.total_data_label.setText(str(len(self.item_id)))

        # 更新Result Table标题
        title = 'Cat.%s-Keyword.%s-Order.%s' % (cat_name, keyword, order_name)
        self.result_title_label.setText(title)

        # 自动保存
        if self.auto_save_checkbox.isChecked():
            self.save_data('auto')

    def update_ui(self, t):
        if t == 'init':
            self.search_button.setText('搜  索')
            self.search_button.setStyleSheet('background-color: rgb(65, 113, 156);')
            self.clear_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.auto_save_checkbox.setEnabled(True)
            self.search_button.setEnabled(True)
        elif t == 'running':
            self.search_button.setText('正在运行')
            self.search_button.setStyleSheet("background-color: rgb(204, 0, 0)")
            self.clear_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.auto_save_checkbox.setEnabled(False)
            self.search_button.setEnabled(False)
        elif t == 'stopped':
            self.search_button.setText('搜  索')
            self.search_button.setStyleSheet('background-color: rgb(65, 113, 156);')
            self.clear_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.auto_save_checkbox.setEnabled(True)
            self.search_button.setEnabled(True)

    def get_location(self):
        if self.international_checkbox.isChecked():
            if self.local_checkbox.isChecked():
                return LOCATION_MAP['Both']
            else:
                return LOCATION_MAP[self.international_checkbox.text()]
        else:
            if self.local_checkbox.isChecked():
                return LOCATION_MAP[self.local_checkbox.text()]
            else:
                return ''

    def clear_table(self):
        self.result_table.setRowCount(0)
        self.result_table.clearContents()
        self.clear_button.setEnabled(False)

        self.item_page = []
        self.item_id = []
        self.shop_id = []
        self.save_button.setEnabled(False)

        self.total_page_label.setText('0')
        self.total_data_label.setText('0')

        self.result_title_label.setText('结  果')

    def save_data(self, t):
        cat_name = self.category_box.currentText()
        order = self.sort_box.currentText()
        keyword = self.keyword_edit.text()
        page = self.page_box.text()
        filename = 'Cat.%s-Keyword.%s-Order.%s-Page.%s' % (cat_name, keyword, order, page)
        data = pd.DataFrame(
            {
                'Page': self.item_page,
                'Item ID': self.item_id,
                'Shop ID': self.shop_id
            }
        )
        if t == 'user':
            save_path, t = QFileDialog.getSaveFileName(self, '保存为文件', './' + filename, 'csv(*.csv)')
            if len(save_path) == 0:
                return
        elif t == 'auto':
            here = os.getcwd()
            save_path = os.path.join(here, filename + '.csv')

        data.to_csv(save_path)
        self.message_label.setText('已保存为 ' + save_path)

    def open_window(self, w):
        if w == 'about':
            win = About(self)
            win.exec_()

    def switch_filter(self):
        if self.filter_box.currentText() != 'Precio':
            self.sort_box.setEnabled(False)
            self.order_label.setEnabled(False)
            self.sort_box.setCurrentText('Descending')
        else:
            self.sort_box.setEnabled(True)
            self.order_label.setEnabled(True)
            self.sort_box.setCurrentText('Ascending')

    def switch_window_mode(self, m):
        self.actionMaximize.setChecked(False)
        self.actionMinimize.setChecked(False)
        self.actionNormal.setChecked(False)
        self.actionFullScreen.setChecked(False)
        if m == 'max':
            self.actionMaximize.setChecked(True)
            self.showMaximized()
        if m == 'min':
            self.actionMinimize.setChecked(True)
            self.showMinimized()
        if m == 'normal':
            self.actionNormal.setChecked(True)
            self.showNormal()
        if m == 'full':
            if self.isFullScreen():
                self.showNormal()
                self.actionFullScreen.setChecked(False)
            else:
                self.actionFullScreen.setChecked(True)
                self.showFullScreen()

    def reset_ui(self):
        # self.category_box.setCurrentText('Deportes y Fitness')
        # self.keyword_edit.setText('')
        # self.page_box.setValue(1)
        # self.filter_box.setCurrentText('Precio')
        # self.sort_box.setCurrentText('Ascending')
        # self.international_checkbox.setChecked(True)
        # self.local_checkbox.setChecked(False)
        # self.auto_save_checkbox.setChecked(False)
        self._ui_init_()
        self.update_ui('init')

    def resizeEvent(self, event):
        super(Main, self).resizeEvent(event)
        print(self.result_table.size())

    def closeEvent(self, event):
        try:
            res = QMessageBox.question(self, 'Exit', 'Do you want to exit?', QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.Yes)
            if res == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print('[Close] Close error:', str(e))
            event.accept()

    ############# 以图搜图相关功能 #############
    def get_image(self, image_url, retry_num=5):
        count = 0
        while True:
            try:
                res = requests.get(image_url)
                image = Image.open(BytesIO(res.content))
                image = np.asarray(image)
            except Exception as e:
                if count < retry_num:
                    count += 1
                    continue
                else:
                    return False, str(e)
            else:
                return True, image

    def image_search_click(self):
        self.imagetab_clear_table()
        # 获取图片链接
        image_url = self.link_edit.text()
        if len(image_url) == 0:
            QMessageBox.warning(self, 'Warning', '请输入图片链接！')
            self.link_edit.setFocus()
            return

        if not image_url.startswith('http'):
            image_url = IMAGE_BASE_URL + image_url
        print(image_url)

        # 获取目标图片并显示
        print('Start request target image...')
        flag, target_image = self.get_image(image_url)
        if not flag:
            QMessageBox.warning(self, 'Error', '获取目标图片出错\n' + target_image)
            print('Get target image failed')
            return
        show_image = QImage(target_image, target_image.shape[1], target_image.shape[0], QImage.Format_RGB888)
        self.image_label.set_image(show_image)

        # 获取当前Category id和page
        cat_name = self.imagetab_category_box.currentText()
        cat_id = CATEGORY_ID_MAP[cat_name]
        # print(cat_id)
        page = int(self.imagetab_page_box.text())
        crawl_params = {
            'by': 'relevancy',
            'limit': 60,
            'match_id': cat_id,
            'newest': 0,
            'order': 'desc',
            'page_type': 'search',
            'scenario': 'PAGE_CATEGORY',
            'version': 2
        }

        # 按页爬取item信息
        print('Starting request item information...')
        res = []
        for i in range(page):
            start_index = i * 60
            crawl_params['newest'] = start_index
            print('Page % d | ' % (i + 1), end='')
            print(crawl_params)
            try:
                response = requests.get(BASE_URL, params=crawl_params).json()
                item_info = response['items']
                print('Number of data:', len(item_info))
                if len(item_info) == 0:
                    if i == 0:
                        QMessageBox.warning(self, 'Warning', '未查询到对应信息！')
                        return
                    else:
                        break
            except Exception as e:
                print('Error', str(e))
                QMessageBox.warning(self, 'Warning', 'Crawler failed\n' + str(e))
                return
            else:
                for item in item_info:
                    res.append({
                        'page': i + 1,
                        'item_id': item['itemid'],
                        'shop_id': item['shopid'],
                        'image_id': item['item_basic']['image']
                    })
        print('Total number of items:', len(res))

        # 逐个获取图片计算ssim相似度
        print('Starting get images...')
        target_height, target_width, _ = target_image.shape
        print('Target image shape:', target_height, target_width, _)
        for i, item in enumerate(res):
            print('%d | ' % i, end='')

            # TODO: 失败重试
            flag, item_image = self.get_image(IMAGE_BASE_URL + item['image_id'])
            if not flag:
                res[i]['score'] = 0
                print('failed', item_image)
                continue
            print('succeed | ', end='')
            item_image_resized = cv2.resize(item_image, (target_height, target_width))
            score, diff = SSIM(target_image, item_image_resized, full=True, multichannel=True)
            res[i]['score'] = score
            # res[i]['image'] = item_image
            print(score)

        # 添加到结果表格中
        # 按分数排序
        self.imagetab_result = sorted(res, key=lambda x: x['score'], reverse=True)
        for item in self.imagetab_result:
            row_count = self.imagetab_result_table.rowCount()
            self.imagetab_result_table.insertRow(row_count)
            item_page = QTableWidgetItem(str(item['page']))
            item_id = QTableWidgetItem(str(item['item_id']))
            shop_id = QTableWidgetItem(str(item['shop_id']))

            # TODO: 对获取图片失败的item的处理
            # res_image = item['image']
            # res_image_qimage = QImage(res_image, res_image.shape[1], res_image.shape[0], QImage.Format_RGB888)
            # res_image_qpixmap = QPixmap.fromImage(res_image_qimage)
            # qicon = QIcon()
            # qicon.addPixmap(res_image_qpixmap)
            # score = QTableWidgetItem(qicon, str(round(item['score'], 2)))
            score = QTableWidgetItem(str(round(item['score'], 2) * 100) + '%')
            self.imagetab_result_table.setItem(row_count, 0, item_page)
            self.imagetab_result_table.setItem(row_count, 1, item_id)
            self.imagetab_result_table.setItem(row_count, 2, shop_id)
            self.imagetab_result_table.setItem(row_count, 3, score)

        # 自动保存
        if self.imagetab_auto_save_checkbox.isChecked():
            self.imagetab_save_data('auto')

    def imagetab_save_data(self, t):
        cat_name = self.imagetab_category_box.currentText()
        page = self.imagetab_page_box.text()
        filename = 'ImageSearch-Cat.%s-Page.%s' % (cat_name, page)
        item_page = []
        item_id = []
        shop_id = []
        item_score = []
        for item in self.imagetab_result:
            item_page.append(item['page'])
            item_id.append(item['item_id'])
            shop_id.append(item['shop_id'])
            item_score.append(str(round(item['score'], 2) * 100) + '%')

        data = pd.DataFrame(
            {
                'Page': item_page,
                'Item ID': item_id,
                'Shop ID': shop_id,
                'Score': item_score
            }
        )

        if t == 'user':
            save_path, t = QFileDialog.getSaveFileName(self, '保存为文件', './' + filename, 'csv(*.csv)')
            if len(save_path) == 0:
                return
        elif t == 'auto':
            here = os.getcwd()
            save_path = os.path.join(here, filename + '.csv')

        data.to_csv(save_path)
        self.message_label.setText('已保存为 ' + save_path)

    def imagetab_clear_table(self):
        self.imagetab_result_table.setRowCount(0)
        self.imagetab_result_table.clearContents()

    ##################### Title Tab #####################
    def get_title(self, url, params, retry_num=5):
        count = 0
        print('Request URL: %s' % url)
        print('Request params:', params)
        while True:
            try:
                res = requests.get(url, params=params).json()
                title = res['data']['name']
            except Exception as e:
                print('#%d 接口请求失败: %s', (count, str(e)))
                if count < retry_num:
                    count += 1
                    continue
                else:
                    return False, str(e)
            else:
                print('#%d 接口请求成功' % count)
                return True, title

    def titletab_clear_table(self):
        self.titletab_result_table.setRowCount(0)
        self.titletab_result_table.clearContents()

    def title_start(self):
        self.titletab_clear_table()
        request_url = 'https://shopee.com.%s/api/v4/item/get'
        request_params = {
            'itemid': 0,
            'shopid': 0
        }
        text = self.titletab_url_edit.toPlainText().strip()
        url_list = text.split('\n')
        item_urls = []
        item_titles = []
        fail_count = 0
        for i, url in enumerate(url_list):
            url = url.strip()
            print('%d | %s' % (i, url))
            if url == '\n' or len(url) == 0:
                continue

            item_urls.append(url)

            # 识别是否是合法链接
            if not (url.startswith('https://shopee.com.') or url.startswith('http://shopee.com')):
                print('第%d行存在非法链接:\n%s' % (i + 1, url))
                # QMessageBox.warning(self, 'Error', '第%d行存在非法链接:\n%s' % (i + 1, url))
                item_titles.append('非法链接')
                fail_count += 1
                continue

            # 获取地区代码填入请求链接中 + 获取去除头部的链接
            if url.startswith('https://'):
                region_code = url[19:21]
                target = url[22:]
            elif url.startswith('http://'):
                region_code = url[18:20]
                target = url[21:]
            # print(region_code)
            cur_request_url = request_url % region_code

            # url pattern识别，获取itemid和shopid
            # 第一种模式 https://shopee.com.mx/product/739950477/11596520940
            if target.startswith('product/'):
                temp = target.split('/')
                shop_id = temp[1]
                item_id = temp[2]
                print('Shop ID %s | Item ID %s' % (shop_id, item_id))
            elif '-i.' in target and '?sp_atk=' in target:
                start_index = target.index('-i.') + 3
                end_index = target.index('?sp_atk=')
                temp = target[start_index:end_index].split('.')
                shop_id = temp[0]
                item_id = temp[1]
                print('Shop ID %s | Item ID %s' % (shop_id, item_id))
            elif '-i.' in target:
                start_index = target.index('-i.') + 3
                temp = target[start_index:].split('.')
                shop_id = temp[0]
                item_id = temp[1]
                print('Shop ID %s | Item ID %s' % (shop_id, item_id))
            else:
                print('未识别的链接模式:\n%s' % url)
                # QMessageBox.warning(self, 'Error', '未识别的链接模式:\n%s' % url)
                item_titles.append('未识别的链接模式')
                fail_count += 1
                continue

            # 判断取到的itemid shopid是否合法
            if not (shop_id.isdigit() and item_id.isdigit()):
                # QMessageBox.warning(self, 'Error', '链接识别失败:\n%s' % url)
                item_titles.append('链接识别失败')
                fail_count += 1
                continue

            # 构建请求参数
            request_params['itemid'] = item_id
            request_params['shopid'] = shop_id

            # 获取信息
            flag, title = self.get_title(cur_request_url, request_params)
            if not flag:
                # QMessageBox.warning(self, 'Error', '信息获取失败:\n%s' % title)
                item_titles.append('信息获取失败')
                fail_count += 1
                continue
            else:
                item_titles.append(title)

        self.titletab_item_titles = item_titles

        # 添加结果到表格
        for i in range(len(item_urls)):
            row_count = self.titletab_result_table.rowCount()
            self.titletab_result_table.insertRow(row_count)
            item_url = QTableWidgetItem(item_urls[i])
            item_title = QTableWidgetItem(item_titles[i])
            self.titletab_result_table.setItem(row_count, 0, item_url)
            self.titletab_result_table.setItem(row_count, 1, item_title)

        self.message_label.setText('Title检索完成, 成功%d/%d' % (len(item_titles) - fail_count, len(item_titles)))

        if self.titletab_autocopy_checkbox.isChecked():
            self.copy_titles()

    def copy_titles(self):
        res = '\n'.join(self.titletab_item_titles)
        pyperclip.copy(res)
        self.message_label.setText('结果已复制到粘贴板')












