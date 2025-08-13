import threading
from os import path
from time import sleep
from typing import Any

import requests

from ..definitions import Method, Params
from ..schemas import KrameriusConfig

DEFAULT_TIMEOUT = 30

TOKEN_TMP_FILE = "/tmp/kramerius_token"
KEYCLOAK_TOKEN_ENDPOINT = "/realms/kramerius/protocol/openid-connect/token"

DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_TIMEOUT = 15
DEFAULT_MAX_ACTIVE_PROCESSES = 2


class KrameriusBaseClient:
    """
    Base client for interacting with the Kramerius API.

    Handles token-based authentication via Keycloak, request retries,
    and basic request routing for both admin and client API endpoints.

    All requests are synchronized using a thread lock (`threading.Lock`)
    to ensure that only one request is in progress at a time. This avoids:
        - race conditions when accessing or refreshing tokens,
        - overlapping retry logic from multiple threads,
        - inconsistent side effects when issuing write operations.

    This makes the client safe for use in multi-threaded environments
    where requests may be sent concurrently.

    Parameters
    ----------
    config : KrameriusConfig
        Configuration object containing API host, credentials,
        and optional timeout and retry settings.

    Methods
    -------
    admin_request_response(
        method, endpoint, params=None, data=None, data_type=None
    )
        Sends an authorized request to the admin API
        and returns the raw response.

    admin_request(method, endpoint, params=None, data=None, data_type=None)
        Sends an authorized request to the admin API
        and returns the parsed JSON response.

    client_request_response(
        method, endpoint, params=None, data=None, data_type=None
    )
        Sends an authorized request to the client API
        and returns the raw response.

    client_request(method, endpoint, params=None, data=None, data_type=None)
        Sends an authorized request to the client API
        and returns the parsed JSON response.
    """

    def __init__(
        self,
        config: KrameriusConfig,
    ):
        self._host = config.host.strip("/")

        self._keycloak_host = None
        self._get_token_body = None
        if (
            config.keycloak_host
            and config.client_id
            and config.client_secret
            and config.username
            and config.password
        ):
            self._keycloak_host = config.keycloak_host.strip("/")
            self._get_token_body = {
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "username": config.username,
                "password": config.password,
                "grant_type": "password",
            }

        self._timeout = config.timeout or DEFAULT_TIMEOUT

        self._token = None
        if path.exists(TOKEN_TMP_FILE):
            with open(TOKEN_TMP_FILE, "r") as f:
                self._token = f.read().strip()

        self._lock = threading.Lock()

        self._max_retries = config.max_retries or DEFAULT_MAX_RETRIES
        self._retry_timeout = config.timeout or DEFAULT_RETRY_TIMEOUT
        self._retries = 0

        self._max_active_processes = (
            config.max_active_processes or DEFAULT_MAX_ACTIVE_PROCESSES
        )

    def _fetch_access_token(self):
        """
        Fetches a new access token from the Keycloak server
        and writes it to a temporary file.

        Raises
        ------
        Exception
            If authorization parameters are not configured
            or token retrieval fails.
        """

        if self._get_token_body is None:
            raise Exception(
                "Authorization parameters are not provided. "
                "Please set them to use admin API."
            )

        response = requests.post(
            url=f"{self._keycloak_host}/{KEYCLOAK_TOKEN_ENDPOINT}",
            data=self._get_token_body,
            timeout=self._timeout,
        )

        if not response.ok:
            raise Exception("Failed to retrieve access token.")

        self._token = response.json().get("access_token")

        with open(TOKEN_TMP_FILE, "w+") as f:
            f.write(self._token)

    def _wait_for_retry(self, response: requests.Response) -> None:
        """
        Waits before retrying a failed request based on exponential backoff.

        Parameters
        ----------
        response : requests.Response
            The HTTP response object triggering the retry.

        Raises
        ------
        requests.HTTPError
            If the maximum number of retries is exceeded.
        """
        if self._retries == 5:
            response.raise_for_status()
        self._retries += 1
        sleep(self._retry_timeout * self._retries)

    def _request(
        self,
        method: Method,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
        data_type: str | None = None,
    ):
        """
        Internal request handler with retry and token refresh logic.

        Parameters
        ----------
        method : Method
            HTTP method (e.g., 'GET', 'POST').
        endpoint : str
            API endpoint relative to the host.
        params : dict, optional
            Query parameters.
        data : Any, optional
            Request body.
        data_type : str, optional
            Content type (e.g., 'application/json').

        Returns
        -------
        requests.Response
            The final response object after retries or token refresh.
        """
        headers = {} if data_type or self._token else None
        if data_type:
            headers["Content-Type"] = data_type
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = requests.request(
            method=method,
            url=f"{self._host}/{endpoint}",
            headers=headers,
            params=params,
            data=data,
        )

        if response.status_code == 401 or (
            response.status_code == 403
            and (
                "user 'not_logged'" in response.json().get("message", "")
                or "not allowed" == response.json().get("message", "")
            )
        ):
            self._fetch_access_token()
            return self._request(method, endpoint, params, data, data_type)

        if not response.ok:
            self._wait_for_retry(response)
            return self._request(method, endpoint, params, data, data_type)

        self._retries = 0
        return response

    def admin_request_response(
        self,
        method: str,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
        data_type: str | None = None,
    ):
        """
        Sends a request to the admin API and returns the raw response.

        Parameters
        ----------
        method : str
            HTTP method.
        endpoint : str
            Admin API endpoint.
        params : dict, optional
            Query parameters.
        data : Any, optional
            Request payload.
        data_type : str, optional
            Content type.

        Returns
        -------
        requests.Response
            Raw HTTP response.
        """
        with self._lock:
            return self._request(
                method, f"api/admin/v7.0/{endpoint}", params, data, data_type
            )

    def admin_request(
        self,
        method: str,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
        data_type: str | None = None,
    ):
        """
        Sends a request to the admin API and returns the JSON-decoded response.

        Parameters
        ----------
        method : str
            HTTP method.
        endpoint : str
            Admin API endpoint.
        params : dict, optional
            Query parameters.
        data : Any, optional
            Request payload.
        data_type : str, optional
            Content type.

        Returns
        -------
        dict
            JSON-decoded response.
        """
        return self.admin_request_response(
            method, endpoint, params, data, data_type
        ).json()

    def client_request_response(
        self,
        method: str,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
        data_type: str | None = None,
    ):
        """
        Sends a request to the client API and returns the raw response.

        Parameters
        ----------
        method : str
            HTTP method.
        endpoint : str
            Client API endpoint.
        params : dict, optional
            Query parameters.
        data : Any, optional
            Request payload.
        data_type : str, optional
            Content type.

        Returns
        -------
        requests.Response
            Raw HTTP response.
        """
        with self._lock:
            return self._request(
                method, f"api/client/v7.0/{endpoint}", params, data, data_type
            )

    def client_request(
        self,
        method: str,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
        data_type: str | None = None,
    ):
        """
        Sends a request to the client API
        and returns the JSON-decoded response.

        Parameters
        ----------
        method : str
            HTTP method.
        endpoint : str
            Client API endpoint.
        params : dict, optional
            Query parameters.
        data : Any, optional
            Request payload.
        data_type : str, optional
            Content type.

        Returns
        -------
        dict
            JSON-decoded response.
        """
        return self.client_request_response(
            method, endpoint, params, data, data_type
        ).json()
