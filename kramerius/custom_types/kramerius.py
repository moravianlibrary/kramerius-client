import uuid
from enum import Enum
from typing import Any, Dict, Literal

from pydantic import AfterValidator
from solrify import MappingEnum
from typing_extensions import Annotated

Method = Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"]
type Params = Dict[str, Any]


def validate_pid(pid: str) -> str:
    try:
        uuid_ = pid[5:] if pid.startswith("uuid:") else pid
        uuid.UUID(uuid_)
        return f"uuid:{uuid_}"
    except ValueError:
        raise ValueError("Invalid UUID format")


Pid = Annotated[
    str,
    AfterValidator(lambda x: validate_pid(x)),
]


class KrameriusField(MappingEnum):
    Pid = "pid"
    ParentPid = "own_parent.pid"
    RootPid = "root.pid"
    OwnPidPath = "own_pid_path"

    Model = "model"
    ParentModel = "own_parent.model"
    RootModel = "root.model"
    ModelPath = "own_model_path"
    Level = "level"

    InCollections = "in_collections"
    DirectInCollections = "in_collections.direct"
    Licenses = "licenses"
    ContainsLicenses = "contains_licenses"
    AncestralLicenses = "licenses_of_ancestors"
    Accessibility = "accessibility"

    Barcode = "id_barcode"
    SystemNumber = "id_sysno"
    Nbn = "id_ccnb"
    Isbn = "id_isbn"
    Issn = "id_issn"
    Signature = "shelf_locators"
    PhysicalLocation = "physical_locations.facet"

    DateStr = "date.str"
    DateMin = "date.min"
    DateMax = "date.max"
    DateRangeStartYear = "date_range_start.year"
    DateRangeEndYear = "date_range_end.year"

    Title = "title.search"
    TitleSort = "title.sort"
    Titles = "titles.search"
    PartNumberSort = "part.number.sort"
    PartNumberString = "part.number.str"

    PublishersFacet = "publishers.facet"
    PublicationPlacesFacet = "publication_places.facet"

    LanguagesFacet = "languages.facet"

    PageCount = "count_page"

    KeywordsFacet = "keywords.facet"
    ImageFullMimeType = "ds.img_full.mime"


class Model(Enum):
    Periodical = "periodical"
    PeriodicalVolume = "periodicalvolume"
    PeriodicalItem = "periodicalitem"
    Supplement = "supplement"
    Article = "article"
    Monograph = "monograph"
    MonographUnit = "monographunit"
    Page = "page"
    Sheetmusic = "sheetmusic"
    Convolute = "convolute"
    Collection = "collection"
    InternalPart = "internalpart"
    Track = "track"
    Map = "map"
    Graphic = "graphic"
    SoundUnit = "soundunit"
    SoundRecording = "soundrecording"
    Archive = "archive"
    Manuscript = "manuscript"
    Picture = "picture"


class Accessibility(Enum):
    Public = "public"
    Private = "private"


class MimeType(Enum):
    Pdf = "application/pdf"
    Jpeg = "image/jpeg"


class KrameriusException(Exception):
    pass
