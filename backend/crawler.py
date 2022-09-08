import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        # self.base_url = target
        pass

    def get_html_text(self, target):
        res = requests.get(target)
        res.raise_for_status()
        return res.text

    def find(self, html):
        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all(name='div', attrs={'class': 'shopee-search-item-result__item'})
        print(len(items))
        # for item in items:


if __name__ == '__main__':
    crawler = Crawler()
    test_url = 'https://shopee.com.co/search?category=11069113&keyword=iphone&locations=Internacional&noCorrection=true&order=asc&page=0&sortBy=price'
    text = crawler.get_html_text(test_url)
    with open('./test_html.html', 'w') as f:
        f.write(text)
    # print(text)
    # crawler.find(text)
