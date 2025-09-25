from typing import List

from lxml import etree

from ..definitions.akubra import FoxmlExportFormat, Xml
from ..schemas.akubra import (
    AcknowledgeDsId,
    AcknowledgePid,
    DatastreamMetadata,
    DatastreamNames,
    Literal,
    Literals,
    ObjectMetadata,
    Relation,
    Relations,
)
from .base import KrameriusBaseClient


class AkubraClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def export(self, pid: str, format: FoxmlExportFormat) -> Xml:
        return self._client.parse_xml(
            self._client._request(
                "GET",
                "api/admin/v7.0/repository/export",
                {"pid": pid, "format": format.value},
            )
        )

    def get_metadata(self, pid: str) -> ObjectMetadata:
        return self._client.parse_schema(
            self._client._request(
                "GET",
                f"api/admin/v7.0/repository/objects/{pid}/meta",
            ),
            ObjectMetadata,
        )

    def get_ds_content(self, pid: str, dsid: str) -> bytes:
        return self._client.parse_bytes(
            self._client._request(
                "GET",
                "api/admin/v7.0/repository/getDatastreamContent",
                {"pid": pid, "dsId": dsid},
            )
        )

    def get_ds_xml_content(self, pid: str, dsid: str) -> Xml:
        return self._client.parse_xml(
            self._client._request(
                "GET",
                "api/admin/v7.0/repository/getDatastreamContent",
                {"pid": pid, "dsId": dsid},
            )
        )

    def get_ds_metadata(self, pid: str, dsid: str) -> DatastreamMetadata:
        return self._client.parse_schema(
            self._client._request(
                "GET",
                "api/admin/v7.0/repository/getDatastreamMetadata",
                {"pid": pid, "dsId": dsid},
            ),
            DatastreamMetadata,
        )

    def get_ds_names(self, pid: str) -> List[str]:
        return self._client.parse_schema(
            self._client._request(
                "GET",
                f"api/admin/v7.0/repository/datastreams/{pid}",
            ),
            DatastreamNames,
        ).datastreams

    def get_relations(self, pid: str) -> List[Relation]:
        return self._client.parse_schema(
            self._client._request(
                "GET",
                "api/admin/v7.0/repository/getRelations",
                {"pid": pid},
            ),
            Relations,
        ).relations

    def get_literals(self, pid: str) -> List[Literal]:
        return self._client.parse_schema(
            self._client._request(
                "GET",
                "api/admin/v7.0/repository/getLiterals",
                {"pid": pid},
            ),
            Literals,
        ).literals

    def ingest(self, foxml: Xml) -> str:
        return self._client.parse_schema(
            self._client._request(
                "POST",
                "api/admin/v7.0/repository/ingest",
                data=etree.tostring(foxml, encoding="utf-8"),
                data_type="application/xml",
            ),
            AcknowledgePid,
        ).pid

    def purge(self, pid: str) -> bool:
        return (
            self._client.parse_schema(
                self._client._request(
                    "DELETE",
                    f"api/admin/v7.0/repository/objects/{pid}",
                ),
                AcknowledgePid,
            ).pid
            == pid
        )

    def create_xml_stream(
        self,
        pid: str,
        dsid: str,
        xml: Xml,
        mime_type: str = "application/rdf+xml",
    ) -> bool:
        return (
            self._client.parse_schema(
                self._client._request(
                    "POST",
                    "api/admin/v7.0/repository/createXMLDatastream",
                    params={
                        "pid": pid,
                        "dsId": dsid,
                        "mimeType": mime_type,
                    },
                    data=etree.tostring(
                        xml, encoding="utf-8", xml_declaration=True
                    ),
                    data_type="application/octet-stream",
                ),
                AcknowledgeDsId,
            ).dsid
            == dsid
        )

    def create_managed_stream(
        self,
        pid: str,
        dsid: str,
        content: bytes,
        mime_type: str,
    ) -> bool:
        return (
            self._client.parse_schema(
                self._client._request(
                    "POST",
                    "api/admin/v7.0/repository/createManagedDatastream",
                    params={
                        "pid": pid,
                        "dsId": dsid,
                        "mimeType": mime_type,
                    },
                    data=content,
                    data_type=mime_type,
                ),
                AcknowledgeDsId,
            ).dsid
            == dsid
        )

    def create_external_stream(
        self,
        pid: str,
        dsid: str,
        location: str,
        mime_type: str,
    ) -> bool:
        return (
            self._client.parse_schema(
                self._client._request(
                    "POST",
                    "api/admin/v7.0/repository/createExternalDatastream",
                    params={
                        "pid": pid,
                        "dsId": dsid,
                        "mimeType": mime_type,
                        "url": location,
                    },
                ),
                AcknowledgeDsId,
            ).dsid
            == dsid
        )

    def purge_stream(self, pid: str, dsid: str) -> bool:
        return (
            self._client.parse_schema(
                self._client._request(
                    "DELETE",
                    "api/admin/v7.0/repository/deleteDatastream",
                    {"pid": pid, "dsId": dsid},
                ),
                AcknowledgeDsId,
            ).dsid
            == dsid
        )
