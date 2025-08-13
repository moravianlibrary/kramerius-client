from solrify import SolrConfig

from ..schemas import KrameriusConfig
from .base import KrameriusBaseClient
from .items import ItemsClient
from .processing import ProcessingClient
from .sdnnt import SdnntClient
from .search import SearchClient
from .statistics import StatisticsClient

PAGINATE_PAGE_SIZE = 10000


class KrameriusClient:
    """
    High-level client interface for interacting with the Kramerius API.

    This client aggregates multiple functional API modules under
    a unified interface, allowing access to items, processing operations,
    SDNNT integration, search, and statistics through dedicated sub-clients.

    Parameters
    ----------
    config : KrameriusConfig
        Configuration object containing connection parameters
        and optional credentials for authentication (via Keycloak),
        timeout, and retry behavior.

    Attributes
    ----------
    Items : ItemsClient
        Sub-client for managing items (e.g., metadata, digital objects).
    Processing : ProcessingClient
        Sub-client for managing processes
        (e.g., reindexation, changing of licenses).
    Sdnnt : SdnntClient
        Sub-client for SDNNT integration.
    Search : SearchClient
        Sub-client for executing Solr search.
    Statistics : StatisticsClient
        Sub-client for retrieving Kramerius statistics.

    Notes
    -----
    - Internally uses `KrameriusBaseClient` to manage HTTP communication,
      authentication, and retry logic.
    - The `SearchClient` uses `solrify.SolrClient`
      with pagination configured via `PAGINATE_PAGE_SIZE`.
    - Thread-safe due to locking in the underlying base client.

    Examples
    --------
    >>> from kramerius_client import KrameriusClient, KrameriusConfig
    >>> client = KrameriusClient(
    >>>     KrameriusConfig(host="https://kramerius.example.org")
    >>> )
    >>> results = client.Search.query({"fulltext": "Masaryk"})
    >>> client.Items.get_metadata("uuid:1234")
    """

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
