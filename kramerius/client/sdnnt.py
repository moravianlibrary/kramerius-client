from datetime import datetime, timezone

from ..schemas import (
    SdnntGranularityRecord,
    SdnntGranularityResponse,
    SdnntResponse,
)
from .base import (
    KrameriusBaseClient,
    response_to_schema,
    response_to_schema_list,
)

PAGE_SIZE = 100


class SdnntClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def get_sdnnt_timestamp(self, tzinfo=timezone.utc) -> datetime | None:
        timestamp = (
            self._client.request("GET", "api/admin/v7.0/sdnnt/sync/timestamp")
            .get("docs")[0]
            .get("fetched")
        )
        return (
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=tzinfo
            )
            if timestamp
            else None
        )

    def get_sdnnt_changes(self, page: int, rows: int) -> SdnntResponse:
        return response_to_schema(
            self._client.request(
                "GET", f"api/admin/v7.0/sdnnt/sync?rows={rows}&page={page}"
            ),
            SdnntResponse,
        )

    def iterate_sdnnt_changes(self):
        page = 0
        num_found = self.get_sdnnt_changes(page, 0).numFound

        while page * PAGE_SIZE < num_found:
            response = self.get_sdnnt_changes(page, PAGE_SIZE)
            for doc in response.docs:
                yield doc
            page += 1

    def get_sdnnt_granularity(self, id: str) -> SdnntGranularityResponse:
        return response_to_schema_list(
            self._client.request(
                "GET", f"api/admin/v7.0/sdnnt/sync/granularity/{id}"
            ),
            SdnntGranularityRecord,
            items_key=id,
        )
