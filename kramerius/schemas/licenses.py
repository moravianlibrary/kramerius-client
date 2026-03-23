"""
Pydantic models for Admin API ``/licenses`` (OpenAPI v7.0, Kramerius server).
"""

from pydantic import BaseModel, ConfigDict, Field

from kramerius.definitions.licenses import LicenseGroup


class License(BaseModel):
    """
    License JSON as returned by ``LicenseTOJSONSupport.licenseToJSON``
    and accepted in ordering payloads (embedded in ``{"licenses": [...]}``
    for ``PUT .../changeOrdering``).
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int
    name: str
    description: str = ""
    priority: int
    group: LicenseGroup

    exclusive: bool | None = None
    maxreaders: int | None = None
    refreshinterval: int | None = None
    maxinterval: int | None = None
    exclusive_lock_type: str | None = Field(
        default=None,
        alias="type",
        description=(
            "Exclusive lock kind: RULE or INSTANCE (JSON key ``type``)."
        ),
    )

    runtime: bool | None = None
    runtime_license_type: str | None = Field(
        default=None,
        alias="runtime_type",
    )


class CreateLocalLicenseRequest(BaseModel):
    """Body for ``POST .../licenses/local``."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str
    description: str = ""
    priority: int | None = None
    group: LicenseGroup = LicenseGroup.Local

    exclusive: bool | None = None
    maxreaders: int | None = None
    refreshinterval: int | None = None
    maxinterval: int | None = None
    exclusive_lock_type: str | None = Field(default=None, alias="type")


class UpdateLocalLicenseRequest(BaseModel):
    """Body for ``PUT .../licenses/local/{id}``."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int
    name: str
    description: str = ""
    priority: int | None = None
    group: LicenseGroup = LicenseGroup.Local

    exclusive: bool | None = None
    maxreaders: int | None = None
    refreshinterval: int | None = None
    maxinterval: int | None = None
    exclusive_lock_type: str | None = Field(default=None, alias="type")


class ChangeLicenseOrderingRequest(BaseModel):
    """
    Body for ``PUT .../licenses/changeOrdering``.

    The OpenAPI example shows a raw array; the server expects an object with a
    ``licenses`` array (see ``LicensesResource.changeOrdering``).
    """

    licenses: list[License]
