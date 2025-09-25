from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from kramerius.definitions.akubra import ControlGroup


class ObjectMetadata(BaseModel):
    property_label: str = Field(..., alias="propertyLabel")
    property_created: datetime = Field(..., alias="propertyCreated")
    property_modified: datetime = Field(..., alias="propertyModified")
    object_storage_path: str = Field(..., alias="objectStoragePath")


class DatastreamMetadata(BaseModel):
    id: str
    mime_type: str = Field(..., alias="mimetype")
    control_group: ControlGroup = Field(..., alias="controlGroup")
    created_at: datetime = Field(..., alias="createDate")
    modified_at: datetime = Field(..., alias="lastModified")
    location: str | None = None


class DatastreamNames(BaseModel):
    datastreams: List[str] = Field(..., alias="datastreamNames")


class Relation(BaseModel):
    namespace: str = Field(..., alias="namespace")
    predicate: str = Field(..., alias="localName")
    object: str = Field(..., alias="resource")


class Relations(BaseModel):
    relations: List[Relation] = Field(..., alias="relations")


class Literal(BaseModel):
    namespace: str = Field(..., alias="namespace")
    key: str = Field(..., alias="localName")
    value: str = Field(..., alias="content")


class Literals(BaseModel):
    literals: List[Literal] = Field(..., alias="literals")


class AcknowledgePid(BaseModel):
    pid: str = Field(..., alias="objectPID")


class AcknowledgeDsId(BaseModel):
    dsid: str = Field(..., alias="dsId")
