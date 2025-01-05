import requests
from bs4 import BeautifulSoup

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
        
    def parse_content(self):
        """
        Parses HTML content and returns the article headline and article content.
        
        Input: HTML content
        Return: article headline AND article content or None
        """
        
        #Retrieve HTML content
        html_content = self.get_content()

        #if html content is None
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, "html.parser")
        try:
            article_headline = soup.find('h1', class_= "headline__text inline-placeholder vossi-headline-text").get_text(strip=True)
            article_content = 4 # placeholder

            if article_headline and article_content:
                return article_headline, article_content
            #If this doesn't work, you most likely need to change the class identifier
        except Exception as e:
            self.log_errors(f"Failed to parse page: {e}")
            return None
        
scraper = Scraper(url='https://www.cnn.com/2025/01/04/politics/mike-johnson-donald-trump-gop-agenda/index.html')
article_headline, article_content = scraper.parse_content()
print(f'article headline: {article_headline}\narticle content: {article_content}')