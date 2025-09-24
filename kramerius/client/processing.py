from ..definitions import ProcessType
from ..definitions.processing import ProcessState
from ..schemas import (
    KrameriusPlanProcess,
    KrameriusProcessPlanResponse,
    KrameriusSingleProcess,
    ProcessParams,
)
from .base import KrameriusBaseClient


class ProcessingClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def plan(
        self, type: ProcessType, params: ProcessParams | None = None
    ) -> KrameriusProcessPlanResponse:
        process = KrameriusPlanProcess(defid=type, params=params)
        return KrameriusProcessPlanResponse.model_validate(
            self._client.admin_request(
                "POST",
                "processes",
                data=process.model_dump_json(exclude_none=True),
                data_type="application/json",
            )
        )

    def get(
        self, id: str | None = None, uuid: str | None = None
    ) -> KrameriusSingleProcess:
        if id is None and uuid is None:
            raise ValueError("Id or uuid of the process must be provided")
        if id:
            return KrameriusSingleProcess.model_validate(
                self._client.admin_request(
                    "GET",
                    f"processes/by_process_id/{id}",
                )
            )
        return KrameriusSingleProcess.model_validate(
            self._client.admin_request(
                "GET",
                f"processes/by_process_uuid/{uuid}",
            )
        )

    def get_num_active(self) -> int:
        num_active = self._client.admin_request(
            "GET",
            "processes/batches",
            {"state": ProcessState.Running.value, "resultSize": 1},
        )["total_size"]
        num_active += self._client.admin_request(
            "GET",
            "processes/batches",
            {"state": ProcessState.Planned.value, "resultSize": 1},
        )["total_size"]
        return num_active

    def get_count_by_state(self, state: ProcessState) -> int:
        return self._client.admin_request(
            "GET",
            "processes/batches",
            {"state": state.value, "resultSize": 1},
        )["total_size"]
