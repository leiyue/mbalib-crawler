# -*- coding: utf-8 -*-
# @Author: leiyue
# @Date:   17/06/15
# @Last modified by:   leiyue
# @Last Modified time: 17/06/15

import requests
from bs4 import BeautifulSoup
from html2text import html2text
import csv


class MBALIB:
    def __init__(self, baseUrl, wikiUrl=None, limit=None, page_numbers=None):
        self.accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        self.headers = {'Accept': self.accept, 'User-Agent': self.user_agent}
        self.baseUrl = baseUrl
        self.wikiUrl = wikiUrl or "http://wiki.mbalib.com"
        self.limit = limit or 100
        self.page_numbers = page_numbers or 5
        self.items = []
        self.order = 0

    def get_page(self, url):
        return requests.get(url, headers=self.headers).content

    def get_item(self, page):
        soup = BeautifulSoup(page, "lxml")
        ol = soup.find("ol", "special")
        for li in ol.find_all("li"):
            self.order += 1
            name, recommend = li.text.replace("\u200e", "").replace("人推荐)", "").replace(",", "").split(" (")
            item = {'order': self.order, 'name': name, 'recommend': int(recommend), 'link': self.wikiUrl + li.a['href']}
            self.items.append(item)

    def get_item_content(self, item):
        html = self.get_page(item['link'])
        soup = BeautifulSoup(html, "lxml")
        content = soup.find("div", {"id": "bodyContent"})
        filename = item['name'] + ".md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html2text(content.prettify()))

    def start(self):
        for offset in (x * self.limit for x in range(self.page_numbers)):
            url = self.baseUrl % (self.limit, offset)
            page = self.get_page(url)
            self.get_item(page)
            print("Getting items from page: %s" % url)
        with open("entries.csv", "w", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["order", "name", "recommend", "link"])
            for item in self.items:
                writer.writerow([item['order'], item['name'], item['recommend'], item['link']])
                self.get_item_content(item)
        print("Items saved.")


if __name__ == '__main__':
    baseUrl = "http://wiki.mbalib.com/w/index.php?title=Special:Mostrecommends&limit=%s&offset=%s"
    wikiUrl = "http://wiki.mbalib.com"
    crawler = MBALIB(baseUrl, wikiUrl, 20, 1)
    crawler.start()
