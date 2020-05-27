#!/usr/local/bin/python3
# -*- coding: UTF-8 –*-
'''
@Author: Leuan
@Date: 2020-05-27 06:23:11
@LastEditors: Leuan
@LastEditTime: 2020-05-27 20:50:29
@message: 
'''
import requests
import threading
from lxml import etree
from queue import Queue
from unipath import Path
import logging
import time
import os
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')  # 配置日志


class SpiderWP():
    def __init__(self):
        self.num = 10  # 爬取图片的张数
        self.queue = Queue()  # 队列
        self.BASE_URL = "http://www.netbian.com/"  # 网址
        self.sort = {}  # 分类对应的链接
        self.file_path = Path(Path(__file__).parent, '壁纸')  # 创建的壁纸路径
        self.sort_flag = ''  # 分类标记

     # 请求并返回Element
    def req(self, _url): 
        rs = requests.get(_url).content.decode("gbk")
        html = etree.HTML(rs)
        return html

      # 获取分类
    def get_sort(self):
        html = self.req(self.BASE_URL)
        tags = html.xpath("//div[@class='nav cate']/a")
        for tag in tags:
            self.sort[tag.text] = self.BASE_URL + tag.get("href")

    # 递归生成图片的入口链接
    def get_page(self, _url):  
        while True:
            html = self.req(_url)
            tags = html.xpath("//div[@class='wrap clearfix']//li/a")
            for tag in tags:
                self.get_jpg(self.BASE_URL + tag.get('href'))
            try:
                next_link = self.BASE_URL + \
                    html.xpath("//a[text()='下一页>']/@href")[0]
            except IndexError:
                logging.warning('图片已全部下载')
                self.num = 0
            if self.num != 0:
                self.get_page(next_link)
            else:
                break
    
    # 获取图片链接添加队列
    def get_jpg(self, _url):
        if self.num != 0:
            html = self.req(_url)
            try:
                title = html.xpath("//div[@class='action']//h1/text()")[0]
                link = html.xpath("//div[@class='pic']//p//a//img/@src")[0]
                self.queue.put((title, link))
                self.num -= 1
            except IndexError:
                logging.warning("图片解析失败，跳过...")

    # 下载图片
    def download(self):
        while True:
            if not self.queue.empty():
                title, link = self.queue.get()

                # 下载图片间隔时间,不建议太低给服务器造成压力(多线程下载的已经很快了)
                time.sleep(2)
                jpg = requests.get(link).content
                title = title + '.' + link.split(".")[-1]
                jpg_path = Path(self.jpg_path, title)

                # 如果本地已经存在同名文件,随机改名
                if jpg_path.exists():
                    jpg_path = Path(self.jpg_path, title.split('.')[0] + str(random.randint(1, 100)) + '.' + link.split(".")[-1])
                logging.info('下载:%s', title)
                with open(jpg_path, 'wb') as f:
                    f.write(jpg)
            # 如果队列为空,则结束程序
            if self.num == 0 and self.queue.empty():
                logging.info('下载完成')
                break

    def mean(self):
        print('''4k壁纸 日历   动漫   风景   美女   游戏   影视   动态   唯美   设计
可爱   汽车   花卉   动物   节日   人物   美食   水果   建筑   体育
军事   非主流 其他   护眼    LOL  王者荣耀 
-------------------------请输入分类名称-------------------------''')
        while True:
            inp = input("==>")
            if inp in self.sort:
                # 根据输入分类在‘壁纸’文件夹下创建子文件夹
                self.jpg_path = Path(self.file_path, inp) 
                if not self.jpg_path.exists():
                    os.makedirs(self.jpg_path)

                self.sort_flag = inp
                # 
                while True:
                    try:
                        self.num = int(
                            input('-------------------------请输入下载张数-------------------------\n==>'))
                        break
                    except ValueError:
                        print('请输入数字')
                break
            else:
                print('输入有误,请重新输入')

    def run(self):
        self.get_sort()
        self.mean()
        r = threading.Thread(target=self.get_page, args=((self.sort[self.sort_flag],)))
        r.start()

        # 多进程开启,不建议调高
        for i in range(8):
            t = threading.Thread(target=self.download)
            t.start()


a = SpiderWP()
a.run()
