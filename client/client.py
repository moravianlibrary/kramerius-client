from .items import ItemsClient
from .processing import ProcessingClient
from .search import SearchClient
from .base import KrameriusBaseClient
from .sdnnt import SdnntClient


class KrameriusClient:
    def __init__(
        self,
        host: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ):
        self._base = KrameriusBaseClient(
            host, username, password, timeout, max_retries
        )

        self.Items = ItemsClient(self._base)
        self.Processing = ProcessingClient(self._base)
        self.Search = SearchClient(self._base)
        self.Sdnnt = SdnntClient(self._base)
