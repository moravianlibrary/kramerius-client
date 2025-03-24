from typing import List

from solrify import Q, SearchBase, SolrClient, SolrConfig

from ..custom_types import KrameriusField, Pid
from ..schemas import KrameriusDocument


class SearchClient:
    def __init__(self, config: SolrConfig):
        self._client = SolrClient(config)

    def get_document(self, pid: Pid) -> KrameriusDocument | None:
        return self._client.get(Q(KrameriusField.Pid, pid))

    def num_found(self, query: SearchBase) -> int:
        return self._client.num_found(query)

    def search(
        self, query: SearchBase, fl: List[KrameriusField] | None = None
    ):
        for document in self._client.search(query, "pid asc", fl):
            yield document
