from scrapy import Spider

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
import os
import requests
import re

chrome_driver_path = r"D:\Projects\Assignments\DataScience\Web Scrapers\chromedriver.exe"


class AltnewsSpider(Spider):
    name = "altnews"
    allowed_domains = ["altnews.in"]
    start_urls = ["https://altnews.in"]
    
    Articles = []
    Tags = []
    DateValue = []
    Headlines = []
    Urls =[]
    Author = []
    ArticleContent = []
    ArticleImagesUrl = []
    ArticleVideosUrl = []
    
    Idset = set()#to avoid duplicate insertion
     
    def parse(self,response):
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.driver.get("https://altnews.in")
        
        self.CreateDirectories()
        self.Scrolling()
        
        self.driver.close()
        
    
    def Scrolling(self):
        scrolling = True
        old_count = len(self.Articles)
        
        while scrolling:
            content = WebDriverWait(self.driver, 5).until(
        EC.presence_of_all_elements_located((By.XPATH,'//*[@class="pbs-content"]')))
            content = content[3]
            self.Articles = content.find_elements(By.TAG_NAME,'article')
            
            for article in self.Articles:
                article.location_once_scrolled_into_view # getting in focus
                receivingData = self.parseNews(article)
                headline  = receivingData["Headline"]
                if headline not in self.Idset and headline != "Headline":
                    self.Tags.append(receivingData["tag"])
                    self.Headlines.append(headline)
                    Url = receivingData["PostUrl"]
                    self.Author.append(receivingData["Author"])
                    print(headline)
                    self.Idset.add(headline)
                    self.Urls.append(Url)
                    
                    self.parseArticle(Url,headline)
            
            sleep(3)
            self.Articles = content.find_elements(By.TAG_NAME,'article')
            new_count = len(self.Articles)
                    
            
            # # Main Logic
            # if old_count == new_count:
            #     scrolling = False
            
            # Testing
            if len(self.Articles) > 10:
                scrolling = False
            else:
                old_count = new_count
                
        print(self.Tags)
        
    def parseNews(self,Article):
        try:
            tag = Article.find_element(By.CLASS_NAME,'cat-tag').text
            #Date = Article.find_element(By.TAG_NAME,'time').text
            Headline =  Article.find_element(By.TAG_NAME,'h4').text
            PostUrl = Article.find_element(By.XPATH,'.//h4/a').get_attribute("href")
            Author = Article.find_element(By.XPATH,'//span[@class="author vcard"]//a[@class="url fn n"]').text
            returningData = {
                'tag': tag,
                # 'Date': Date,
                'Headline': Headline,
                'PostUrl': PostUrl,
                'Author': Author
            }
        except:
            returningData = {
                'tag': 'tag',
                #'Date': 'Date',
                'Headline': 'Headline',
                'PostUrl': 'PostUrl',
                'Author': 'Author'
            }
            
        return returningData
        
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