from enum import Enum

import lxml.etree as etree

type Xml = etree._Element


class FoxmlExportFormat(str, Enum):
    Archive = "archive"
    Storage = "storage"


class ControlGroup(str, Enum):
    Xml = "X"
    Managed = "M"
    External = "E"
