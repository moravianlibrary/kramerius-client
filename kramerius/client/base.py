import threading
from os import path
from time import sleep
from typing import Any, Type, TypeVar

import requests
from lxml import etree
from pydantic import BaseModel

from kramerius.definitions.akubra import Xml

from ..definitions import Method, Params
from ..schemas import KrameriusConfig

TOKEN_TMP_FILE = "/tmp/kramerius_token"


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
    request_response(
        method, endpoint, params=None, data=None, data_type=None
    )
        Sends an authorized request to the admin API
        and returns the raw response.

    request(method, endpoint, params=None, data=None, data_type=None)
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
        self.config = config

        self._token = None
        if path.exists(TOKEN_TMP_FILE):
            with open(TOKEN_TMP_FILE, "r") as f:
                self._token = f.read().strip()

        self._lock = threading.Lock()

        self._current_attempt = 1

    def _fetch_service_account_token(self):
        """
        Fetches a new access token using service account credentials
        and writes it to a temporary file.

        Raises
        ------
        Exception
            If token retrieval fails.
        """

        response = requests.get(
            url=f"{self._host}/api/exts/v7.0/tokens/{self.config.client_id}",
            params={"secrets": self.config.service_account_secret},
            timeout=self.config.timeout,
        )

        if not response.ok:
            raise Exception("Failed to retrieve service account access token.")

        return response.json().get("access_token")

    def _fetch_user_access_token(self):
        """
        Fetches a new access token from the Keycloak server
        and writes it to a temporary file.

        Raises
        ------
        Exception
            If authorization parameters are not configured
            or token retrieval fails.
        """

        response = requests.post(
            url=(
                f"{self.config.keycloak_host}"
                "/realms/kramerius/protocol/openid-connect/token"
            ),
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "username": self.config.username,
                "password": self.config.password,
                "grant_type": "password",
            },
            timeout=self.config.timeout,
        )

        if not response.ok:
            raise Exception("Failed to retrieve user access token.")

        return response.json().get("access_token")

    def _fetch_access_token(self):
        """
        Fetches a new access token using either service account
        or user credentials.
        """
        if self.config.client_id and self.config.service_account_secret:
            token = self._fetch_service_account_token()
        elif (
            self.config.keycloak_host
            and self.config.client_id
            and self.config.client_secret
            and self.config.username
            and self.config.password
        ):
            token = self._fetch_user_access_token()
        else:
            raise Exception(
                "Authorization parameters are not provided. "
                "Please set them to use admin API.\n"
                "Required parameters are either:\n"
                "- client_id and service_account_secret "
                "for service account access\n"
                "or\n"
                "- keycloak_host, client_id, client_secret, "
                "username and password for user access."
            )

        self._token = token

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
        if response.status_code in [
            status for status in range(400, 500) if status not in [401, 403]
        ]:
            response.raise_for_status()

        if self._current_attempt > self.config.max_retries:
            response.raise_for_status()

        self._current_attempt += 1
        sleep(self.config.retry_timeout * self._current_attempt)

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
        headers = {} if (data_type and data) or self._token else None
        if data_type and data:
            headers["Content-Type"] = data_type
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = requests.request(
            method=method,
            url=f"{self.config.host}/{endpoint}",
            headers=headers,
            params=params,
            data=data,
        )

        if response.status_code == 401 or (
            response.status_code == 403
            and (
                "'not_logged'" in response.json().get("message", "")
                or "not allowed" in response.json().get("message", "")
            )
        ):
            self._fetch_access_token()
            return self._request(method, endpoint, params, data, data_type)

        if not response.ok:
            self._wait_for_retry(response)
            return self._request(method, endpoint, params, data, data_type)

        self._current_attempt = 1
        return response

    def request(
        self,
        method: Method,
        endpoint: str,
        params: Params | None = None,
        data: Any | None = None,
        data_type: str = "application/json",
    ):
        with self._lock:
            return self._request(method, endpoint, params, data, data_type)


AnyModel = TypeVar("AnyModel", bound=BaseModel)


def response_to_schema(
    response: requests.Response, schema: Type[AnyModel]
) -> AnyModel:
    return schema.model_validate(response.json())


def response_to_bytes(response: requests.Response) -> bytes:
    return response.content


def response_to_xml(response: requests.Response) -> Xml:
    return etree.fromstring(response.content)
