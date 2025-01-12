from base_scraper import BaseScraper
from bs4 import BeautifulSoup

class CNNScraper(BaseScraper):
    def get_headline(self) -> str:
        """
        Extracts the headline from the article page.

        Returns:
            str: The article headline if found.
            None: If an error occurs or the headline is not found.
        """ 
        # retrieve html content
        soup = self.get_soup()

        # if html content is None
        if not soup:
            return None
            
        try:
            article_headline = soup.find('h1').get_text(strip=True)  

            # Check if the headline exists
            if not article_headline:
                raise ValueError("Article content not found in the provided HTML structure.")
            
            return article_headline
        except Exception as e:
            # error is most likely due to the element class name changing over time
            return None
    
    def get_content(self) -> str:
        """
        Extracts the main content of the article from the page.

        Returns:
            str: The extracted article content if found.
            None: If an error occurs or the content is not found.
        """
        # retrieve HTML content
        soup = self.get_soup()

        if not soup:
            return None

        try:
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
            return None

    def get_article_data(self) -> tuple[str, str]:
        """
        Extracts the headline and content from the website.

        Returns:
            tuple: (str, str) The article headline and content if found.
        """

        headline = self.get_headline()
        content = self.get_content()

        return headline, content

scraper_cnn = CNNScraper(url='https://www.cnn.com/2025/01/04/politics/mike-johnson-donald-trump-gop-agenda/index.html')
article_headline, article_content = scraper_cnn.get_article_data()
print(f'CNN:\nArticle Headline: {article_headline}\n\nArticle Content: {article_content}\n')