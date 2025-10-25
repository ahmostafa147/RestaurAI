import requests
import json
from typing import Dict, Any

class GoogleScraper:
    def __init__(self, token: str, google_map_url: str, bright_data_url: str):
        self.token = token
        self.google_map_url = google_map_url
        self.bright_data_url = bright_data_url
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
    def scrape_reviews(self, days_limit: int = 9) -> Dict[str, Any]:

        data = json.dumps({
            "input": [{"url":f"{self.google_map_url}","days_limit":days_limit}],
        })

        response = requests.post(
            self.bright_data_url,
            headers=self.headers,
            data=data
        )
        return response.json()