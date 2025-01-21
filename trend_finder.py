import json
from base_scraper import BaseScraper

# For now this will only include CNN articles. Expand once article finder, scraper, and text processing pipeline is finished. 
# Realized that is probably easier to create an article finder for each possible website.
class CNNArticleFinder():
    """
    The purpose of this class is to extract the urls for the trending articles of the topic of interest. 
    The class should return a list of urls for the article data extraction tools.
    """
    def __init__(self, url, user_data):
        """
        Initialize the CNNArticleFinder

        Args:
            topics (JSON String): A JSON string containing topics to find articles for.
                          Example: '{"topics": ["Technology", "Health"]}'
        """        
        self.topics = json.loads(user_data)['topics']
        self.topic_pages = self.topic_navigation()
        self.url = url

    def topic_navigation(self):
        """
        Navigates the CNNArticleFinder to the proper url based on topics selected.

        Return:
            topic_pages (str): list of strings containing the urls needed for extraction
                            Example: ['https://cnn.com/politics', 'https://www.cnn.com/world']
        """
        topic_pages = {
            'US': 'https://www.cnn.com/us',
            'World': 'https://www.cnn.com/world',
            'Politics': 'https://cnn.com/politics',
            'Business': 'https://cnn.com/business',
            'Health': 'https://cnn.com/health',
            'Entertainment': 'https://cnn.com/entertainment',
            'Style': 'https://cnn.com/style',
            'Travel': 'https://cnn.com/Travel',
            'Science': 'https://cnn.com/science',
            'Climate': 'https://cnn.com/climate'
        }
        
        # Access user topic preference
        user_topic_pref = self.topics

        # Get the keys based on user defined topic preference
        try:
            keys = set(user_topic_pref) & set(topic_pages.keys())  
            pages = [topic_pages[key] for key in keys]    
            return pages
        except Exception as e:
            print(f'Error occured in topic navigation: {e}')

    def get_page_soup(self):
        """
        Return
           content (dict): dictionary containing the html content soup objects to the users desired topic pages
        """
        # Get the html content for each url
        content = {}
        try:
            for topic in self.topics:
                for page in self.topic_pages:
                    base_scraper = BaseScraper(url=page)
                    page_soup = base_scraper.get_soup()
                    content[topic] = page_soup
            return content
        except Exception as e:
            print(f'Error occured in get_page_soup: {e}')

    def hyperlink_search(self):
        """
        Searches soup for hyperlinks. 

        Return:
            hyperlinks (dict): A dictionary containing article hyperlinks in string format     
        """
        # retrieve page soup
        soup = self.get_page_soup()

        # if page soup is None
        if not soup:
            raise ValueError('Page soup could not be found')
        
        try:
            content = {}
            for topic, page in soup.items():
                div = page.find('div', class_='container_lead-plus-headlines__cards-wrapper')
                a_elements = div.find_all('a', href=True)
                href_values = [tag['href'] for tag in a_elements] 
                content[topic] = href_values
            return content
        except Exception as e:
            print(f'There was an error with element finding for hyperlink search: {e}')

    def get_link(self):
        """
        Uses extracted hyperlinks and converts them to accessable urls for article data extraction tool.

        Returns:
            urls (dict): dictionary of urls to be sent to the article data extraction tool
        """
        hyperlinks = self.hyperlink_search()

        if not hyperlinks:
            raise ValueError('Hyperlinks for article data extraction tool could not be found')
        
        try:
            urls = {}
            for topic, hyperlink_list in hyperlinks.items():
                urls[topic] = []        
                for hyperlink in hyperlink_list:
                    url_prefix = 'https://www.cnn.com' 
                    proper_link = url_prefix + hyperlink
                    urls[topic].append(proper_link)         
            return urls
        except Exception as e:
            print(f'Error occured in the url creation process: {e}')

def main():
    user_data = {
        'topics': ['Politics', 'World']
    }
    user_data = json.dumps(user_data)
    article_finder = CNNArticleFinder(
        url='https://www.cnn.com/politics', 
        user_data=user_data)
    print(article_finder.topics)
    print(article_finder.topic_pages)
    print(article_finder.hyperlink_search())
    print(article_finder.get_link())

if __name__ == '__main__':
    main()