from kramerius.definitions.akubra import Xml

from .base import KrameriusBaseClient, response_to_bytes, response_to_xml


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
