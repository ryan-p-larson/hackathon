import scrapy
from scrapy.crawler import CrawlerProcess

import json
class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('../data/01-courses-result.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


import logging
class CourseSpider(scrapy.Spider):
    name = "majors"
    start_urls = [
                        # fall 2017
                        'https://myui.uiowa.edu/my-ui/courses/course-search.page?query.sessionCode=20173&query.courseSubject=&query.titleAndTextQuery=&query.levels=R&query.levels=L&query.levels=U&query.levels=E&query.sort=COURSE_NUMBER&search=Search&_sourcePage=PqZXQMXRwPGDmkqcL2BD2Ll4l2gJIY9GsXpBZa20Uy9APawb9ab70w%3D%3D&__fp=C7r3hKST39cMaZgyVMinLsr9KSXoD4wmWnkh0kcQIuZeHPka4sCeo2MgFxpqZNG40SaqKv4YQUdiZUgwYvuXxw%3D%3D&_ticket=OkUuxZt9qrAWrzYw2FmCCSh8WEEj2fMl',
                        # spring 2016
                        'https://myui.uiowa.edu/my-ui/courses/course-search.page?query.sessionCode=20168&query.courseSubject=&query.titleAndTextQuery=&query.levels=R&query.levels=L&query.levels=U&query.levels=E&query.sort=COURSE_NUMBER&search=Search&_sourcePage=PqZXQMXRwPGDmkqcL2BD2Ll4l2gJIY9GsXpBZa20Uy9APawb9ab70w%3D%3D&__fp=C7r3hKST39cMaZgyVMinLsr9KSXoD4wmWnkh0kcQIuZeHPka4sCeo2MgFxpqZNG40SaqKv4YQUdiZUgwYvuXxw%3D%3D&_ticket=OkUuxZt9qrAWrzYw2FmCCSh8WEEj2fMl'
                        ]
    custom_settings = {
        'LOG_LEVEL': logging.WARNING,
        'ITEM_PIPELINES': {'__main__.JsonWriterPipeline': 1}, # Used for pipeline 1
        'FEED_FORMAT':'json',                                                   # Used for pipeline 2
        'FEED_URI': '../data/01-courses-result.json'                                   # Used for pipeline 2
    }

    def parse(self, response):
        content = response.xpath('//*[@id="content"]/div/div[3]/div')
        course_divs = content.xpath('.//div[@class="panel panel-default course-result"]')
        
        for course_div in course_divs:

            # heading
            div_heading = course_div.xpath('.//div[1]/h3[@class="panel-title"]')
            attr_name = div_heading.xpath('.//a[@class="normal"]/text()').extract_first()
            attr_hrs = div_heading.xpath('.//span[@class="pull-right"]')\
                .xpath('normalize-space(.)').extract_first()

            # course names
            course_ids = course_div.xpath('.//a[@class="course-number"]/text()').extract()
            course_links = course_div.xpath('.//a[@class="course-number"]')

            # Details
            attr_desc = course_div.xpath('.//div[@class="panel-body"]/div/text()')\
                .extract_first().strip()

            # requirements!
            attr_reqs = course_div.xpath('.//div[3]/div/div/em/p/text()').extract_first()

            for link in course_links:
                _id = link.xpath('.//text()').extract_first()
                href = 'http://catalog.registrar.uiowa.edu' + link.xpath('.//@href').extract_first()
        
                yield {
                    "courseID": _id,
                    "name": attr_name,
                    "hours": attr_hrs,
                    "description": attr_desc,
                    "requirements": attr_reqs,
                    "href": href
                }
            

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(CourseSpider)
process.start()
