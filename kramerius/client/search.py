from solrify import F, SolrClient, SolrConfig

from ..definitions import KrameriusField, Pid
from ..schemas import KrameriusDocument


class SearchClient(SolrClient[KrameriusDocument]):
    document_type = KrameriusDocument

    def __init__(self, config: SolrConfig):
        super().__init__(config)

    def get_document(self, pid: Pid) -> KrameriusDocument | None:
        return super().get_one_or_none(F(KrameriusField.Pid, pid))

    def get_children(self, pid: Pid, fields: list[str] | None = None, sort: KrameriusField | None = None) -> list[KrameriusDocument]:
        """
        Solr search for documents with pid as its parent.
        :param pid: uuid of document
        :param fields: list of fields to return, optional
        :param sort: sort fields by, optional
        :return: List od KrameriusDocument, sorted by field ascending
        """
        l: list[KrameriusDocument] = list(super().search(F(KrameriusField.ParentPid, pid), fl=fields))
        return sorted(l,key=lambda doc: doc.model_dump(by_alias=True)[sort.value]) if sort else l
