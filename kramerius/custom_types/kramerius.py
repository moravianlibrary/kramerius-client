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
    Pid = ("Pid", "pid")
    ParentPid = ("ParentPid", "own_parent.pid")
    RootPid = ("RootPid", "root.pid")
    OwnPidPath = ("OwnPidPath", "own_pid_path")

    Model = ("Model", "model")
    ParentModel = ("ParentModel", "own_parent.model")
    RootModel = ("RootModel", "root.model")
    ModelPath = ("ModelPath", "own_model_path")
    Level = ("Level", "level")

    InCollections = ("InCollections", "in_collections")
    DirectInCollections = ("DirectInCollections", "in_collections.direct")
    Licenses = ("Licenses", "licenses")
    ContainsLicenses = ("ContainsLicenses", "contains_licenses")
    AncestralLicenses = ("AncestralLicenses", "licenses_of_ancestors")
    Accessibility = ("Accessibility", "accessibility")

    ControlNumber = ("ControlNumber", "id_sysno")
    Barcode = ("Barcode", "id_barcode")
    Nbn = ("Nbn", "id_ccnb")
    Isbn = ("Isbn", "id_isbn")
    Issn = ("Issn", "id_issn")
    Signature = ("Signature", "shelf_locators")
    PhysicalLocation = ("PhysicalLocation", "physical_locations.facet")

    DateMin = ("DateMin", "date.min")
    DateMax = ("DateMax", "date.max")
    DateRangeStartYear = ("DateRangeStartYear", "date_range_start.year")
    DateRangeEndYear = ("DateRangeEndYear", "date_range_end.year")

    Title = ("Title", "title.search")
    TitleSort = ("TitleSort", "title.sort")
    Titles = ("Titles", "titles.search")
    PartNumberSort = ("PartNumberSort", "part.number.sort")
    PartNumberString = ("PartNumberString", "part.number.str")

    PublishersFacet = ("PublishersFacet", "publishers.facet")
    PublicationPlacesFacet = (
        "PublicationPlacesFacet",
        "publication_places.facet",
    )
    LanguagesFacet = ("LanguagesFacet", "languages.facet")

    PageCount = ("PageCount", "count_page")

    KeywordsFacet = ("KeywordsFacet", "keywords.facet")
    ImageFullMimeType = ("ImageFullMimeType", "ds.img_full.mime")


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


class KrameriusException(Exception):
    pass
