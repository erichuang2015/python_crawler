#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/3/18 15:40
# @Author : Tom_tao
# @Site : 
# @File : demo8.py
# @Software: PyCharm

import os
import re
import threading
from queue import Queue
from urllib import request

import requests
from lxml import etree


class Procude(threading.Thread):
    headers = {
        'Cookie': '__cfduid=d47dc4792639872b4ea3d70b71fb72f911584374974; _ga=GA1.2.719626918.1584374976; UM_distinctid=170e41b8eb128-0959c2fa1789f8-4313f6a-1fa400-170e41b8eb21da; _agep=1584374980; _agfp=f8c4f380e36d9737d95609408cc68a2f; _agtk=4d2296932f4bd09594912a158be3f813; _gid=GA1.2.1973474054.1584504686; __gads=ID=6e1da9ac44340e2c:T=1584504685:S=ALNI_Mbe8KbTUgtMAjvE7UCom8xvSnM34Q; CNZZDATA1256911977=1137117854-1584369797-%7C1584505087',
        'Referer': 'http://www.doutula.com/photo/list/?page=2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Procude, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_page(url)

    def parse_page(self, url):
        response = requests.get(url, headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        imgs = html.xpath("//div[@class='page-content text-center']//img[@class!='gif']")
        for img in imgs:
            img_url = img.get('data-original')
            alt = img.get('alt')
            alt = re.sub(r'[\?？\.、.!！，,\*]', '', alt)
            suffix1 = os.path.splitext(img_url)[1]
            suffix = suffix1[0:4]
            file_name = alt + suffix
            self.img_queue.put((img_url, file_name))


class Consumer(threading.Thread):
    def __init__(self, page_queue, img_queue, *args, **kwargs):
        super(Consumer, self).__init__(*args, **kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break

            img_url, file_name = self.img_queue.get()  # 元组解包
            request.urlretrieve(img_url, 'images/' + file_name)
            print(file_name + "下载完成")


def main():
    page_queue = Queue(100)
    img_queue = Queue(1000)
    for x in range(1, 101):
        url = "http://www.doutula.com/photo/list/?page=%d" % x
        page_queue.put(url)
        # time.sleep(1)

    for x in range(5):
        t = Procude(page_queue, img_queue)
        t.start()

    for x in range(5):
        t = Consumer(page_queue, img_queue)
        t.start()


if __name__ == '__main__':
    main()
