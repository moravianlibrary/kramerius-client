from enum import Enum
import uuid


Wildcard = "*"


class Field(Enum):
    Pid = "pid"
    ParentPid = "own_parent.pid"
    OwnPidPath = "own_pid_path"

    Accessibility = "accessibility"
    Licences = "licenses"
    ContainsLicences = "contains_licenses"
    AncestralLicences = "licenses_of_ancestors"
    Model = "model"
    ModelPath = "own_model_path"
    ParentModel = "own_parent.model"
    Level = "level"

    Barcode = "id_barcode"
    Signature = "shelf_locators"
    Cnb = "id_ccnb"
    Sysno = "id_sysno"

    PhysicalLocation = "physical_locations.facet"

    DateMin = "date.min"
    DateMax = "date.max"
    DateRangeStartYear = "date_range_start.year"
    DateRangeEndYear = "date_range_end.year"

    Title = "title.search"
    TitleSort = "title.sort"
    PartNumberSort = "part.number.sort"
    PartNumberString = "part.number.str"

    PublishersFacet = "publishers.facet"
    PublicationPlacesFacet = "publication_places.facet"
    LanguagesFacet = "languages.facet"

    PageCount = "count_page"

    KeywordsFacet = "keywords.facet"
    ImageFullMimeType = "ds.img_full.mime"


class SolrConjuction(Enum):
    And = " AND "
    Or = " OR "


class Pid:
    def __init__(self, value: str):
        try:
            self._uuid = uuid.UUID(
                value[5:] if value.startswith("uuid:") else value
            )
        except ValueError:
            raise ValueError("Invalid UUID format")

    def __str__(self):
        return f"uuid:{self._uuid}"

    def __repr__(self):
        return f"Pid('{self}')"

    def __eq__(self, other):
        if isinstance(other, Pid):
            return self._uuid == other._uuid
        return False

    def __hash__(self):
        return hash(self._uuid)


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


class TreePredicate(Enum):
    HasPage = "hasPage"
    HasPart = "hasPart"
    HasVolume = "hasVolume"
    HasItem = "hasItem"
    HasUnit = "hasUnit"
    HasIntCompPart = "hasIntCompPart"
    IsOnPage = "isOnPage"


class License(Enum):
    Public = "public"
    OnSite = "onsite"
    OnSiteSheetmusic = "onsite-sheetmusic"
    Dnnto = "dnnto"
    Dnntt = "dnntt"
    PublicOnContract = "mzk_public-contract"
    PublicMUO = "mzk_public-muo"
    Covid = "covid"
    License = "license"


class MimeType(Enum):
    Pdf = "application/pdf"


class Accessibility(Enum):
    Public = "public"
    Private = "private"
