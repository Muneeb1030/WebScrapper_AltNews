from scrapy import Spider
from scrapy.http import Request 
from scrapy.selector import Selector

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from time import sleep

chrome_driver_path = r"D:\Projects\Assignments\DataScience\Web Scrapers\chromedriver.exe"

class AltnewsSpider(Spider):
    name = "altnews"
    allowed_domains = ["altnews.in"]
    # start_urls = ["https://altnews.in"]
    
    def start_requests(self):
        self.service = Service(chrome_driver_path) 
        self.driver = webdriver.Chrome(service=self.service) 
        self.driver.maximize_window()
        self.driver.get("https://altnews.in")
        sleep(5)
        
        
        
        
        
        sel = Selector(text=self.driver.page_source())

    def parse(self, response):
        pass
