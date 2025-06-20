from ..custom_types import ProcessType
from ..custom_types.processing import ProcessState
from ..schemas import KrameriusPlanProcess, KrameriusProcess, ProcessParams
from .base import KrameriusBaseClient


class ProcessingClient:
    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def plan(
        self, type: ProcessType, params: ProcessParams | None = None
    ) -> KrameriusProcess:
        process = KrameriusPlanProcess(defid=type, params=params)
        return self._client.admin_request(
            "POST",
            "processes",
            data=process.model_dump_json(exclude_none=True),
            data_type="application/json",
        )
        # return KrameriusProcess.model_validate(
        #     self._client.admin_request(
        #         "POST",
        #         "processes",
        #         data=process.model_dump_json(exclude_none=True),
        #         data_type="application/json",
        #     )
        # )

    def get(
        self, id: str | None = None, uuid: str | None = None
    ) -> KrameriusProcess:
        if id is None and uuid is None:
            raise ValueError("Id or uuid of the process must be provided")
        if id:
            return self._client.admin_request(
                "GET",
                f"processes/by_process_id/{id}",
            )
        return self._client.admin_request(
            "GET",
            f"processes/by_process_uuid/{uuid}",
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
