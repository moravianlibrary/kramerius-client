from collections import defaultdict
from pathlib import Path
from typing import Callable

import yaml
from solrify import F

from kramerius.client import KrameriusClient
from kramerius.definitions import KrameriusField, RightsCriterium
from kramerius.definitions.actions import Action
from kramerius.features.access_control.models import (
    AccessControlLicense,
    ActionGrant,
    Actor,
)
from kramerius.features.access_control.param_chunking import (
    expand_actors_for_rights_param_storage,
)
from kramerius.schemas import (
    ChangeLicenseOrderingRequest,
    CreateLocalLicenseRequest,
    CreateRightParamRequest,
    CreateRightRequest,
    CreateRoleRequest,
    RightCriteriumParamsPayload,
    RightCriteriumPayload,
    RightRecord,
    RightRoleRef,
    RoleListParams,
)

KRAMERIUS_DEFAULT_ROLES = [
    "common_users",
    "offline_access",
    "uma_authorization",
    "default-roles-kramerius",
    "kramerius_admin",
]


def _load_licenses(root: Path) -> list[AccessControlLicense]:
    with open(root / "licenses.yaml", "r") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, list):
        raise ValueError("licenses.yaml must be a list of licenses")

    return [AccessControlLicense.model_validate(license) for license in raw]


def _load_actors(root: Path) -> list[Actor]:
    actors: list[Actor] = []

    for path in root.glob("access-control/*.yaml"):
        with open(path, "r") as f:
            raw = yaml.safe_load_all(f)
            for actor in raw:
                actors.append(Actor.model_validate(actor))

    return actors


def _get_rights_criterium_qname(
    action: Action, license: str | None, ips: list[str] | None
) -> str | None:
    if license and ips:
        return RightsCriterium.LicensesIpFiltered.value
    if license:
        return RightsCriterium.Licenses.value
    if ips:
        return RightsCriterium.DefaultIpAddressFilter.value
    return None


