from typing import List

from pydantic import BaseModel

from ..definitions import KrameriusField


# TODO: move to Solr library
class SearchParams(BaseModel):
    query: str
    rows: int | None = None
    start: int | None = None
    fl: List[KrameriusField] | None = None
    fq: str | None = None
    sort: str | None = None
    cursorMark: str | None = None
    facet: bool | None = None
    facet_field: str | None = None
    facet_min_count: int | None = None

    def with_pagination(self):
        self.sort = "pid ASC"
        self.cursorMark = "*"
        return self

    def build(self):

        params = {"q": str(self.query)}
        for value, key in [
            (self.rows, "rows"),
            (self.start, "start"),
            (
                ",".join([fl.value for fl in self.fl]) if self.fl else None,
                "fl",
            ),
            (self.fq, "fq"),
            (self.sort, "sort"),
            (self.cursorMark, "cursorMark"),
            ("true" if self.facet else None, "facet"),
            (self.facet_field, "facet.field"),
            (self.facet_min_count, "facet.mincount"),
        ]:
            if value is not None:
                params[key] = value

        return params
