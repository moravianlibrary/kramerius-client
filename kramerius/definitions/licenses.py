from enum import Enum, StrEnum


class GlobalLicense(Enum):
    Public = "public"
    Orphan = "orphan"
    Dnnto = "dnnto"
    Dnntt = "dnntt"
    OnSite = "onsite"
    OnSiteSheetmusic = "onsite-sheetmusic"
    SpecialNeeds = "special-needs"
    CoverAndContent = "cover-and-content"


License = GlobalLicense | str


class LicenseGroup(StrEnum):
    """Values of the ``group`` field on license JSON."""

    Local = "local"
    Embedded = "embedded"


class ExclusiveLockType(StrEnum):
    """
    ``type`` on exclusive-lock licenses
    (``ExclusiveReadersLock.ExclusiveLockType``).
    """

    Rule = "RULE"
    Instance = "INSTANCE"


class RuntimeLicenseType(StrEnum):
    """``runtime_type`` when ``runtime`` is true (``RuntimeLicenseType``)."""

    AllDocuments = "ALL_DOCUMENTS"
    CoverAndContentMonographPage = "COVER_AND_CONTENT_MONOGRAPH_PAGE"
