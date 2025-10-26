import requests
import json
from typing import Dict, Any

class YelpScraper:
    def __init__(self, token: str, yelp_url: str, bright_data_url: str):
        self.token = token
        self.yelp_url = yelp_url
        self.bright_data_url = bright_data_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    def scrape_reviews(self, unrecommended_reviews: bool, start_date: str = "2025-03-02T00:00:00.000Z", end_date: str = "2025-06-01T00:00:00.000Z", sort_by: str = "DATE_DESC") -> Dict[str, Any]:
        data = json.dumps({
            "input": [{"url":f"{self.yelp_url}",
                "unrecommended_reviews":unrecommended_reviews,
                "start_date":start_date,
                "end_date":end_date,
                "sort_by":sort_by
            }]
        })
        response = requests.post(
            self.bright_data_url,
            headers=self.headers,
            data=data
        )
        return response.json()