from requests import HTTPError

from kramerius.definitions.akubra import Xml

from .base import KrameriusBaseClient, response_to_bytes, response_to_xml
import requests


class ItemsClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def get_mods(self, pid) -> Xml:
        return response_to_xml(
            self._client.request(
                "GET",
                f"api/client/v7.0/items/{pid}/metadata/mods",
            )
        )

    def get_image(self, pid: str) -> bytes:
        return response_to_bytes(
            self._client.request(
                "GET",
                f"api/client/v7.0/items/{pid}/image",
                data_type="image/jpeg",
            )
        )

    def get_children(self, pid: str) -> list[dict[str, str]]:
        response: requests.Response = self._client.request(
            "GET",
            f"api/client/v7.0/items/{pid}/info/structure",
        )
        return response.json()["children"]["own"]

    def get_item_model(self, pid: str) -> str:
        response: requests.Response = self._client.request(
            "GET",
            f"api/client/v7.0/items/{pid}/info/structure",
        )
        return response.json()["model"]

    def get_foxml_full(self, pid: str) -> Xml:
        response: requests.Response = self._client.request(
            "GET",
            f"api/admin/v7.0/items/{pid}/info/structure",
            # data_type="application/xml",
        )
        if response.status_code != 200:
            raise HTTPError(f"{response.status_code}: {response.text}")
        return response_to_xml(response)

    def get_imageserver_location_full(self, pid: str) -> str:
        ds_id = "IMG_FULL"
        response: requests.Response = self._client.request(
            "GET",
            f"api/admin/v7.0/repository/getDatastreamMetadata?pid={pid}&dsId={ds_id}",
        )
        if response.status_code != 200:
            raise HTTPError(f"{response.status_code}: {response.text}")
        return response.json()["location"]
