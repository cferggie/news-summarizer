import requests
from bs4 import BeautifulSoup

# Replace with your API key and endpoint
url = "http://localhost:11434/api/generate"

def summarize_text(paragraph):

    data = {
        "model": "deepseek-r1",
        "prompt": paragraph ,
        # "text": paragraph,
        "system": """
        The user will provide text. The response should ingest the paragraph and provide an unbiased summary of the text. 
        Begin each response with Unbiased Summary:""",
        
        "stream": False
    }

    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response')
            return summary
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f'An error occured: {e}')
        return None

# Example paragraph to summarize
paragraph = """

The rapid advancements in artificial intelligence (AI) have reshaped numerous industries,
ranging from healthcare to transportation. Machine learning algorithms now aid in diagnosing diseases,
autonomous vehicles navigate roads with impressive accuracy, and personalized recommendations enhance
user experiences in e-commerce and entertainment. Despite these benefits, challenges like ethical considerations,
data privacy concerns, and potential biases in AI systems require ongoing attention.
"""

summary = summarize_text(paragraph)
print(summary)