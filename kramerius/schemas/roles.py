"""Pydantic models for Admin API ``/roles`` (OpenAPI v7.0)."""

from pydantic import BaseModel, ConfigDict, Field


class RoleListParams(BaseModel):
    """Query parameters for ``GET .../roles`` (``getRoles``)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str | None = None
    offset: int | str | None = None
    result_size: int | str | None = Field(default=None, alias="resultSize")
    ordering: str | None = None
    typefordering: str | None = None


class Role(BaseModel):
    """Role JSON as returned by ``RolesResource.roleToJSON``."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str


class CreateRoleRequest(BaseModel):
    """Body for ``POST .../roles`` (server assigns ``id``)."""

    model_config = ConfigDict(extra="ignore")

    name: str


class UpdateRoleRequest(BaseModel):
    """Body for ``PUT .../roles/{id}``."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
