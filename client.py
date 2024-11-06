import requests
from lxml import etree
import os
from time import sleep
from typing import Any, Dict, Optional


WAIT_TIME = 15
kramerius_url = os.getenv("KRAMERIUS_API_URL")


class KrameriusClient:
    def __init__(self, base_url=kramerius_url):
        self.base_url = base_url
        self.curr_wait = 0
        self.retries = 0

    def get_response(self, url: str, params: Optional[Dict[str, Any]] = None):
        response = (
            requests.get(url)
            if params is None
            else requests.get(url, params=params)
        )

        if response.status_code != 200:
            if self.retries == 5:
                raise Exception(
                    f"Failed to get response from {url}"
                    f" after {self.retries} retries"
                )
            self.curr_wait += WAIT_TIME
            sleep(self.curr_wait)
            return self.get_response(url, params=params)

        self.curr_wait = 0
        self.retries = 0
        return response.json()

    def get_datastream(self, url: str):
        response = requests.get(url)

        if response.status_code != 200:
            if self.retries == 5:
                raise Exception(
                    f"Failed to get datastream from {url}"
                    f" after {self.retries} retries"
                )
            self.curr_wait += WAIT_TIME
            sleep(self.curr_wait)
            return self.get_datastream(url)

        self.curr_wait = 0
        self.retries = 0
        return etree.fromstring(response.content)

    def search(self, params: Dict[str, Any]):
        url = f"{self.base_url}/api/client/v7.0/search"
        return self.get_response(url, params=params)

    def get_mods(self, pid) -> Optional[etree._ElementTree]:
        url = f"{self.base_url}/api/client/v7.0/items/{pid}/metadata/mods"
        return self.get_datastream(url)
