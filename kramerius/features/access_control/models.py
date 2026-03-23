from typing import Annotated, List

from pydantic import BaseModel, Field, model_validator

from kramerius.definitions.actions import (
    LICENSE_SCOPED,
    OBJECT_TARGETABLE,
    Action,
)
from kramerius.definitions.licenses import GlobalLicense


def _to_action(action: Action | str) -> Action:
    return action if isinstance(action, Action) else Action(action)


class AccessControlLicense(BaseModel):
    name: str = Field(description="License name.")
    local: bool = Field(True, description="Is this a local license?")

    @model_validator(mode="after")
    def validate_license(self) -> "AccessControlLicense":
        global_values = {m.value for m in GlobalLicense}
        if not self.local and self.name not in global_values:
            raise ValueError(f"Invalid global license name: {self.name}")
        return self


def validate_license_scope(action: Action | str) -> None:
    if _to_action(action) not in LICENSE_SCOPED:
        raise ValueError("License only allowed for a_read and a_pdf_read")


def validate_object_scope(action: Action | str) -> None:
    if _to_action(action) not in OBJECT_TARGETABLE:
        raise ValueError(
            "Object only allowed for: a_read, a_pdf_read, a_delete, "
            "a_index, a_rebuild_processing_index, a_set_accessibility, "
            "a_rights_edit, a_collections_edit, "
            "a_able_tobe_part_of_collections"
        )


class ActionGrant(BaseModel):
    action: Action
    license: str | None = Field(default=None, description="License name.")
    object_pid: str | None = Field(
        default=None, alias="object", description="Object PID."
    )

    @model_validator(mode="after")
    def validate_grant(self) -> "ActionGrant":
        if self.license:
            validate_license_scope(self.action)
        if self.object_pid:
            validate_object_scope(self.action)
        return self


class Actor(BaseModel):
    name: str = Field(min_length=1, description="...")
    role: str
    ips: list[str] = Field(default_factory=list)
    actions: Annotated[list[ActionGrant], Field(min_length=1)]


class AccessControlUser(BaseModel):
    username: str = Field(description="User identifier (login name).")
    roles: List[str] = Field(
        min_length=1, description="Role names assigned to this user."
    )


AccessControl = List[Actor]
AccessControlLicenses = List[AccessControlLicense]
AccessControlUsers = List[AccessControlUser]
