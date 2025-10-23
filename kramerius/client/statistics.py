from ..schemas import SearchParams
from .base import KrameriusBaseClient


class StatisticsClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def search(self, search_params: SearchParams):
        return self._client.request(
            "GET",
            "api/admin/v7.0/statistics/search",
            params=search_params.build(),
        )
