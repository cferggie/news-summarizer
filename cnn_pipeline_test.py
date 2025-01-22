from cnn_article_finder import CNNArticleFinder
from cnn_scraper import CNNScraper
import json
from logger import setup_logger

def main():
    # setup logger
    # logger is inside the function to keep the module name as cnn_pipeline_test
    logger = setup_logger(__name__)
    
    user_data = json.dumps({
        'topics': ['US']
    })
    
    cnn_article_finder = CNNArticleFinder(user_data)
    links = cnn_article_finder.get_link() #dict {topic: [link1, link2, ...]}

    for topic, link_list in links.items():
        for link in link_list:
            print(f"Link: {link}")
            try:  
                cnn_scraper = CNNScraper(link)
                headline, article_body = cnn_scraper.get_article_data()
                logger.info(f"Headline: {headline}")
                logger.info(f"Article Body: found")
            except Exception as e:
                logger.error(f"Error: {e}") 
                logger.error(f"Link: {link}")   

if __name__ == "__main__":
    main()
