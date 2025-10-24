from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, model_validator

from ..definitions import (
    IndexationType,
    License,
    PathType,
    Pid,
    ProcessState,
    ProcessType,
)


class EmptyParams(BaseModel):
    pass


class ImportParams(BaseModel):
    inputDataDir: str
    startIndexer: bool
    license: License
    collections: str
    pathtype: PathType


class ImportMetsParams(ImportParams):
    policy: str
    useIIPServer: bool


class PidOrPidlistParams(BaseModel):
    pid: Optional[Pid] = None
    pidlist: Optional[List[Pid]] = None

    @model_validator(mode="after")
    def at_least_one_required(cls, model):
        if model.pid is None and not model.pidlist:
            raise ValueError("Either 'pid' or 'pidlist' must be set.")
        return model


class IndexParams(PidOrPidlistParams):
    type: IndexationType
    ignoreInconsistentObjects: bool


class AddLicenseParams(PidOrPidlistParams):
    license: License


class RemoveLicenseParams(AddLicenseParams):
    pass


class DeleteTreeParams(BaseModel):
    pid: Pid
    ignoreIncosistencies: bool


ProcessParams = (
    ImportParams
    | ImportMetsParams
    | IndexParams
    | AddLicenseParams
    | RemoveLicenseParams
    | DeleteTreeParams
    | EmptyParams
)


class KrameriusPlanProcess(BaseModel):
    defid: ProcessType
    params: ProcessParams | None


class KrameriusProcessPlanResponse(BaseModel):
    uuid: str
    name: str
    state: ProcessState


class KrameriusProcessBatch(BaseModel):
    id: str
    owner_id: str
    owner_name: str

    state: ProcessState
    planned: datetime | None = None
    started: datetime | None = None
    finished: datetime | None = None

    token: str


class KrameriusProcess(BaseModel):
    id: str
    uuid: str

    defid: ProcessType
    name: str

    state: ProcessState
    planned: datetime | None = None
    started: datetime | None = None
    finished: datetime | None = None


class KrameriusSingleProcess(BaseModel):
    batch: KrameriusProcessBatch
    process: KrameriusProcess


class KrameriusBatchOfProcesses(BaseModel):
    batch: KrameriusProcessBatch
    processes: List[KrameriusProcess]
