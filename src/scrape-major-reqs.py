import scrapy
from scrapy.crawler import CrawlerProcess
import json

#### STARTING URLS!
with open('../data/majorresult.json') as f:
    data = json.load(f)

major_links = [a['href'] for a in data]
def test_link(link):
    # split /
    url_part = link.split('/')[-2]
    link_type = url_part.split('-')[-1]

    return (link_type == 'ba') or (link_type =='bs')
whitelist_links = [link for link in major_links if test_link(link) == True]


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('../data/academicplansresult.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


import logging
class PlansSpider(scrapy.Spider):
    name = "academic plans"
    start_urls = whitelist_links

    custom_settings = {
        'LOG_LEVEL': logging.WARNING,
        'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, # Used for pipeline 1
        'FEED_FORMAT':'json',                                 # Used for pipeline 2
        'FEED_URI': '../data/academicplanresult.json',                 # Used for pipeline 2
        'DOWNLOAD_DELAY': 2
    }

    def parse(self, response):
        url = response.url
        major = url.split('/')[-2]

        academic_plans = response.xpath('//table[@class="sc_plangrid"]')
        aca_plan = academic_plans[0]

        currentYear = None
        currentSemester = None

        rows = aca_plan.xpath('.//tr')
        for row in rows:
            row_class = row.xpath('@class').extract_first()
            #print (row_class)

            # check sum (skip)
            #row.xpath('@class').extract_first()                #'plangridsum odd'
            if ('plangridsum' in row_class):
                # 'even', 'odd' classes added
                continue

            # check year
            #row.xpath('.//th/@class').extract_first)()         # 'year'
            #row.xpath('.//th/text()').extract_first()          # 'Second Year'
            elif (row_class == 'plangridyear'):
                year = row.xpath('.//th/text()').extract_first()
                currentYear = year
                continue

            # check semester
            #row.xpath('@class').extract_first()                # 'plangridterm'
            #row.xpath('.//th/text()').extract_first()          # 'Fall'
            elif (row_class == 'plangridterm'):
                term = row.xpath('.//th/text()').extract_first()
                currentSemester = term
                continue
            else:
                # class infor
                #row.xpath('.//td[@class="codecol"]/a/text()').extract_first() # 'CS:1210'
                row_link = row.xpath('.//td[@class="codecol"]/a') #.extract_first()
                row_link_class = row_link.xpath('@class').extract_first()

                if (row_link_class is not None):
                    courseID = row_link.xpath('text()').extract_first()
                    yield {
                        "major": major,
                        "courseID": courseID,
                        "year": currentYear,
                        "semester": currentSemester
                        # theres room in the url for
                        # college
                        # and department
                    }









process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(PlansSpider)
process.start()
