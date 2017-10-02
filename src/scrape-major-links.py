import scrapy
from scrapy.crawler import CrawlerProcess

import json
class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('../data/majorresult.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


import logging
class MajorsSpider(scrapy.Spider):
    name = "majors"
    start_urls = [
        'http://catalog.registrar.uiowa.edu/catalog-contents/',
    ]
    custom_settings = {
        'LOG_LEVEL': logging.WARNING,
        'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, # Used for pipeline 1
        'FEED_FORMAT':'json',                                 # Used for pipeline 2
        'FEED_URI': '../data/majorresult.json'                        # Used for pipeline 2
    }

    def parse(self, response):
        major_groups = response.css('ul.leveltwo')
        majors = [a for a in major_groups.xpath('.//a')]

        for major in majors:
            yield {
                'href': 'http://catalog.registrar.uiowa.edu' + major.css('a::attr(href)').extract()[0],
                'text': major.xpath('text()').extract()
            }

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(MajorsSpider)
process.start()
