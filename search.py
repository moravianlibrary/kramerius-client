from __future__ import annotations
from enum import Enum
from typing import List, Optional, Tuple, Union
from pydantic import BaseModel
from .client import KrameriusClient
from .document import KrameriusDocument
from .types import SolrConjuction, Field


START_CURSOR_MARK = "*"
PAGINATE_PAGE_SIZE = 100
# PAGINATE_PAGE_SIZE = 1000

SolrValue = Union[str, int, float, List, Tuple, Enum]


class KrameriusSearch:
    def __init__(self, client: KrameriusClient):
        self.client = client

    def get_document(self, pid):
        params = SearchParams().with_rows(1).with_query(base_(Field.Pid, pid))
        response = self.client.search(params.build())
        return (
            KrameriusDocument(response["response"]["docs"][0])
            if response["response"]["numFound"] > 0
            else None
        )

    def num_found(self, query: SearchQuery | str):
        params = SearchParams().with_query(query).with_rows(0)
        return self.client.search(params.build())["response"]["numFound"]

    def search(
        self, query: SearchQuery | str, fl: Optional[List[Field]] = None
    ):
        params = (
            SearchParams()
            .with_query(query)
            .with_rows(PAGINATE_PAGE_SIZE)
            .with_fl(fl)
        )
        numFound = self.num_found(query)
        if numFound <= PAGINATE_PAGE_SIZE:
            for document in self.client.search(params.build())["response"][
                "docs"
            ]:
                yield KrameriusDocument(document)
            return

        params = params.with_pagination()
        while True:
            response = self.client.search(params.build())

            for document in response["response"]["docs"]:
                yield KrameriusDocument(document)

            numFound = response["response"]["numFound"]
            nextCursorMark = response["nextCursorMark"]

            if nextCursorMark == params.cursorMark:
                break
            params.with_cursor_mark(nextCursorMark)


class SearchParams:
    def __init__(self):
        self.query = "*"
        self.rows = 10
        self.start = 0
        self.fl: Optional[List[Field]] = None
        self.fq = None
        self.sort = None
        self.cursorMark = None

    def with_query(self, query):
        self.query = query
        return self

    def with_rows(self, rows):
        self.rows = rows
        return self

    def with_start(self, start):
        self.start = start
        return self

    def with_fl(self, fl: List[Field]):
        self.fl = fl
        return self

    def with_fq(self, fq):
        self.fq = fq
        return self

    def with_pagination(self):
        self.sort = "pid ASC"
        self.cursorMark = START_CURSOR_MARK
        return self

    def with_cursor_mark(self, cursorMark):
        self.cursorMark = cursorMark
        return self

    def build(self):
        return {
            "q": (
                self.query.build()
                if isinstance(self.query, SearchQuery)
                else self.query
            ),
            "rows": self.rows,
            "start": self.start,
            "fl": ",".join([fl.value for fl in self.fl]) if self.fl else None,
            "fq": self.fq,
            "cursorMark": self.cursorMark,
            "sort": self.sort,
        }


class SearchQuery(BaseModel):
    field: Field | None = None
    value: SolrValue | None = None
    list_conjunction: SolrConjuction | None = None
    not_subquery: Optional["SearchQuery"] = None
    sub_queries: List["SearchQuery"] | None = None
    conjuctions: List[SolrConjuction] | None = None

    def _append_part(
        self, conjuction: SolrConjuction, part: "SearchQuery"
    ) -> "SearchQuery":
        if not self.sub_queries:
            return SearchQuery(
                sub_queries=[self, part], conjuctions=[conjuction]
            )
        self.conjuctions.append(conjuction)
        self.sub_queries.append(part)
        return self

    def _has_multiple_subqueries(self) -> bool:
        return self.sub_queries is not None and len(self.sub_queries) > 1

    @classmethod
    def _parse_args(cls, *args) -> "SearchQuery":
        if len(args) == 1 and isinstance(args[0], SearchQuery):
            return args[0]
        elif len(args) == 2:
            field, value = args
            return SearchQuery(
                field=field, value=value, list_conjunction=SolrConjuction.And
            )
        elif len(args) == 3:
            field, value, list_conjunction = args
            return SearchQuery(
                field=field, value=value, list_conjunction=list_conjunction
            )
        else:
            raise ValueError(
                "Invalid arguments: pass either a SearchQuery, "
                "a field and value pair, "
                "or a field, value, and list_conjunction triplet."
            )

    @classmethod
    def base_(cls, *args) -> "SearchQuery":
        return cls._parse_args(*args)

    @classmethod
    def not_(cls, *args) -> "SearchQuery":
        subquery = cls._parse_args(*args)
        return cls(not_subquery=subquery)

    def and_(self, *args) -> "SearchQuery":
        subquery = self._parse_args(*args)
        return self._append_part(SolrConjuction.And, subquery)

    def or_(self, *args) -> "SearchQuery":
        subquery = self._parse_args(*args)
        return self._append_part(SolrConjuction.Or, subquery)

    def _parse_value(self, value: SolrValue) -> str:
        if isinstance(value, str):
            return f'"{value}"' if value != "*" else value
        elif isinstance(value, Enum):
            return f'"{value.value}"'
        elif isinstance(value, list):
            if not value:
                raise ValueError("List values cannot be empty.")
            if not all(isinstance(v, (str, int, float, Enum)) for v in value):
                raise TypeError(
                    "List values must be of type str, int, float, or Enum."
                )
            if not self.list_conjunction:
                raise ValueError(
                    "List conjunction must be provided for list values."
                )
            return f"({self.list_conjunction.value.join(
                [self._parse_value(v) for v in value]
            )})"
        elif isinstance(value, tuple) and len(value) == 2:
            value_1 = self._parse_value(value[0])
            value_2 = self._parse_value(value[1])
            return f"[{value_1} TO {value_2}]"
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        raise TypeError(f"Unsupported value type: {type(value)}")

    def build(self) -> str:
        if self.not_subquery is not None:
            return (
                f"-{self.not_subquery.build()}"
                if not self.not_subquery._has_multiple_subqueries()
                else f"-({self.not_subquery.build()})"
            )
        if self.sub_queries:
            parts = [
                (
                    sub.build()
                    if not sub._has_multiple_subqueries()
                    else f"({sub.build()})"
                )
                for sub in self.sub_queries
            ]
            return f"{self.conjuctions[0].value}".join(parts)
        if self.field is not None and self.value is not None:
            return f"{self.field.value}:{self._parse_value(self.value)}"
        raise ValueError("Invalid query structure.")


def base_(*args) -> SearchQuery:
    return SearchQuery.base_(*args)


def not_(*args) -> SearchQuery:
    return SearchQuery.not_(*args)
