from kramerius.schemas.licenses import (
    ChangeLicenseOrderingRequest,
    CreateLocalLicenseRequest,
    License,
    UpdateLocalLicenseRequest,
)

from .base import (
    KrameriusBaseClient,
    response_to_schema,
    response_to_schema_list,
)


class LicensesClient:
    """Admin API client for ``/api/admin/v7.0/licenses``."""

    def __init__(self, client: KrameriusBaseClient):
        self._client = client

    def get_all(self, runtime: bool = True) -> list[License]:
        return response_to_schema_list(
            self._client.request(
                "GET",
                "api/admin/v7.0/licenses",
                params={"runtime": runtime},
            ),
            License,
        )

    def get_global(self, runtime: bool = True) -> list[License]:
        return response_to_schema_list(
            self._client.request(
                "GET",
                "api/admin/v7.0/licenses/global",
                params={"runtime": runtime},
            ),
            License,
        )

    def get_local(self, runtime: bool = True) -> list[License]:
        return response_to_schema_list(
            self._client.request(
                "GET",
                "api/admin/v7.0/licenses/local",
                params={"runtime": runtime},
            ),
            License,
        )

    def create_local(self, body: CreateLocalLicenseRequest) -> License:
        return response_to_schema(
            self._client.request(
                "POST",
                "api/admin/v7.0/licenses/local",
                data=body.model_dump_json(exclude_none=True, by_alias=True),
            ),
            License,
        )

    def get_local_by_id(self, license_id: int) -> License:
        return response_to_schema(
            self._client.request(
                "GET",
                f"api/admin/v7.0/licenses/local/{license_id}",
            ),
            License,
        )

    def update_local(
        self, license_id: int, body: UpdateLocalLicenseRequest
    ) -> License:
        return response_to_schema(
            self._client.request(
                "PUT",
                f"api/admin/v7.0/licenses/local/{license_id}",
                data=body.model_dump_json(exclude_none=True, by_alias=True),
            ),
            License,
        )

    def delete_local(self, license_id: int) -> None:
        self._client.request(
            "DELETE",
            f"api/admin/v7.0/licenses/local/{license_id}",
        )

    def change_ordering(
        self, body: ChangeLicenseOrderingRequest
    ) -> list[License]:
        return response_to_schema_list(
            self._client.request(
                "PUT",
                "api/admin/v7.0/licenses/changeOrdering",
                data=body.model_dump_json(exclude_none=True, by_alias=True),
            ),
            License,
        )

    def move_up(self, license_id: int) -> list[License]:
        return response_to_schema_list(
            self._client.request(
                "PUT",
                f"api/admin/v7.0/licenses/moveup/{license_id}",
            ),
            License,
        )

    def move_down(self, license_id: int) -> list[License]:
        return response_to_schema_list(
            self._client.request(
                "PUT",
                f"api/admin/v7.0/licenses/movedown/{license_id}",
            ),
            License,
        )
