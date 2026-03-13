from enum import Enum


class TreePredicate(Enum):
    HasPage = "hasPage"
    HasPart = "hasPart"
    HasVolume = "hasVolume"
    HasItem = "hasItem"
    HasUnit = "hasUnit"
    HasIntCompPart = "hasIntCompPart"
    IsOnPage = "isOnPage"


class DatastreamId(Enum):
    ImgFull = "IMG_FULL"
    ImgThumbnail = "IMG_THUMB"
    ImgPreview = "IMG_PREVIEW"
    Ocr = "TEXT_OCR"
    Alto = "ALTO"
    RelsExt = "RELS-EXT"
    BiblioMods = "BIBLIO_MODS"
    DC = "DC"
    Audit = "AUDIT"
