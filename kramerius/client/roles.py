from kramerius.schemas.roles import (
    CreateRoleRequest,
    Role,
    RoleListParams,
    UpdateRoleRequest,
)

from .base import (
    KrameriusBaseClient,
    response_to_schema,
    response_to_schema_list,
)


class RolesClient:
    """
    Admin API client for ``/api/admin/v7.0/roles``.

    On the server, list/detail GET allows ``a_roles_read`` or the same edit
    rights as mutations; POST/PUT/DELETE require ``a_roles_edit`` or
    ``a_rights_edit`` (see ``RolesResource``).
    """

    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def list_roles(self, params: RoleListParams | None = None) -> list[Role]:
        """
        Filtered / paginated role list (``getRoles``).

        Pass ``RoleListParams`` for query fields; ``None`` means no query string.
        """
        return response_to_schema_list(
            self._client.request(
                "GET",
                "api/admin/v7.0/roles",
                params=(
                    params or RoleListParams()
                ).model_dump(exclude_none=True, by_alias=True),
            ),
            Role,
        )

    def create(self, body: CreateRoleRequest) -> Role:
        return response_to_schema(
            self._client.request(
                "POST",
                "api/admin/v7.0/roles",
                data=body.model_dump_json(exclude_none=True),
            ),
            Role,
        )

    def get(self, role_id: str | int) -> Role:
        return response_to_schema(
            self._client.request(
                "GET",
                f"api/admin/v7.0/roles/{role_id}",
            ),
            Role,
        )

    def update(self, role_id: str | int, body: UpdateRoleRequest) -> Role:
        return response_to_schema(
            self._client.request(
                "PUT",
                f"api/admin/v7.0/roles/{role_id}",
                data=body.model_dump_json(exclude_none=True),
            ),
            Role,
        )

    def delete(self, role_id: str | int) -> None:
        self._client.request(
            "DELETE",
            f"api/admin/v7.0/roles/{role_id}",
        )
