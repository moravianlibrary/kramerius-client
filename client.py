import requests
from lxml import etree
from time import sleep
from typing import Any, Dict, Optional


DEFAULT_TIMEOUT = 15
DEFAULT_MAX_RETRIES = 5


class KrameriusClient:
    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.base_url = host
        self.username = username
        self.password = password

        self.timeout = timeout
        self.max_retries = max_retries

        self.retries = 0

    def _wait_for_retry(self, response: requests.Response) -> None:
        if self.retries == 5:
            print(f"Failed to get response after {self.retries} retries")
            response.raise_for_status()
        self.retries += 1
        sleep(self.timeout * self.retries)

    def get_response(self, url: str, params: Optional[Dict[str, Any]] = None):
        response = (
            requests.get(url)
            if params is None
            else requests.get(url, params=params)
        )

        if response.status_code != 200:
            self._wait_for_retry(response)
            return self.get_response(url, params=params)

        self.curr_wait = 0
        self.retries = 0
        return response.json()

    def get_datastream(self, url: str):
        response = requests.get(url)

        if response.status_code != 200:
            self._wait_for_retry(url)
            if self.retries == 5:
                raise Exception(
                    f"Failed to get datastream from {url}"
                    f" after {self.retries} retries"
                )
            self.curr_wait += self.timeout
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
