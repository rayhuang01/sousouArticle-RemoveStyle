# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
#from urllib import parse
from bs4 import BeautifulSoup
import html
#import pysolr
from sousouArticle.items import SousouarticleItem
from pymongo import MongoClient
#import pymongo
import pprint
"""
******************************************************************
step 1: set process company range in line {}, mapping to _id in SEOCompany
******************************************************************
"""
class SousouaticleSpider(scrapy.Spider):
    name = 'sousouAticle'
    allowed_domains = ['weixin.sogou.com','mp.weixin.qq.com','mmbiz.qpic.cn']
    start_urls = ['http://weixin.sogou.com/']
    custom_settings={
            'MONGO_URI':'mongodb://192.168.8.119:2222/',
            'MONGO_DATEBASE':'zheyibu'
            }
    
    client = MongoClient('mongodb://192.168.8.119:2222/')
    db = client.get_database("zheyibu")
    
    def parse(self, response):
#        url = "http://weixin.sogou.com/weixin?type=2&s_from=input&query=%E4%B8%AD%E5%BC%98%E5%85%89%E4%BC%8F&ie=utf8&_sug_=n&_sug_type_=&w=01019900&sut=1979&sst0=1514388312989&lkt=0%2C0%2C0"
#        yield scrapy.Request(url=url,callback=self.parse_page)
        collection = self.db['SEOCompany']
        companies = collection.find({"_id":{"$gt": 2,"$lt":4}})
        for company in companies:
            pprint.pprint(company["Name"])
        
            yield scrapy.FormRequest.from_response(
                    response,
                    formdata={'query': company["Name"]},
                    callback=self.parse_page,
                    meta={'name':company["Name"], 'id':company['_id']}
                    )

    def parse_page(self, response):
        if response.status == 200:
            
            links = response.selector.xpath('//ul[@class="news-list"]/li/div[@class="txt-box"]/h3/a').extract()

            for link in links:
                sel = Selector(text=html.unescape(link), type="html")
                articleUrl = sel.xpath('//@href')[0].extract()
                
                yield scrapy.Request(url=articleUrl,
                                     callback=self.parse_article,
                                     meta={'name':response.meta.get('name'), 'id':response.meta.get('id')}
                                     )
            
            #NEXT PAGE
#            navigator = response.selector.xpath('//div[@class="p-fy"]').extract_first()
#            if navigator:
#                soup = BeautifulSoup(navigator,"html.parser")
#                
#                nextLink = soup.find_all('a',id='sogou_next')
#                if nextLink:
#                    next_page_url = "http://weixin.sogou.com/weixin" + nextLink[0].get('href')
#                    print (next_page_url)
#                    yield scrapy.Request(url=next_page_url,callback=self.parse_page)
            #NEXT PAGE
                
        else:
            print ("search failed on page:" + response.url)
            
    def parse_article(self, response):
        if response.status == 200:
            content = response.selector.xpath('//div[@id="page-content"]/div[@id="img-content"]/div[@id="js_content"]').extract_first()

            soup = BeautifulSoup(content,"html.parser")
            for img in soup.findAll('img'):
                newtag =  soup.new_tag('img',src=img['data-src'],style='width: 623px;cursor: zoom-in;')
                img.replaceWith(newtag)
            ##################################
            #删除样式
            ##################################
#            for bi in soup.findAll('section'):
#                if bi['style']:
#                    del (bi['style'])
            ##################################
            #删除样式
            ##################################
                    
            content = soup.prettify()
            
            item = SousouarticleItem()
            item['reviewurl'] = response.url
            item['articleId'] = "0"
            item['content'] = content
            item['author'] = response.selector.xpath('//div[@id="page-content"]/div[@id="img-content"]/div[@id="meta_content"]/span[@class="rich_media_meta rich_media_meta_text rich_media_meta_nickname"]/text()').extract_first()
            item['date'] = response.selector.xpath('//div[@id="page-content"]/div[@id="img-content"]/div[@id="meta_content"]/em[@class="rich_media_meta rich_media_meta_text"]/text()').extract_first()
            item['title'] = response.selector.xpath('//div[@id="page-content"]/div[@id="img-content"]/h2[@class="rich_media_title"]/text()').extract_first().strip('\r\n').lstrip().rstrip()
            item['image_urls'] = [src for src in response.xpath('//div[@id="page-content"]/div[@id="img-content"]//img/@data-src').extract()]
            item['image_paths'] = []
            item['companyId'] = response.meta.get('id')
            item['companyName'] = response.meta.get('name')

            yield item
        else:
            print ("search failed on article:" + response.url)