def push_access_control(
    client: KrameriusClient,
    root: Path,
    repo_pid: str,
    dry_run: bool,
    log: Callable[[str], None],
):
    def _log(target: str, message: str):
        log(f"[{target}] {message}")

    licenses_config = _load_licenses(root)
    actors_config = expand_actors_for_rights_param_storage(_load_actors(root))

    for actor in actors_config:
        for action in actor.actions:
            if action.object_pid is None:
                continue
            num_found = client.Search.num_found(
                F(KrameriusField.Pid, action.object_pid)
            )
            if num_found == 0:
                raise ValueError(
                    f"Object {action.object_pid} not found in Kramerius"
                )

    # --- 1. Licenses ---
    # - 1.1. Create local licenses that are missing in remote
    # - 1.2. Prune remote local licenses that are not in config
    # - 1.3. Order licenses in remote like in config
    remote_local_licenses = client.Licenses.get_local()
    remote_local_licenses_by_name = {L.name: L for L in remote_local_licenses}
    remote_local_licenses_names = set(remote_local_licenses_by_name.keys())
    config_local_licenses_names = {L.name for L in licenses_config if L.local}

    # 1.1.
    missing_local_licenses = (
        config_local_licenses_names - remote_local_licenses_names
    )
    for license_name in missing_local_licenses:
        _log("licenses/CreateLocal", f"Creating local license {license_name}")
        if not dry_run:
            client.Licenses.create_local(
                CreateLocalLicenseRequest(name=license_name)
            )
    if not missing_local_licenses:
        _log(
            "licenses/CreateLocal", "All local licenses are present in remote"
        )

    # 1.2.
    remote_local_licenses_to_prune = (
        remote_local_licenses_names - config_local_licenses_names
    )
    for license_name in remote_local_licenses_to_prune:
        license = remote_local_licenses_by_name[license_name]
        _log(
            "licenses/DeleteLocal",
            f"Pruning remote local license {license_name}",
        )
        if not dry_run:
            client.Licenses.delete_local(license.id)
    if not remote_local_licenses_to_prune:
        _log("licenses/DeleteLocal", "No remote local licenses to prune")

    # 1.3.
    remote_licenses = client.Licenses.get_all()
    remote_licenses_priority_by_name = {
        L.name: L.priority for L in remote_licenses
    }
    remote_licenses_by_name = {L.name: L for L in remote_licenses}

    change_priority_licenses = []
    for idx, license in enumerate(licenses_config):
        if license.name not in remote_licenses_by_name:
            continue
        remote_priority = remote_licenses_priority_by_name.get(license.name)

        if remote_priority != idx + 1:
            remote_license = remote_licenses_by_name[license.name]
            change_priority_licenses.append(
                remote_license.model_copy(update={"priority": idx + 1})
            )

    if change_priority_licenses:
        _log(
            "licenses/ChangePriority",
            f"Changing priority of {len(change_priority_licenses)} licenses",
        )
        if not dry_run:
            client.Licenses.change_ordering(
                ChangeLicenseOrderingRequest(licenses=change_priority_licenses)
            )
    if not change_priority_licenses:
        _log("licenses/ChangePriority", "No licenses to change priority")

    # --- 2. Roles ---
    # - 2.1. Create roles that are missing in remote
    # - 2.2. Prune rights for roles that are not in config
    # - 2.3. Prune roles that are not in config
    local_roles = {a.role for a in actors_config}
    remote_roles = client.Roles.list_roles(
        RoleListParams(offset=0, result_size=500)
    )
    if len(remote_roles) == 500:
        raise ValueError("Too many roles to process")
    remote_roles_by_name = {R.name: R for R in remote_roles}
    remote_roles_names = set(remote_roles_by_name.keys())
    all_rights = client.Rights.list_rights()
    rights_by_role_id: dict[int, list[RightRecord]] = defaultdict(list)
    for r in all_rights:
        rights_by_role_id[r.role.id].append(r)

    # 2.1.
    missing_roles = local_roles - remote_roles_names

    for role_name in missing_roles:
        _log("roles/Create", f"Creating role {role_name}")
        if not dry_run:
            client.Roles.create_role(CreateRoleRequest(name=role_name))
    if not missing_roles:
        _log("roles/Create", "All roles are present in remote")

    if missing_roles and not dry_run:
        remote_roles = client.Roles.list_roles(
            RoleListParams(offset=0, result_size=500)
        )
        remote_roles_by_name = {R.name: R for R in remote_roles}

    # 2.2.
    remote_roles_to_prune = (
        remote_roles_names - local_roles - set(KRAMERIUS_DEFAULT_ROLES)
    )

    for role_name in remote_roles_to_prune:
        role = remote_roles_by_name[role_name]
        role_rights = rights_by_role_id.get(role.id, [])
        if role_rights:
            _log("roles/DeleteRights", f"Pruning rights for role {role_name}")
            if not dry_run:
                for role_right in role_rights:
                    client.Rights.delete(role_right.id)
        else:
            _log(
                "roles/DeleteRights",
                f"No rights to prune for role {role_name}",
            )
    if not remote_roles_to_prune:
        _log("roles/DeleteRights", "No roles to prune rights for")

    # 2.3.
    for role_name in remote_roles_to_prune:
        role = remote_roles_by_name[role_name]
        _log("roles/Delete", f"Pruning role {role_name}")
        if not dry_run:
            client.Roles.delete(role.id)
    if not remote_roles_to_prune:
        _log("roles/Delete", "No roles to prune")

    # --- 3. Create Params ---
    # Create params that are missing in remote
    remote_params = client.Rights.list_params()
    remote_params_by_name = {P.description: P for P in remote_params}
    remote_params_names = set(remote_params_by_name.keys())
    config_params_by_name = {P.name: P for P in actors_config if P.ips}
    config_params_names = set(config_params_by_name.keys())

    missing_params = config_params_names - remote_params_names

    for param_name in missing_params:
        param = config_params_by_name[param_name]
        _log("params/Create", f"Creating param {param_name}")
        if not dry_run:
            client.Rights.create_param(
                CreateRightParamRequest(
                    description=param_name, objects=param.ips
                )
            )
    if not missing_params:
        _log("params/Create", "All params are present in remote")

    if missing_params and not dry_run:
        remote_params = client.Rights.list_params()

    # --- 4. Rights ---
    # - 4.1. Create rights that are missing in remote
    # - 4.2. Prune rights that are not in config
    type RightKey = tuple[str, str, str, str | None, str | None, str | None]

    def _remote_right_key(right: RightRecord) -> RightKey:
        return (
            right.action.value,
            right.pid,
            right.role.name,
            right.criterium_qname,
            right.criterium_params_description,
            right.criterium_license,
        )

    def _config_right_key(actor: Actor, action: ActionGrant) -> RightKey:
        if action.license == "":
            raise ValueError("License cannot be empty")
        return (
            action.action.value,
            action.object_pid or repo_pid,
            actor.role,
            _get_rights_criterium_qname(
                action.action, action.license, actor.ips
            ),
            actor.name if actor.ips else None,
            action.license or None,
        )

    remote_rights = client.Rights.list_rights()
    remote_rights_by_key = {_remote_right_key(R): R for R in remote_rights}
    remote_rights_keys = set(remote_rights_by_key.keys())
    config_rights_by_key = {
        _config_right_key(A, action): (A, action)
        for A in actors_config
        for action in A.actions
    }
    config_rights_keys = set(config_rights_by_key.keys())
    remote_params_by_name = {P.description: P for P in remote_params}

    # 4.1.
    missing_rights = config_rights_keys - remote_rights_keys

    for key in missing_rights:
        actor, action = config_rights_by_key[key]
        qname = _get_rights_criterium_qname(
            action.action, action.license, actor.ips
        )
        _log(
            "rights/Create",
            (
                f"Creating right for {actor.name} {action.action.value}"
                f" for role {actor.role}"
                f" for object {action.object_pid or repo_pid}"
                f" for criterium {qname}"
                f" for params {actor.name if actor.ips else None}"
                f" for license {action.license}"
            ),
        )
        if not dry_run:
            role = remote_roles_by_name[actor.role]
            remote_param = remote_params_by_name.get(actor.name)
            criterium = None
            if qname is not None:
                criterium = RightCriteriumPayload(
                    qname=qname,
                    params=(
                        RightCriteriumParamsPayload(
                            id=remote_param.id,
                            description=remote_param.description,
                            objects=remote_param.objects,
                        )
                        if remote_param
                        else None
                    ),
                    license=action.license,
                )
            client.Rights.create(
                CreateRightRequest(
                    action=action.action,
                    pid=action.object_pid or repo_pid,
                    role=RightRoleRef(id=role.id, name=role.name),
                    criterium=criterium,
                )
            )
    if not missing_rights:
        _log("rights/Create", "All rights are present in remote")

    # 4.2.
    remote_rights_to_prune = remote_rights_keys - config_rights_keys

    for key in remote_rights_to_prune:
        right = remote_rights_by_key[key]
        _log(
            "rights/Delete",
            f"Pruning right for {right.role.name} {right.action.value}",
        )
        if not dry_run:
            client.Rights.delete(right.id)
    if not remote_rights_to_prune:
        _log("rights/Delete", "No rights to prune")

    # --- 5. Prune Params ---
    remote_params_to_prune = remote_params_names - config_params_names

    for param_name in remote_params_to_prune:
        param = remote_params_by_name[param_name]
        _log("params/Delete", f"Pruning param {param_name}")
        if not dry_run:
            try:
                client.Rights.delete_param(param.id)
            except Exception as e:
                _log("params/Delete", f"Error pruning param {param_name}: {e}")
                raise e
    if not remote_params_to_prune:
        _log("params/Delete", "No params to prune")
