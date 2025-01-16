import requests
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.google.com/',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    def fetch_html_content(self) -> bytes:
        """
        Fetches the HTML content of the specified URL.

        Returns:
            bytes: The HTML content of the response if successful.
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
        
    def get_soup(self):
        """
        Parses HTML content with BS4 and returns the BS4 object
        
        Returns:
            bs4.BeautifulSoup: The parsed HTML content of the response if successful.
            None: If an error occurs when the object is being created.      
        """
        # retrieve html content
        html_content = self.fetch_html_content()

        # if html content is None
        if not html_content:
            return None
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return soup
        except Exception as e:
            return None

if __name__ == '__main__':
    print('File has been excecuted properly')