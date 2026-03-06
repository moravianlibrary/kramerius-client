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

    def get_ocr_text(self, pid: str) -> str:
        """
        Retrieves OCR text as string, no editing from source.
        :param pid: uuid
        :return: string of OCR text
        """
        response: requests.Response = self._client.request(
            "GET",
            f"api/client/v7.0/items/{pid}/ocr/text",
            data_type="text/plain",
        )
        if response.status_code != 200:
            raise HTTPError(f"{response.status_code}: {response.text}")
        return response.text

    def get_ocr_text_all_child_pages(self, pid: str) -> str:
        """
        Retrieves and concatenates OCR from children of :param pid: . Each page concatenated with a newline. If a child of :param pid: does not have ocr a warning message is printed but the process does not fail.
        :param pid: uuid
        :return: string of OCR texts
        """
        children = self.get_children(pid)
        text: str = ""
        for child in children:
            try:
                child_text = self.get_ocr_text(child['pid'])
            except HTTPError:
                print(f"Child {child['pid']} isn't a page or just doesn't have OCR")
                continue
            text += child_text + '\n'

        if text == "":
            print(f"FINAL: Document {pid} doesn't have pages or none of them had OCR")
        return text


    def get_foxml_full(self, pid: str) -> Xml:
        """
        Retrieves full admin foxml of document
        :param pid: uuid
        :return: Xml structure
        :raises: HTTPError on responses other than code 200
        """
        response: requests.Response = self._client.request(
            "GET",
            f"api/admin/v7.0/items/{pid}/foxml",
        )
        if response.status_code != 200:
            raise HTTPError(f"{response.status_code}: {response.text}")
        return response_to_xml(response)

    def get_imageserver_location_full(self, pid: str) -> str:
        """
        Retrieves location of IMG_FULL scan
        :param pid: uuid
        :return: str http address on imageserver
        :raises: HTTPError on responses other than code 200
        """
        ds_id = "IMG_FULL"
        response: requests.Response = self._client.request(
            "GET",
            f"api/admin/v7.0/repository/getDatastreamMetadata?pid={pid}&dsId={ds_id}",
        )
        if response.status_code != 200:
            raise HTTPError(f"{response.status_code}: {response.text}")
        return response.json()["location"]
