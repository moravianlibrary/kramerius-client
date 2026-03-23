"""
Pydantic models for Admin API ``/rights``
(OpenAPI v7.0 / ``RightsResource``).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from kramerius.definitions.actions import Action
from kramerius.definitions.criteria import RightsCriterium


def _coerce_action(v):
    if v is None or isinstance(v, Action):
        return v
    if isinstance(v, str):
        try:
            return Action(v)
        except ValueError:
            return v
    return v


ActionLike = Annotated[Action | str, BeforeValidator(_coerce_action)]


class RightsListParams(BaseModel):
    """Query parameters for ``GET .../rights``."""

    model_config = ConfigDict(extra="ignore")

    pids: str | None = None
    action: Action | None = None


class RightRoleRef(BaseModel):
    """``role`` object on a right (see ``RightsResource.userToJSON``)."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str


class RightParamRecord(BaseModel):
    """
    Criterium params / ``GET .../rights/params`` row.

    Matches admin OpenAPI: ``id``, ``objects``, ``description`` only.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int
    description: str = ""
    objects: list[str] = Field(default_factory=list)


class RightCriteriumParamsPayload(BaseModel):
    """
    ``criterium.params`` in POST/PUT bodies.

    Same shape as ``GET/PUT .../rights/params`` (``id``, ``objects``,
    ``description``).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int | None = None
    description: str | None = None
    objects: list[str] | None = None


class RightCriteriumPayload(BaseModel):
    """``criterium`` object when creating or updating a right."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    qname: RightsCriterium | str
    params: RightCriteriumParamsPayload | None = None
    label: str | None = None
    license: str | None = Field(
        default=None,
        description=(
            "License name (server accepts ``license`` and/or ``label``)."
        ),
    )


class RightCriteriumView(BaseModel):
    """``criterium`` on a right in responses."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    qname: str
    params: RightParamRecord | None = None
    license: str | None = None
    label: str | None = None


class RightRecord(BaseModel):
    """Single right as returned by the API."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    action: ActionLike
    pid: str
    role: RightRoleRef
    criterium: RightCriteriumView | None = None
    fixed_priority: int | None = Field(default=None, alias="fixedPriority")

    @property
    def criterium_qname(self) -> str | None:
        if self.criterium:
            return self.criterium.qname
        return None

    @property
    def criterium_params_description(self) -> str | None:
        if (
            self.criterium
            and self.criterium.params
            and self.criterium.params.description != ""
        ):
            return self.criterium.params.description
        return None

    @property
    def criterium_license(self) -> str | None:
        if self.criterium:
            return self.criterium.license
        return None


class CreateRightRequest(BaseModel):
    """Body for ``POST .../rights``."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    action: Action
    pid: str
    role: RightRoleRef
    criterium: RightCriteriumPayload | None = None
    fixed_priority: int | None = Field(default=None, alias="fixedPriority")
    id: int | None = None


class UpdateRightRequest(BaseModel):
    """Body for ``PUT .../rights/{id}``."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int
    action: Action
    pid: str
    role: RightRoleRef
    criterium: RightCriteriumPayload | None = None
    fixed_priority: int | None = Field(default=None, alias="fixedPriority")


class RightDeleteResult(BaseModel):
    """``DELETE .../rights/{id}`` response (right JSON plus ``deleted``)."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int
    action: ActionLike
    pid: str
    role: RightRoleRef
    criterium: RightCriteriumView | None = None
    fixed_priority: int | None = Field(default=None, alias="fixedPriority")
    deleted: bool


class CriteriumTypeMetadata(BaseModel):
    """One entry under ``GET .../rights/criteria`` (keyed by ``qname``)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    params_necessary: bool = Field(alias="paramsNecessary")
    is_label_assignable: bool = Field(alias="isLabelAssignable")
    is_license_assignable: bool = Field(alias="isLicenseAssignable")
    root_level_criterum: bool = Field(alias="rootLevelCriterum")
    applicable_actions: list[ActionLike] = Field(alias="applicableActions")


class CreateRightParamRequest(BaseModel):
    """
    Body for ``POST .../rights/params``.

    Not in OpenAPI; implemented on the server.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int | None = None
    description: str | None = None
    objects: list[str] | None = None


class UpdateRightParamRequest(BaseModel):
    """Body for ``PUT .../rights/params/{id}``."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int
    description: str | None = None
    objects: list[str] | None = None


class RightParamDeleteResult(RightParamRecord):
    deleted: bool = True


class RightsActionsResponse(BaseModel):
    """``GET .../rights/actions`` (not in OpenAPI; present on server)."""

    model_config = ConfigDict(extra="ignore")

    actions: list[ActionLike]
