from kramerius.schemas.processing import KrameriusBatchOfProcesses

from ..definitions import ProcessType
from ..definitions.processing import ProcessState
from ..schemas import (
    KrameriusPlanProcess,
    KrameriusProcessPlanResponse,
    KrameriusSingleProcess,
    ProcessParams,
)
from .base import (
    KrameriusBaseClient,
    response_to_schema,
    response_to_schema_list,
)


class ProcessingClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def plan(
        self, type: ProcessType, params: ProcessParams | None = None
    ) -> KrameriusProcessPlanResponse:
        return response_to_schema(
            self._client.request(
                "POST",
                "api/admin/v7.0/processes",
                data=KrameriusPlanProcess(
                    defid=type, params=params
                ).model_dump_json(exclude_none=True),
            ),
            KrameriusProcessPlanResponse,
        )

    def get(
        self, id: str | None = None, uuid: str | None = None
    ) -> KrameriusSingleProcess:
        endpoint = None
        if id:
            endpoint = f"api/admin/v7.0/processes/by_process_id/{id}"
        elif uuid:
            endpoint = f"api/admin/v7.0/processes/by_process_uuid/{uuid}"
        else:
            raise ValueError("Id or uuid of the process must be provided")

        return response_to_schema(
            self._client.request("GET", endpoint), KrameriusSingleProcess
        )

    def page(
        self,
        page: int = 1,
        page_size: int = 10,
        state: ProcessState | None = None,
    ) -> list[KrameriusSingleProcess]:
        params = {
            "offset": page_size * (page - 1),
            "limit": page_size,
            "wt": "json",
        }
        if state:
            params["state"] = state.value

        return response_to_schema_list(
            self._client.request(
                "GET",
                "api/admin/v7.0/processes/batches",
                params,
            ),
            KrameriusBatchOfProcesses,
            "batches",
        )

    def get_count_by_state(self, state: ProcessState) -> int:
        return self._client.request(
            "GET",
            "api/admin/v7.0/processes/batches",
            {"state": state.value, "resultSize": 1},
        ).json()["total_size"]

    def get_num_active(self) -> int:
        return sum(
            self.get_count_by_state(state)
            for state in [ProcessState.Running, ProcessState.Planned]
        )
