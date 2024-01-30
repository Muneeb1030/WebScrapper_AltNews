import scrapy


class AltnewsSpider(scrapy.Spider):
    name = "altnews"
    allowed_domains = ["altnews.in"]
    start_urls = ["https://altnews.in"]

    def parse(self, response):
        pass
