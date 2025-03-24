from solrify import Q, SolrClient, SolrConfig

from ..custom_types import KrameriusField, Pid
from ..schemas import KrameriusDocument


class SearchClient(SolrClient[KrameriusDocument]):
    def __init__(self, config: SolrConfig):
        super().__init__(config)

    def get_document(self, pid: Pid) -> KrameriusDocument | None:
        return super().get(Q(KrameriusField.Pid, pid))
