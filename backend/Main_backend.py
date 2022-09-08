import os
import requests
import pandas as pd

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, \
    QMessageBox, QTableWidgetItem, QLineEdit, QProgressBar, QLabel, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from frontend import MainWindow
from backend import About
from images import get_img_path
from config.config import __APPNAME__, __VERSION__,\
    CATEGORY_ID_MAP, SORT_MAP, BASE_URL, CRAWL_PARAMS, LOCATION_MAP, FILTER_MAP


class Main(QMainWindow, MainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.craw_params = CRAWL_PARAMS.copy()
        self.item_page = []
        self.item_id = []
        self.shop_id = []

        self._ui_init_()

    def _ui_init_(self):
        self.setupUi(self)

        self.setWindowTitle(__APPNAME__ + ' v' + __VERSION__)

        # 禁用当前未完成功能
        # self.actionReset.setEnabled(False)
        self.actionSetting.setEnabled(False)
        self.actionReleaseNotes.setEnabled(False)

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
        # 设置显示的选项
        self.category_box.setCurrentText('Deportes y Fitness')
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
        self.search_button.clicked.connect(self.search)
        self.clear_button.clicked.connect(self.clear_table)
        self.save_button.clicked.connect(lambda: self.save_data('user'))
        self.filter_box.currentTextChanged.connect(self.switch_filter)
        self.actionReset.triggered.connect(self.reset_ui)
        self.actionAbout.triggered.connect(lambda: self.open_window('about'))
        self.actionMaximize.triggered.connect(lambda: self.switch_window_mode('max'))
        self.actionMinimize.triggered.connect(lambda: self.switch_window_mode('min'))
        self.actionNormal.triggered.connect(lambda: self.switch_window_mode('normal'))
        self.actionFullScreen.triggered.connect(lambda: self.switch_window_mode('full'))
        self.actionExit.triggered.connect(self.close)

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
