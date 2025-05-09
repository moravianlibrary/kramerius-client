from typing import List

from pydantic import BaseModel, Field

from ..custom_types import Accessibility, License, Model


class KrameriusDocument(BaseModel):
    pid: str | None = None
    parent_pid: str | None = Field(None, alias="own_parent.pid")
    root_pid: str | None = Field(None, alias="root.pid")
    own_pid_path: str | None = None

    model: Model | None = None
    parent_model: Model | None = Field(None, alias="own_parent.model")
    root_model: Model | None = Field(None, alias="root.model")
    model_path: str | None = Field(None, alias="own_model_path")
    level: int | None = None

    in_collections: List[str] | None = None
    direct_in_collections: List[str] | None = Field(
        None, alias="in_collections.direct"
    )
    licenses: List[License] | None = None
    contains_licenses: List[License] | None = None
    licenses_of_ancestors: List[License] | None = None
    accessibility: Accessibility | None = None

    system_number: List[str] | None = Field(None, alias="id_sysno")
    barcode: List[str] | None = Field(None, alias="id_barcode")
    nbn: List[str] | None = Field(None, alias="id_ccnb")
    isbn: List[str] | None = Field(None, alias="id_isbn")
    issn: List[str] | None = Field(None, alias="id_issn")
    signature: List[str] | None = Field(None, alias="shelf_locators")
    physical_location: List[str] | None = Field(
        None, alias="physical_locations.facet"
    )

    @property
    def isxn(self) -> str | None:
        return self.isbn or self.issn

    date_min: str | None = Field(None, alias="date.min")
    date_max: str | None = Field(None, alias="date.max")
    date_range_start_year: int | None = Field(
        None, alias="date_range_start.year"
    )
    date_range_end_year: int | None = Field(None, alias="date_range_end.year")

    title: str | None = Field(None, alias="title.search")
    title_sort: str | None = Field(None, alias="title.sort")
    part_number_sort: int | None = Field(None, alias="part.number.sort")
    part_number_string: str | None = Field(None, alias="part.number.str")

    publishers_facet: List[str] | None = Field(None, alias="publishers.facet")
    publication_places_facet: List[str] | None = Field(
        None, alias="publication_places.facet"
    )
    languages_facet: List[str] | None = Field(None, alias="languages.facet")

    page_count: int | None = Field(None, alias="count_page")

    keywords_facet: List[str] | None = Field(None, alias="keywords.facet")
    image_full_mime_type: str | None = Field(None, alias="ds.img_full.mime")
