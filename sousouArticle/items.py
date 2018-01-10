# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SousouarticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    reviewurl = scrapy.Field()
    articleId = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    companyId = scrapy.Field()
    companyName = scrapy.Field()
    Thumb = scrapy.Field()
    _id = scrapy.Field()