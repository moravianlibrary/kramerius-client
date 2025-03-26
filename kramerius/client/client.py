from solrify import SolrConfig

from ..schemas import KrameriusConfig
from .base import KrameriusBaseClient
from .items import ItemsClient
from .processing import ProcessingClient
from .sdnnt import SdnntClient
from .search import SearchClient
from .statistics import StatisticsClient

PAGINATE_PAGE_SIZE = 100


class KrameriusClient:
    def __init__(self, config: KrameriusConfig):
        self._base = KrameriusBaseClient(config)

        self.Items = ItemsClient(self._base)
        self.Processing = ProcessingClient(self._base)
        self.Sdnnt = SdnntClient(self._base)
        self.Search = SearchClient(
            SolrConfig(
                host=config.host,
                endpoint="api/client/v7.0/search",
                id_field="pid",
                page_size=PAGINATE_PAGE_SIZE,
                timeout=config.timeout or 30,
            )
        )
        self.Statistics = StatisticsClient(self._base)
