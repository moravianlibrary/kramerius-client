from enum import Enum


class GlobalLicense(Enum):
    Public = "public"
    Dnnto = "dnnto"
    Dnntt = "dnntt"
    OnSite = "onsite"
    OnSiteSheetmusic = "onsite-sheetmusic"


License = GlobalLicense | str
