import requests
from PyQt5.QtCore import pyqtSignal, QThread


class Crawler(QThread):
    # list:   爬取的数据 (cur_page, item_ids, shop_ids)
    # bool:   爬取是否成功
    # str:    错误信息
    data = pyqtSignal(tuple, bool, str)

    def __init__(self, base_url):
        super(Crawler, self).__init__()
        self.base_url = base_url
        self.is_running = False

    def search(self, params, page):
        self.is_running = True
        for i in range(page):
            if not self.is_running:
                return
            item_id = []
            shop_id = []
            start_index = i * 60
            params['newest'] = start_index
            try:
                response = requests.get(self.base_url, params=params).json()
                item_info = response['items']
                print('Page %d | Number of Data: %d' % (i, len(item_info)))
                if len(item_info) == 0:
                    self.data.emit((i + 1, [], []), True, '未查询到数据')
                    return
                    # if i == 0:
                    #     self.data.emit((), False, '未查询到数据')
                    #     return
                    # else:
                    #     self.data.emit((), True, '未查询到数据')
            except Exception as e:
                print('Error')
                print(str(e))
                self.data.emit((i + 1, [], []), False, str(e))
                return
            else:
                for item in item_info:
                    item_id.append(item['itemid'])
                    shop_id.append(item['shopid'])
                self.data.emit((i + 1, item_id, shop_id), True, 'Success')

    def stop(self):
        self.is_running = False


