from solrify import F, SolrClient, SolrConfig

from ..definitions import KrameriusField, Pid
from ..schemas import KrameriusDocument


class SearchClient(SolrClient[KrameriusDocument]):
    document_type = KrameriusDocument

    def __init__(self, config: SolrConfig):
        super().__init__(config)

    def get_document(self, pid: Pid) -> KrameriusDocument | None:
        return super().get_one_or_none(F(KrameriusField.Pid, pid))
