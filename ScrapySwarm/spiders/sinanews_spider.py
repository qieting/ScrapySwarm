#!/usr/bin/python3
'''
@File : sinanews_spider.py

@Time : 2019/6/25

@Author : Boholder

@Function : 【借助百度搜索】，爬取最新布局的新浪新闻 exm:
            https://news.sina.com.cn/c/2019-06-24/doc-ihytcitk7355640.shtml

            感谢新浪前端开发者，
            即使url因新闻分类各不相同，布局还是统一的，省大事了。

            为什么要借助百度，因为新浪内置的新浪搜索不能完美地执行
            "选定关键字全包含" 参数，即使它确实在高级搜索确实定义了。
            当然，也省得再写个爬虫了。
'''

import scrapy
import re

from ScrapySwarm.tools.bdsearch_url_util \
    import BDsearchUrlUtil

from ScrapySwarm.items import SinaNewsItem

from ScrapySwarm.tools.crawl_time_format \
    import getCurrentTime, formatTimeStr


class SinaNewsSpider(scrapy.Spider):
    name = 'sinanews'
    keyword = ''
    site = 'news.sina.com.cn'
    bd = BDsearchUrlUtil()

    def close(self, reason):
        # 当爬虫停止时，调用clockoff()修改数据库
        if self.bd.clockoff(self.site, self.keyword):
            print('SinaNews_spider clock off successful')

        # 重载前scrapy原来的代码
        closed = getattr(self, 'closed', None)
        if callable(closed):
            return closed(reason)

    def start_requests(self):
        # get params (from console command) when be started
        self.keyword = getattr(self, 'q', None)

        if self.keyword is None:
            self.keyword = '中美贸易'

        # get url list for mongoDB
        urllist = self.bd.getNewUrl(self.site, self.keyword)

        # if no new url or error, urllist=None
        if urllist:
            for url in urllist:
                yield scrapy.Request(url, self.parse)

        # # test spider
        # url = 'http://news.sina.com.cn/c/2019-06-24' \
        #       '/doc-ihytcitk7355640.shtml'
        # yield scrapy.Request(url, self.parse)

    def parse(self, response):
        item = SinaNewsItem()

        item['url'] = response.url
        item['crawl_time'] = getCurrentTime()
        item['keyword'] = self.keyword

        item['title'] = response.xpath(
            '//h1[@class=\'main-title\']/text()').get()

        time = response.xpath(
            '//div[@class=\'date-source\']'
            '/span[@class=\'date\']/text()').get()
        item['time'] = formatTimeStr(time)

        item['source'] = response.xpath(
            '//div[@class=\'date-source\']'
            '/a[@class=\'source\']/text()').get()

        # 正文抽取
        content = ''

        # /a/ /c/ doc-... /o/
        if response.xpath(
                '//div[@id=\'article\']//p/text()'):

            for paragraph in response.xpath(
                    '//div[@id=\'article\']//p/text()'):
                paragraph = paragraph.get().strip()
                paragraph = re.sub(r'<[^i].*?>', '', paragraph)
                paragraph = re.sub(r'\(function[\s\S]+?\}\)\(\);', '', paragraph)
                content = content + paragraph

        # some of /o/
        # http://news.sina.com.cn/o/2019-05-14/doc-ihvhiews1782968.shtml
        elif response.xpath(
                '//div[@id=\'article\']//p/text()'):

            for paragraph in response.xpath(
                    '//div[@id=\'article\']//div/text()'):
                paragraph = paragraph.get().strip()
                paragraph = re.sub(r'<[^i].*?>', '', paragraph)
                paragraph = re.sub(r'\(function[\s\S]+?\}\)\(\);', '', paragraph)
                content = content + paragraph

        item['content'] = content

        yield item