import requests
from bs4 import BeautifulSoup
import re

class Scraper:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.google.com/',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    def get_content(self):
        """
        Fetches the landing page for NVDA and returns the response
        
        Input: self
        Return: HTML content or None incase of error
        """
        try:
            response = requests.get(url=self.url, headers=self.headers)
            response.raise_for_status()  # Raise an error for non-200 status codes
            return response.content
        except requests.RequestException as e: 
            #catches any HTTP related errors
            self.log_errors(f"Failed to reach page: {e}")
            return None
    
    def article_content_extraction(self):
        """
        Extracts the article content from a webpage.
        Input: self
        Return: article content
        """

        # retrieve HTML content
        html_content = self.get_content()

        # incase HTML content is None
        if not html_content:
            return None

        # extract article content
        soup = BeautifulSoup(html_content, 'html_parser')
        try:
            article_content = soup.find('div', class_= lambda cls: cls and 'article' in cls and 'content' in cls in cls)                 
            article_content = article_content.get_text() #extract only the text
            article_content = " ".join(article_content.split())
            return article_content
        
        except Exception as e:
            # error is most likely due to the element class name changing over time
            self.log_errors(f"Failed to parse page: {e}")
            return None
     
    def parse_content(self):
        """
        Parses HTML content and returns the article headline and article content.
        
        Input: HTML content
        Return: article headline AND article content or None
        """
        
        # retrieve html content
        html_content = self.get_content()

        # if html content is None
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, "html.parser")
        try:
            article_headline = soup.find('h1').get_text(strip=True)
            article_content = soup.find_all(lambda tag: 
                         tag.name == 'div' and
                         tag.get('class') and 
                         any('article' and 'content' in cls for cls in tag.get('class'))
                        )
            
            if article_headline and article_content:
                return article_headline, article_content
        except Exception as e:
            # error is most likely due to the element class name changing over time
            self.log_errors(f"Failed to parse page: {e}")
            return None
        
scraper_cnn = Scraper(url='https://www.cnn.com/2025/01/04/politics/mike-johnson-donald-trump-gop-agenda/index.html')
article_headline, article_content = scraper_cnn.parse_content()
print(f'article headline: {article_headline}\narticle content: {article_content}\n')

scraper_fox = Scraper(url='https://www.foxnews.com/us/pennsylvania-man-served-army-indicted-charges-attempted-join-hezbollah-kill-jews-doj')
article_headline, article_content = scraper_fox.parse_content()
print(f'article headline: {article_headline}\narticle content: {article_content}\n')

scraper_ap = Scraper(url='https://apnews.com/article/new-orleans-bourbon-street-truck-crash-terrorism-149bdb38ca0d7fc8e184eb3d32b5de40')
article_headline, article_content = scraper_fox.parse_content()
print(f'article headline: {article_headline}\narticle content: {article_content}\n')
