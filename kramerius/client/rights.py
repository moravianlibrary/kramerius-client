from kramerius.definitions.actions import Action
from kramerius.schemas.licenses import License
from kramerius.schemas.rights import (
    CreateRightParamRequest,
    CreateRightRequest,
    CriteriumTypeMetadata,
    RightDeleteResult,
    RightParamDeleteResult,
    RightParamRecord,
    RightRecord,
    RightsActionsResponse,
    RightsListParams,
    UpdateRightParamRequest,
    UpdateRightRequest,
)

from .base import (
    KrameriusBaseClient,
    response_to_schema,
    response_to_schema_list,
)


class RightsClient:
    """
    Admin API client for ``/api/admin/v7.0/rights``.

    Editing endpoints require ``a_rights_edit`` on the repository (or on the
    object path for some list cases). ``GET .../criteria`` also allows
    ``a_criteria_read`` (see ``RightsResource``).
    """

    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def list_rights(
        self, params: RightsListParams | None = None
    ) -> list[RightRecord]:
        qp = (params or RightsListParams()).model_dump(
            exclude_none=True,
            mode="json",
        )
        return response_to_schema_list(
            self._client.request(
                "GET",
                "api/admin/v7.0/rights",
                params=qp,
            ),
            RightRecord,
        )

    def create(self, body: CreateRightRequest) -> RightRecord:
        return response_to_schema(
            self._client.request(
                "POST",
                "api/admin/v7.0/rights",
                data=body.model_dump_json(
                    exclude_none=True,
                    by_alias=True,
                ),
            ),
            RightRecord,
        )

    def get(self, right_id: int) -> RightRecord:
        return response_to_schema(
            self._client.request(
                "GET",
                f"api/admin/v7.0/rights/{right_id}",
            ),
            RightRecord,
        )

    def update(self, right_id: int, body: UpdateRightRequest) -> RightRecord:
        return response_to_schema(
            self._client.request(
                "PUT",
                f"api/admin/v7.0/rights/{right_id}",
                data=body.model_dump_json(
                    exclude_none=True,
                    by_alias=True,
                ),
            ),
            RightRecord,
        )

    def delete(self, right_id: int) -> RightDeleteResult:
        return response_to_schema(
            self._client.request(
                "DELETE",
                f"api/admin/v7.0/rights/{right_id}",
            ),
            RightDeleteResult,
        )

    def resolve(
        self, pid: str, action: Action
    ) -> dict[str, list[RightRecord]]:
        """Resolve rights for PID paths; ``action`` is required by the server."""
        raw = self._client.request(
            "GET",
            f"api/admin/v7.0/rights/resolve/{pid}",
            params={"action": action},
        ).json()
        return {
            path: [RightRecord.model_validate(item) for item in items]
            for path, items in raw.items()
        }

    def list_params(self) -> list[RightParamRecord]:
        return response_to_schema_list(
            self._client.request("GET", "api/admin/v7.0/rights/params"),
            RightParamRecord,
        )

    def create_param(self, body: CreateRightParamRequest) -> RightParamRecord:
        return response_to_schema(
            self._client.request(
                "POST",
                "api/admin/v7.0/rights/params",
                data=body.model_dump_json(exclude_none=True, by_alias=True),
            ),
            RightParamRecord,
        )

    def get_param(self, param_id: int) -> RightParamRecord:
        return response_to_schema(
            self._client.request(
                "GET",
                f"api/admin/v7.0/rights/params/{param_id}",
            ),
            RightParamRecord,
        )

    def update_param(
        self, param_id: int, body: UpdateRightParamRequest
    ) -> RightParamRecord:
        return response_to_schema(
            self._client.request(
                "PUT",
                f"api/admin/v7.0/rights/params/{param_id}",
                data=body.model_dump_json(exclude_none=True, by_alias=True),
            ),
            RightParamRecord,
        )

    def delete_param(self, param_id: int) -> RightParamDeleteResult:
        return response_to_schema(
            self._client.request(
                "DELETE",
                f"api/admin/v7.0/rights/params/{param_id}",
            ),
            RightParamDeleteResult,
        )

    def criteria(self) -> dict[str, CriteriumTypeMetadata]:
        raw = self._client.request(
            "GET",
            "api/admin/v7.0/rights/criteria",
        ).json()
        return {
            qname: CriteriumTypeMetadata.model_validate(meta)
            for qname, meta in raw.items()
        }

    def licenses(self) -> list[License]:
        """Licenses available in rights UI (same JSON shape as admin licenses)."""
        return response_to_schema_list(
            self._client.request("GET", "api/admin/v7.0/rights/licenses"),
            License,
        )

    def actions(self, pid: str | None = None) -> RightsActionsResponse:
        """
        List formal action names (``a_*``).

        Not described in OpenAPI; implemented on the server as
        ``GET .../rights/actions``.
        """
        params = {"pid": pid} if pid is not None else {}
        return response_to_schema(
            self._client.request(
                "GET",
                "api/admin/v7.0/rights/actions",
                params=params,
            ),
            RightsActionsResponse,
        )
