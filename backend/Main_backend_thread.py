import requests
import pandas as pd

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, \
    QMessageBox, QTableWidgetItem, QLineEdit, QProgressBar, QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from frontend import MainWindow
from backend import About, Crawler
from images import get_img_path
from config.config import __APPNAME__, __VERSION__,\
    CATEGORY_ID_MAP, SORT_MAP, BASE_URL, CRAWL_PARAMS, LOCATION_MAP


class Main(QMainWindow, MainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.craw_params = CRAWL_PARAMS.copy()
        self.item_page = []
        self.item_id = []
        self.shop_id = []
        self.total_page = 0
        self.data_number = 0

        self._ui_init_()

        # 初始化爬虫线程
        self.crawler = Crawler(BASE_URL)
        self.crawler.data.connect(self.update_vis)

    def _ui_init_(self):
        self.setupUi(self)

        self.setWindowTitle(__APPNAME__ + ' v' + __VERSION__)

        # 禁用当前未完成功能
        self.actionReset.setEnabled(False)
        self.actionSetting.setEnabled(False)
        self.actionReleaseNotes.setEnabled(False)

        # 初始化界面
        self.clear_button.setEnabled(False)
        self.save_button.setEnabled(False)
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
        # 设置显示的选项
        self.category_box.setCurrentText('Deportes y Fitness')
        # 显示居中
        temp = QLineEdit()
        temp.setReadOnly(True)
        temp.setAlignment(Qt.AlignCenter)
        self.category_box.setLineEdit(temp)
        # 添加排序选项
        for t in SORT_MAP.keys():
            self.sort_box.addItem(t)
        # 设置显示的选项
        self.sort_box.setCurrentText('升序')
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
        # self.search_button.clicked.connect(self.search)
        self.search_button.clicked.connect(self.click_search)
        self.clear_button.clicked.connect(self.clear_table)
        self.save_button.clicked.connect(self.save_data)
        self.actionAbout.triggered.connect(lambda: self.open_window('about'))
        self.actionMaximize.triggered.connect(lambda: self.switch_window_mode('max'))
        self.actionMinimize.triggered.connect(lambda: self.switch_window_mode('min'))
        self.actionNormal.triggered.connect(lambda: self.switch_window_mode('normal'))
        self.actionFullScreen.triggered.connect(lambda: self.switch_window_mode('full'))
        self.actionExit.triggered.connect(self.close)

    def click_search(self):
        # 如果当前正在搜索
        if self.crawler.is_running:
            self.crawler.is_running = False
            self.message_label.setText('搜索被终止')
            self.update_status('stopped')

        # 如果当前未在搜索
        else:
            self.data_number = 0
            self.crawler.is_running = True

            # 获取当前参数
            cat_name = self.category_box.currentText()
            cat_id = CATEGORY_ID_MAP[cat_name]
            order = SORT_MAP[self.sort_box.currentText()]
            keyword = self.keyword_edit.text()
            self.total_page = int(self.page_box.text())
            location = self.get_location()

            # 构造请求参数
            self.craw_params['keyword'] = keyword
            self.craw_params['limit'] = 60
            self.craw_params['match_id'] = cat_id
            self.craw_params['order'] = order
            self.craw_params['locations'] = location

            # 初始化界面
            # 统计数据
            self.total_page_label.setText('0')
            self.total_data_label.setText('0')
            # 清空当前表格
            self.clear_table()
            # 初始化progress bar
            self.progress_bar.show()
            self.progress_bar.setRange(0, self.total_page)
            # 更新界面状态
            self.update_status('running')

            # 后台开始爬取
            self.crawler.search(self.craw_params, self.total_page)

    def update_vis(self, data, flag, msg):
        """
        更新表格与界面
        :param data: (cur_page, item_id, shop_id)
        :param flag:
        :param msg:
        :return:
        """
        if not self.crawler.is_running:
            return

        if not flag:
            QMessageBox.warning(self, 'Warning', 'Crawler failed\n' + msg)
            self.progress_bar.setValue(0)
            self.progress_bar.hide()
            self.message_label.setText('搜索异常结束')
            # 更新界面状态
            self.update_status('stopped')
            return
        cur_page, item_ids, shop_ids = data
        if len(item_ids) == 0:
            if cur_page == 1:
                QMessageBox.warning(self, 'Warning', '未搜索到任何信息，请重试!')
                self.progress_bar.setValue(0)
                self.progress_bar.hide()
                self.message_label.setText('搜索结束, 无有效数据')
            else:
                self.progress_bar.setValue(0)
                self.progress_bar.hide()
                self.message_label.setText('当前页面无有效数据，搜索结束')

            # 更新界面状态
            self.update_status('stopped')
            return
        else:
            if cur_page == self.total_page:
                self.message_label.setText('搜索完成')

                # 更新界面状态
                self.update_status('stopped')
            else:
                self.message_label.setText('正在搜索第%d页...' % (cur_page + 1))
            self.progress_bar.setValue(cur_page)

        # 添加数据到表格中
        # for i in range(len(item_ids)):
        #     row_count = self.result_table.rowCount()
        #     self.result_table.insertRow(row_count)
        #     item_page = QTableWidgetItem(str(cur_page))
        #     item_id = QTableWidgetItem(str(item_ids[i]))
        #     shop_id = QTableWidgetItem(str(shop_ids[i]))
        #     self.result_table.setItem(row_count, 0, item_page)
        #     self.result_table.setItem(row_count, 1, item_id)
        #     self.result_table.setItem(row_count, 2, shop_id)

        # 设置总页数与数据条数
        # self.total_page_label.setText(str(cur_page))
        # self.data_number += len(item_ids)
        # self.total_data_label.setText(str(self.data_number))

    def update_status(self, t):
        if t == 'running':
            self.search_button.setText('停   止')
            self.search_button.setStyleSheet("background-color: rgb(204, 0, 0)") # 清空 保存按钮
            self.clear_button.setEnabled(False)
            self.save_button.setEnabled(False)
            self.auto_save_checkbox.setEnabled(False)
            self.crawler.is_running = True
        elif t == 'stopped':
            self.search_button.setText('搜   索')
            self.search_button.setStyleSheet('background-color: rgb(65, 113, 156);')
            self.clear_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.auto_save_checkbox.setEnabled(True)
            self.crawler.is_running = False

    def search(self):
        # 清空当前表格
        self.clear_table()

        cat_name = self.category_box.currentText()
        cat_id = CATEGORY_ID_MAP[cat_name]
        # print('Cat id: %d, Cat name: %s' % (cat_id, cat_name))
        order = SORT_MAP[self.sort_box.currentText()]
        # print('Sort Type:', order)
        keyword = self.keyword_edit.text()
        # print('Keyword:', keyword)
        page = int(self.page_box.text())
        # print('Page:', page)
        # print(type(page))
        location = self.get_location()

        # 初始化progress bar
        self.progress_bar.show()
        self.progress_bar.setRange(0, page)

        # 获取请求参数
        self.craw_params['keyword'] = keyword
        self.craw_params['limit'] = 60
        self.craw_params['match_id'] = cat_id
        self.craw_params['order'] = order
        self.craw_params['locations'] = location

        # 请求
        res = []
        for i in range(page):
            # 更新status bar
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
                return
            else:
                for item in item_info:
                    # res.append({
                    #     'item_page': str(i + 1),
                    #     'item_id': str(item['itemid']),
                    #     'shop_id': str(item['shopid'])
                    # })
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
            # item_page = QTableWidgetItem(item['item_page'])
            # item_id = QTableWidgetItem(item['item_id'])
            # shop_id = QTableWidgetItem(item['shop_id'])
            item_page = QTableWidgetItem(str(self.item_page[i]))
            item_id = QTableWidgetItem(str(self.item_id[i]))
            shop_id = QTableWidgetItem(str(self.shop_id[i]))
            self.result_table.setItem(row_count, 0, item_page)
            self.result_table.setItem(row_count, 1, item_id)
            self.result_table.setItem(row_count, 2, shop_id)

        self.clear_button.setEnabled(True)
        self.save_button.setEnabled(True)

        # 搜索完成
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.message_label.setText('搜索完成')

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

    def save_data(self):
        cat_name = self.category_box.currentText()
        order = self.sort_box.currentText()
        keyword = self.keyword_edit.text()
        page = self.page_box.text()
        filename = 'Category_%s-Keyword_%s-Order_%s-Page_%s' % (cat_name, keyword, order, page)
        save_path, t = QFileDialog.getSaveFileName(self, '保存为文件', './' + filename, 'csv(*.csv)')
        if len(save_path) == 0:
            return
        data = pd.DataFrame(
            {
                'Page': self.item_page,
                'Item ID': self.item_id,
                'Shop ID': self.shop_id
            }
        )
        data.to_csv(save_path)

    def open_window(self, w):
        if w == 'about':
            win = About(self)
            win.exec_()

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
