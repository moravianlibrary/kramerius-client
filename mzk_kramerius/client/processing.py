from ..datatypes import ProcessType
from ..schemas import KrameriusProcess, ProcessParams, EmptyParams
from .base import KrameriusBaseClient


class ProcessingClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def plan(
        self, type: ProcessType, params: ProcessParams = EmptyParams
    ) -> KrameriusProcess:
        return self._client.admin_request("POST", "processes", params=params)
