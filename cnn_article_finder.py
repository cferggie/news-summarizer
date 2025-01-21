import json
import logging
from typing import Dict, List, Optional
from base_scraper import BaseScraper

# Add custom exceptions
class CNNArticleFinderError(Exception):
    """Base exception for CNNArticleFinder"""
    pass

class TopicNavigationError(CNNArticleFinderError):
    """Raised when there's an error in topic navigation"""
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
    def __init__(self, url: str, user_data: str):
        """
        Args:
            url (str): Base URL for CNN
            user_data (str): JSON string containing topics to find articles for
                           Example: '{"topics": ["Technology", "Health"]}'                    
        Raises:
            ValueError: If no topics are provided by the user_data json string
            ValueError: If no valid topics are found in the user_data json string
            CNNArticleFinderError: Invalid JSON format in user_data
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            parsed_data = json.loads(user_data)
            self.topics = parsed_data.get('topics', [])

            if not self.topics:
                self.logger.error("No topics provided in user_data")
                raise ValueError("No topics provided in user_data")
            if not set(self.topics) & set(CNNConfig.TOPIC_PAGES.keys()):
                self.logger.error(f"Invalid topics provided: {self.topics}. Valid topics are: {list(CNNConfig.TOPIC_PAGES.keys())}")
                raise ValueError('User provided topics do not match the topics in the CNNConfig.TOPIC_PAGES dictionary')        
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in user_data: {e}")
            raise CNNArticleFinderError(f"Invalid JSON format in user_data: {e}")
            
        self.url = url
        self.topic_pages = self.topic_navigation()

    def topic_navigation(self) -> List[str]:
        """
        Navigates to the proper URLs based on selected topics.

        Returns:
            List[str]: List of URLs needed for extraction

        Raises:
            TopicNavigationError: If no valid topics are found or navigation fails
        """
        user_topics = self.topics
        topic_pages = CNNConfig.TOPIC_PAGES

        try:
            valid_topics = set(user_topics) & set(topic_pages.keys())
            if not valid_topics:
                self.logger.error(f"No valid topics found. Provided topics: {self.topics}")
                raise TopicNavigationError(f"No valid topics found. Provided topics: {self.topics}")
            
            return [topic_pages[key] for key in valid_topics]
            
        except Exception as e:
            self.logger.error(f"Error in topic navigation: {e}")
            raise TopicNavigationError(f"Failed to navigate topics: {e}") from e

    def get_page_soup(self) -> Dict[str, Optional[object]]:
        """
        Fetches and parses HTML content for each topic page.

        Returns:
            Dict[str, Optional[object]]: Dictionary containing BeautifulSoup objects for each topic

        Raises:
            CNNArticleFinderError: If no page content could be fetched
        """
        content = {}
        for topic in self.topics:
            for page in self.topic_pages:
                try:
                    base_scraper = BaseScraper(url=page)
                    page_soup = base_scraper.get_soup()
                    if not page_soup:
                        self.logger.warning(f"No soup content found for {page}")
                        continue
                    content[topic] = page_soup
                except Exception as e:
                    self.logger.error(f"Error fetching soup for {page}: {e}")
                    content[topic] = None
        
        if not content:
            raise CNNArticleFinderError("Failed to fetch any page content")
        return content

    def hyperlink_search(self) -> Dict[str, List[str]]:
        """
        Searches soup for hyperlinks.

        Returns:
            Dict[str, List[str]]: Dictionary containing article hyperlinks by topic

        Raises:
            ValueError: If page soup is not found
            CNNArticleFinderError: If element finding fails
        """
        soup = self.get_page_soup()
        if not soup:
            raise ValueError('Page soup could not be found')
        
        try:
            content = {}
            for topic, page in soup.items():
                if page is None:
                    self.logger.warning(f"Skipping hyperlink search for topic {topic} - no page content")
                    continue
                    
                div = page.find('div', class_='container_lead-plus-headlines__cards-wrapper')
                if div is None:
                    self.logger.warning(f"No headline wrapper found for topic {topic}")
                    continue
                    
                a_elements = div.find_all('a', href=True)
                href_values = [tag['href'] for tag in a_elements]
                content[topic] = href_values
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error in hyperlink search: {e}")
            raise CNNArticleFinderError(f"Failed to find hyperlinks: {e}") from e

    def get_link(self) -> Dict[str, List[str]]:
        """
        Converts extracted hyperlinks to accessible URLs.

        Returns:
            Dict[str, List[str]]: Dictionary of complete URLs by topic

        Raises:
            ValueError: If no hyperlinks are found
            CNNArticleFinderError: If hyperlinks cannot be processed
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
            raise CNNArticleFinderError(f"Failed to process hyperlinks: {e}") from e

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
        filename='cnn_article_finder.log',
        filemode='w'
    )
    
    # Example usage
    try:
        user_data = json.dumps({
            'topics': []
        })
        
        article_finder = CNNArticleFinder(
            url=CNNConfig.BASE_URL, 
            user_data=user_data
        )
        
        # Execute and log results
        logging.info(f"Selected topics: {article_finder.topics}")
        logging.info(f"Topic pages: {article_finder.topic_pages}")
        logging.info(f"Found hyperlinks: {article_finder.hyperlink_search()}")
        logging.info(f"Complete URLs: {article_finder.get_link()}")
        
    except CNNArticleFinderError as e:
        logging.error(f"Application error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    main() 