from typing import Iterable
from scrapy import Spider
from scrapy.http import Request 
from scrapy.selector import Selector

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from time import sleep
import os

chrome_driver_path = r"D:\Projects\Assignments\DataScience\Web Scrapers\chromedriver.exe"


class AltnewsSpider(Spider):
    name = "altnews"
    allowed_domains = ["altnews.in"]
    # start_urls = ["https://altnews.in"]
    Tags = []
    DateValue = []
    Headlines = []
    Urls =[]
    Author = []
    
    def start_requests(self) -> Iterable[Request]:
        self.CreateDirectories()
        
        self.service = Service(chrome_driver_path) 
        self.driver = webdriver.Chrome(service=self.service) 
        self.driver.maximize_window()
        self.driver.get("https://altnews.in")
        sleep(5)
        
        self.Scrolling()
        
        return super().start_requests()
            
    def CreateDirectories(self):
        output_directory = 'output_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        articles_sub_directory = f'{output_directory}/detailed_news_articles'
        if not os.path.exists(articles_sub_directory):
            os.makedirs(articles_sub_directory)  
        
        images_sub_directory = f'{output_directory}/news_articles_Images'
        if not os.path.exists(images_sub_directory):
            os.makedirs(images_sub_directory) 
    
    def Scrolling(self):
        content = self.driver.find_elements(By.XPATH,'//*[@class="pbs-content"]')[3]
        for Article in content.find_elements(By.TAG_NAME,'article'):
            receivingData = self.parseNews(Article)
    
    
    def parseNews(Article):
        try:
            tag = Article.find_element(By.CLASS_NAME,'cat-tag').text
            Date = Article.find_element(By.TAG_NAME,'time').text
            Headline =  Article.find_element(By.TAG_NAME,'h4').text
            PostUrl = Article.find_element(By.XPATH,'.//h4/a').get_attribute("href")
            Author = Article.find_element(By.XPATH,'//span[@class="author vcard"]//a[@class="url fn n"]').text
            returningData = [tag,Date,Headline,PostUrl,Author]
        except:
            returningData = ['tag','Date','Headline','PostUrl','Author']
            
        return returningData
        
    def parse(self, response):
        pass
        
