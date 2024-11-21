import requests
from time import sleep
from ..datatypes import Method, Params
from typing import Any
import threading


DEFAULT_TIMEOUT = 15
DEFAULT_MAX_RETRIES = 5


class KrameriusBaseClient:
    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ):
        self.base_url = host.strip("/")
        self.username = username
        self.password = password

        self._token = None

        self.lock = threading.Lock()
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.max_retries = max_retries or DEFAULT_MAX_RETRIES

        self.retries = 0

    def _fetch_access_token(self):
        if not self.username or not self.password:
            raise ValueError(
                "Username and password must be provided to use admin API."
            )

        response = self._request(
            "POST",
            "/api/auth/token",
            data={"username": self.username, "password": self.password},
        )

        token = response.json().get("access_token")
        if token is None:
            raise ValueError("Failed to retrieve access token.")
        self._token = token

    def _wait_for_retry(self, response: requests.Response) -> None:
        if self.retries == 5:
            print(f"Failed to get response after {self.retries} retries")
            response.raise_for_status()
        self.retries += 1
        sleep(self.timeout * self.retries)

    def _request(
        self,
        method: Method,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
    ):
        url = self.base_url + endpoint

        response = requests.request(method, url, params=params, data=data)

        if (
            response.status_code == 403
            and "user 'not_logged'" in response.json().get("message", "")
        ):
            self._fetch_access_token()
            return self._request(method, endpoint, params=params, data=data)

        if response.status_code != 200:
            self._wait_for_retry(response)
            return self._request(method, endpoint, params=params, data=data)

        self.curr_wait = 0
        self.retries = 0
        return response

    def admin_request_response(
        self, method: str, endpoint: str, params: Params | None = None
    ):
        with self.lock:
            return self._request(
                method, f"/api/admin/v7.0/{endpoint}", params=params
            )

    def admin_request(
        self, method: str, endpoint: str, params: Params | None = None
    ):
        return self.admin_request_response(method, endpoint, params).json()

    def client_request_response(
        self, method: str, endpoint: str, params: Params | None = None
    ):
        with self.lock:
            return self._request(
                method, f"/api/client/v7.0/{endpoint}", params=params
            )

    def client_request(
        self, method: str, endpoint: str, params: Params | None = None
    ):
        return self.client_request_response(method, endpoint, params).json()
