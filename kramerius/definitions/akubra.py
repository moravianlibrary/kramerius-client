from enum import Enum

from lxml import etree

type Xml = etree._Element


class FoxmlExportFormat(str, Enum):
    Archive = "archive"
    Storage = "storage"


class ControlGroup(str, Enum):
    Xml = "X"
    Managed = "M"
    External = "E"
