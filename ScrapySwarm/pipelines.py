# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from pymongo.errors import DuplicateKeyError
import ScrapySwarm.items as items
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient \
            (settings['LOCAL_MONGO_HOST'], settings['LOCAL_MONGO_PORT'])
        db = connection[settings['MONGO_DB_NAME']]

        self.bdsearch = db[settings['COLL_BAIDU_SREACH']]
        self.Information = db[settings['COLL_WEIBO_INFOMATION']]
        self.Tweets = db[settings['COLL_WEIBO_TWEETS']]
        self.Comments = db[settings['COLL_WEIBO_COMMENTS']]
        self.Relationships = db[settings['COLL_WEIBO_RELATIONSHIPS']]
        self.Chinanews = db[settings['COLL_CHINA_NEWS']]

    def process_item(self, item, spider):
        # self.collection.insert(dict(item))
        # log.msg("Question added to MongoDB database!",
        #         level=log.DEBUG, spider=spider)

        if isinstance(item, items.BaiduSearchItem):
            self.insert_item(self.bdsearch, item)
        elif isinstance(item, items.RelationshipsItem):
            self.insert_item(self.Relationships, item)
        elif isinstance(item, items.TweetsItem):
            self.insert_item(self.Tweets, item)
        elif isinstance(item, items.InformationItem):
            self.insert_item(self.Information, item)
        elif isinstance(item, items.CommentItem):
            self.insert_item(self.Comments, item)
        elif isinstance(item, items.ChinaNewsItem):
            self.insert_item(self.Chinanews, item)

        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            # 有重复数据
            pass
