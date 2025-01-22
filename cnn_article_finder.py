import json
from logger import setup_logger
from typing import Dict, List, Optional
from base_scraper import BaseScraper

# Add custom exceptions
class NoTopicsError(Exception):
    """Raised when there's no topics provided"""
    pass

class InvalidJSONError(Exception):
    """Raised when there's an error in the initialization of the CNNArticleFinder class"""
    pass

class NoMatchingTopicsError(Exception):
    """Raised when there's no matching topics found"""
    pass

class TopicNavigationError(Exception):
    """Raised when there's an error in topic navigation"""
    pass

class PageSoupError(Exception):
    """Raised when there's an error in getting soup"""
    pass

class DivNotFoundError(Exception):
    """Raised when the div is not found in the soup"""
    pass

class AElementNotFoundError(Exception):
    """Raised when the a elements are not found in the soup"""
    pass

class CNNConfig:
    """Configuration class for CNN-related constants and settings"""
    BASE_URL = "https://www.cnn.com"
    TOPIC_PAGES = {
        'US': f'{BASE_URL}/us',
        'World': f'{BASE_URL}/world',
        'Politics': f'{BASE_URL}/politics',
        'Business': f'{BASE_URL}/business',
        'Health': f'{BASE_URL}/health',
        'Entertainment': f'{BASE_URL}/entertainment',
        'Style': f'{BASE_URL}/style',
        'Travel': f'{BASE_URL}/Travel',
        'Science': f'{BASE_URL}/science',
        'Climate': f'{BASE_URL}/climate'
    }

class CNNArticleFinder:
    """
    Extracts URLs for trending CNN articles of the topics of interest.
    """
    def __init__(self, user_data: str):
        """
        Args:
            user_data (str): JSON string containing topics to find articles for
                           Example: '{"topics": ["Technology", "Health"]}'                    
        Raises:
            InitError: If no topics are provided by the user_data json string
            InitError: If no valid topics are found in the user_data json string
            InitError: Invalid JSON format in user_data
        """
        self.logger = setup_logger(__name__)
        
        # This error handling will likely be given to another file. Will keep for now
        try:
            parsed_data = json.loads(user_data)
            self.topics = parsed_data.get('topics', [])

            if not self.topics:
                self.logger.critical("No topics provided in user_data")
                raise NoTopicsError("No topics provided in user_data")
            
            if not set(self.topics) & set(CNNConfig.TOPIC_PAGES.keys()):
                self.logger.critical(f"Invalid topics provided: {self.topics}. Valid topics are: {list(CNNConfig.TOPIC_PAGES.keys())}")
                raise NoMatchingTopicsError('User provided topics do not match the topics in the CNNConfig.TOPIC_PAGES dictionary')  
                  
        except json.JSONDecodeError as e:
            self.logger.critical(f"Invalid JSON format in user_data: {e}")
            raise InvalidJSONError(f"Invalid JSON format in user_data: {e}")
        
        self.topic_pages = self.topic_navigation()

    def topic_navigation(self) -> List[str]:
        """
        Navigates to the proper URLs based on selected topics.

        Returns:
            List[str]: List of URLs needed for extraction

        Raises:
            NoMatchingTopicsError: If no matching topics are found
            ValueError: Navigation fails
        """
        user_topics = self.topics
        topic_pages = CNNConfig.TOPIC_PAGES

        try:
            valid_topics = set(user_topics) & set(topic_pages.keys())
            if not valid_topics:
                # This may not be useful right now, but will be once the LLM is creating desired user topics based 
                # on political preferences.
                self.logger.error(f"No matching topics found. Provided topics: {self.topics}")
                raise NoMatchingTopicsError(f"No matching topics found. Provided topics: {self.topics}")
            
            return [topic_pages[key] for key in valid_topics]
            
        except Exception as e:
            self.logger.error(f"Error in topic_navigation: {e}")
            raise Exception(f"Error in topic_navigation: {e}")   

    def get_page_soup(self) -> Dict[str, object]:
        """
        Fetches and parses HTML content for each topic page.

        Returns:
            Dict[str, object]: Dictionary containing BeautifulSoup objects for each topic

        Raises:
            PageSoupError: If page content could not be fetched for any topic
        """
        content = {}
        for topic in self.topics:
            for page in self.topic_pages:
                base_scraper = BaseScraper(url=page)
                page_soup = base_scraper.get_soup() # Let the BaseScraper handle the errors
                if not page_soup:
                    self.logger.error(f"Could not get soup for {topic} from {page}")
                    raise PageSoupError(f"Could not get soup for {topic} from {page}")
                content[topic] = page_soup

        return content

    def hyperlink_search(self) -> Dict[str, List[str]]:
        """
        Searches soup for hyperlinks.

        Returns:
            Dict[str, List[str]]: Dictionary containing article hyperlinks by topic

        Raises:
            ValueError: If page soup is not found
        """
        soup = self.get_page_soup()
        try:
            content = {}
            for topic, page in soup.items():
                div = page.find('div', class_='container_lead-plus-headlines__cards-wrapper')
                if not div:
                    self.logger.warning(f"No headline wrapper found in soup for {topic}")
                    raise DivNotFoundError(f"No headline wrapper found in soup for {topic}")

                a_elements = div.find_all('a', href=True)
                if not a_elements:
                    self.logger.warning(f"No a elements found for {topic}. Hyperlinks not found")
                    raise AElementNotFoundError(f"No a elements found for {topic}. Hyperlinks not found")

                href_values = [tag['href'] for tag in a_elements]
                content[topic] = href_values
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error in hyperlink_search: {e}")
            raise Exception(f"Error in hyperlink_search: {e}")

    def get_link(self) -> Dict[str, List[str]]:
        """
        Converts extracted hyperlinks to accessible URLs.

        Returns:
            Dict[str, List[str]]: Dictionary of complete URLs by topic

        Raises:
            ValueError: If no hyperlinks are found
        """
        try:
            hyperlinks = self.hyperlink_search()
            if not hyperlinks:
                raise ValueError('No hyperlinks found')

            urls = {}
            for topic, hyperlink_list in hyperlinks.items():
                urls[topic] = [
                    f"{CNNConfig.BASE_URL}{hyperlink}" 
                    for hyperlink in hyperlink_list
                ]
            return urls
            
        except Exception as e:
            self.logger.error(f"Error creating URLs: {e}")

def main():
    try:
        user_data = json.dumps({
            'topics': ['US']
        })
        
        article_finder = CNNArticleFinder(
            user_data=user_data
        )
        
        # Execute and log results
        article_finder.logger.info(f"Selected topics: {article_finder.topics}")
        article_finder.logger.info(f"Topic pages: {article_finder.topic_pages}")
        article_finder.logger.info(f"Found hyperlinks: {article_finder.hyperlink_search()}")
        article_finder.logger.info(f"Complete URLs: {article_finder.get_link()}")
        
    except Exception as e:
        article_finder.logger.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    main() 