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

    def fetch_html_content(self) -> str:
        """
        Fetches the HTML content of the specified URL.

        Returns:
            str: The HTML content of the response if successful.
            None: If an error occurs during the request.
        """
        try:
            # Make the HTTP GET request
            response = requests.get(url=self.url, headers=self.headers)

            # Raise an error for non-200 status codes
            response.raise_for_status()

            return response.content
        
        # Handle HTTP-specific errors (4xx, 5xx)
        except requests.exceptions.HTTPError as http_err:
            self.log_errors(f"HTTP error occurred: {http_err}")

        # Handle connection errors
        except requests.exceptions.ConnectionError as conn_err:
            self.log_errors(f"Connection error occurred: {conn_err}")

        # Handle request timeouts   
        except requests.exceptions.Timeout as timeout_err:
            self.log_errors(f"Request timed out: {timeout_err}")

        # Handle other requests exceptions
        except requests.RequestException as req_err:
            self.log_errors(f"An error occurred during the request: {req_err}")

    def article_headline_extraction(self) -> str:
        """
        Extracts the headline from the article page.

        Returns:
            str: The article headline if found.
            None: If an error occurs or the headline is not found.
        """ 
        # retrieve html content
        html_content = self.fetch_html_content()

        # if html content is None
        if not html_content:
            return None
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            article_headline = soup.find('h1').get_text(strip=True)  

            # Check if the headline exists
            if not article_headline:
                raise ValueError("Article content not found in the provided HTML structure.")
            
            return article_headline
        except Exception as e:
            # error is most likely due to the element class name changing over time
            self.log_errors(f"Failed to extract headline: {e}")
            return None

    def article_content_extraction(self) -> str:
        """
        Extracts the main content of the article from the page.

        Returns:
            str: The extracted article content if found.
            None: If an error occurs or the content is not found.
        """
        # retrieve HTML content
        html_content = self.fetch_html_content()

        if not html_content:
            return None

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Match a div where the class contains 'article' and 'content'.
            raw_content = soup.find(
                'div', 
                class_= lambda cls: cls and 'article' in cls and 'content' in cls in cls
                )                 

            if not raw_content:
                raise ValueError("Article content not found in the provided HTML structure.")
            
            # Extract and clean the text from the raw content
            raw_text = raw_content.get_text()
            cleaned_text = " ".join(raw_text.split())
            
            return cleaned_text

        except Exception as e:
            # Log errors, likely due to changes in HTML structure
            self.log_errors(f"Failed to extract article content: {e}")
            return None
    
    def parse_content(self):
        """
        Parses the HTML content and returns both the article headline and content.

        Returns:
            tuple: (str, str) The article headline and content if found.
        """

        headline = self.article_headline_extraction()
        content = self.article_content_extraction()

        return headline, content
    
    @staticmethod
    def log_errors(message):
        """
        Logs an error message. Replace with actual logging in production.

        Args:
            message (str): The error message to log.
        """
        print(f"ERROR: {message}")
        
scraper_cnn = Scraper(url='https://www.cnn.com/2025/01/04/politics/mike-johnson-donald-trump-gop-agenda/index.html')
article_headline, article_content = scraper_cnn.parse_content()
print(f'CNN:\nArticle Headline: {article_headline}\n\nArticle Content: {article_content}\n')

scraper_fox = Scraper(url='https://www.foxnews.com/us/pennsylvania-man-served-army-indicted-charges-attempted-join-hezbollah-kill-jews-doj')
article_headline, article_content = scraper_fox.parse_content()
print(f'Fox News:\nArticle Headline: {article_headline}\n\nArticle Content: {article_content}\n')

scraper_ap = Scraper(url='https://apnews.com/article/new-orleans-bourbon-street-truck-crash-terrorism-149bdb38ca0d7fc8e184eb3d32b5de40')
article_headline, article_content = scraper_ap.parse_content()
print(f'AP:\nArticle Headline: {article_headline}\n\nArticle Content: {article_content}\n')
