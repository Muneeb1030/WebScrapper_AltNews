from scrapy import Spider
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import requests
import pandas as pd

chrome_driver_path = r"D:\Projects\Assignments\DataScience\Web Scrapers\chromedriver.exe"

# Specify the path to the Chrome driver executable
class AltnewsSpider(Spider):
    name = "altnews"
    allowed_domains = ["altnews.in"]
    start_urls = ["https://altnews.in"]
     
    def parse(self, response):
        # Set up the Chrome WebDriver
        self.service = Service(chrome_driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.maximize_window()
        self.driver.get(response.url)
        
        # Create directories for storing scraped data
        self.create_directories()
        # f# Call functions to parse Articles
        self.scrolling()
        
        self.driver.close()
    
    def scrolling(self):
        scrolling = True
        articles = []
        article_links = set() # to avoid repeation
        old_count = len(articles)
        try:# In case of any abnormality or exception
            #scrollling logic
            while scrolling:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(3)
                articles = self.driver.find_elements(By.XPATH, '//h4/a') # Extracting links to articles
                
                for link in articles: #Inserting article links in set to avaoid repeation
                    article_links.add(link.get_attribute("href"))
                                                       
                new_count = len(articles)
                        
                if old_count == new_count: # Scroll ends, if no new article is found
                    scrolling = False
                else:
                    old_count = new_count # else continues
            
            self.parse_article(article_links)
        except:
            self.parse_article(article_links)
            
    def parse_article(self, links):
        publishers = []
        dates = []
        headlines = []
        article_urls = []
        article_tags = []
        article_content = []
        article_images = []
        article_videos = []
        article_filenames = []
        
        for idx, link in enumerate(links):
            article_urls.append(link)
            self.driver.get(link)
            sleep(2)
            
            # Extract News Headline
            title = self.driver.find_element(By.TAG_NAME, "h1").text 
            # Create file name
            filename = "".join(char if char.isalnum() or char.isspace() else "_" for char in title)
            
            # Extract Article Content
            paragraphs_list = self.driver.find_elements(By.XPATH, "//div[@data-role='article_content']//p")
            text = ' '.join([paragraph.text for paragraph in paragraphs_list[:-7]])
            
            # Extract Images Url Present in page
            url_list = self.driver.find_elements(By.XPATH, "//div[@data-role='article_content']//img")
            image_url_list = ', '.join([link.get_attribute("src") for link in url_list])
            
            # Download Images from article
            for idx, link in enumerate(url_list[:-3]):
                self.download_image(link.get_attribute("src"), idx, filename)
            
            url_list.clear()
            
            # Extract Video Url present in page
            url_list = self.driver.find_elements(By.XPATH, "//div[@data-role='article_content']//iframe")
            video_url_list = ', '.join([link.get_attribute("src") for link in url_list])
            
            url_list.clear()
            
            
            headlines.append(title)
            article_filenames.append(filename)
            dates.append(self.driver.find_element(By.XPATH, '//header//time').text) # Extract Time
            publishers.append(self.driver.find_element(By.CLASS_NAME, "byline").text)  # Extract author information
            article_tags.append(self.driver.find_element(By.ID, "breadcrumbs").find_elements(By.TAG_NAME, 'a')[1].text) # Extract Tag 
            article_content.append(text)
            article_images.append(image_url_list)
            article_videos.append(video_url_list)
            
            if idx % 20 == 0: # Allow Program to write data after regular interval
                self.write_to_csv(publishers, dates, headlines, article_urls, article_tags, article_content, article_images, article_videos, article_filenames)
                
    def write_to_csv(self, publishers, dates, headlines, article_urls, article_tags, article_content, article_images, article_videos, article_filenames):
        csv_path = 'output_data/Articles.csv'
        
        # Data Header (the content to be scrapped)
        columns = ['Date', 'ArticleTags', 'Publisher', 'Headline', 'ArticleUrl']
                
        new_data_list = []

        for idx in range(len(article_filenames)):
            data_item = {
                'Date': dates[idx],
                'ArticleTags': article_tags[idx],
                'Publisher': publishers[idx],
                'Headline': headlines[idx],
                'ArticleUrl': article_urls[idx]      
            }
            new_data_list.append(data_item)
            self.write_to_file({
                'Headlines': headlines[idx],
                'ArticleFileName': article_filenames[idx],
                'Date': dates[idx],
                'Publisher': publishers[idx],
                'ArticleTag': article_tags[idx],
                'ArticleContent': article_content[idx],
                'ArticleImages': article_images[idx],
                'ArticleVideos': article_videos[idx],
                'ArticleUrl': article_urls[idx]
            })
                    
        try:
            # Read the existing CSV file or create a new one if not found
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            df = pd.DataFrame(columns=columns)
                
        # Add data to the dataframe and write to the CSV file
        df = pd.concat([df, pd.DataFrame(new_data_list)], ignore_index=True)
        df.to_csv(csv_path, index=False, mode='a', header=not os.path.isfile(csv_path))
                
        headlines.clear()
        article_filenames.clear()
        dates.clear()
        publishers.clear()
        article_tags.clear()
        article_content.clear()
        article_images.clear()
        article_videos.clear()
        article_urls.clear()
        
    def download_image(self, image_url, idx, title):
        download = requests.get(image_url, stream=True) 
        images_folder = os.path.join('output_data\\Images')
        # Construct the full path with a different filename for each image
        image_path = os.path.join(images_folder, f'{title}_{idx}.jpg')

        with open(image_path, 'wb') as f:
            for chunk in download.iter_content(chunk_size=128):
                f.write(chunk)

    def write_to_file(self, data_item):
        # Create or open the file in write mode inside the "output_data/Articles" directory
        output_directory = "output_data/Articles"
        os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist
        
        with open(os.path.join(output_directory, f"{data_item['ArticleFileName']}.txt"), "w", encoding="utf-8") as file:
            file.write(f"Date: {data_item['Date']}\n")
            file.write(f"Publisher: {data_item['Publisher']}\n\n")
            file.write(f"Headline : {data_item['Headlines']}\n\n")
            file.write(f"Article Tag: {data_item['ArticleTag']}\n\n")
            file.write(f"Article URL: {data_item['ArticleUrl']}\n\n")
            file.write(f"Article : {data_item['ArticleContent']}\n\n")
            file.write(f"Article Image Links: {data_item['ArticleImages']}\n\n")  
            file.write(f"Article Video Links: {data_item['ArticleVideos']}\n\n")
    
    def create_directories(self):
        output_directory = 'output_data'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        articles_sub_directory = f'{output_directory}/Articles'
        if not os.path.exists(articles_sub_directory):
            os.makedirs(articles_sub_directory)  
        
        images_sub_directory = f'{output_directory}/Images'
        if not os.path.exists(images_sub_directory):
            os.makedirs(images_sub_directory)
