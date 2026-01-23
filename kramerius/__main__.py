import json
import os
from datetime import datetime
from math import ceil
from pathlib import Path
from time import sleep
from typing import List, Optional

import typer
from dotenv import load_dotenv
from pydantic import BaseModel
from solrify import F

from kramerius.definitions.kramerius import KrameriusField, Model
from kramerius.definitions.processing import IndexationType, ProcessState
from kramerius.schemas.processing import (
    IndexParams,
    PidOrPidlistParams,
    ProcessParams,
)

from .client import KrameriusClient
from .definitions import ProcessType, SdnntSyncAction, validate_pid
from .parsers import chunked
from .schemas import AddLicenseParams, KrameriusConfig, SearchParams

load_dotenv()


app = typer.Typer(help="Kramerius CLI")


MAX_PID_LIST_SIZE = 3000
MAX_LEVEL = 5


@app.callback()
def main(
    ctx: typer.Context,
    host: Optional[str] = typer.Option(
        None, envvar="K7_HOST", help="Kramerius server host"
    ),
    keycloak_host: Optional[str] = typer.Option(
        None, envvar="K7_KEYCLOAK_HOST", help="Keycloak server host"
    ),
    client_id: Optional[str] = typer.Option(
        None, envvar="K7_CLIENT_ID", help="Keycloak client ID"
    ),
    client_secret: Optional[str] = typer.Option(
        None, envvar="K7_CLIENT_SECRET", help="Keycloak client secret"
    ),
    username: Optional[str] = typer.Option(
        None,
        envvar="K7_USERNAME",
        help="Username for authentication with Keycloak",
    ),
    password: Optional[str] = typer.Option(
        None,
        envvar="K7_PASSWORD",
        help="Password for authentication with Keycloak",
    ),
    timeout: Optional[int] = typer.Option(
        30, envvar="K7_TIMEOUT", help="Request timeout in seconds"
    ),
    max_retries: Optional[int] = typer.Option(
        5,
        envvar="K7_MAX_RETRIES",
        help="Maximum number of retries for failed requests",
    ),
    retry_timeout: Optional[int] = typer.Option(
        30,
        envvar="K7_RETRY_TIMEOUT",
        help="Timeout between retries in seconds",
    ),
    max_active_processes: int = typer.Option(
        3,
        help="Maximum number of active processes",
    ),
    log_dir: Path = typer.Option(
        Path("/tmp"), help="Directory for storing run logs"
    ),
    pidlist_size: int = typer.Option(
        MAX_PID_LIST_SIZE, help="Maximum size of the PID list"
    ),
) -> KrameriusClient:
    """
    Executed before any subcommand.

    Used for:
    1. building and storing the client,
    2. setting up logging for the CLI.
    """
    ctx.obj = {}
    # Kramerius Client
    ctx.obj["client"] = KrameriusClient(
        KrameriusConfig(
            host=host,
            keycloak_host=keycloak_host,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            timeout=timeout,
            max_retries=max_retries,
            retry_timeout=retry_timeout,
            max_active_processes=max_active_processes,
        )
    )

    ctx.obj["pidlist_size"] = pidlist_size

    # File logging
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = log_dir / f"kramerius_cli_out_{timestamp}.log"
    err_file = log_dir / f"kramerius_cli_err_{timestamp}.log"

    out_file.touch(exist_ok=True)
    err_file.touch(exist_ok=True)

    ctx.obj["out_file"] = out_file
    ctx.obj["err_file"] = err_file


typer.CallbackParam
PidOption = typer.Option(None, help="PID of the document to retrieve")
PidsFileOption = typer.Option(
    None, help="File containing a list of PIDs to retrieve"
)
QueryArg = typer.Argument(..., help="Search query string")
FlOption = typer.Option(None, help="Optional field list for search results")
ProcessIdArg = typer.Argument(..., help="ID of the process to retrieve")
LicenseArg = typer.Argument(..., help="License to add or remove")
TargetDirArg = typer.Argument(..., help="Target directory for saving")


def _echo_log(ctx: typer.Context, message: str, err: bool = False):
    typer.echo(message, err=err)
    with open(
        ctx.obj.get("out_file" if not err else "err_file"),
        "a",
        encoding="utf-8",
    ) as f:
        typer.echo(message, file=f, err=err)


def _echo_pydantic(doc: BaseModel):
    typer.echo(json.dumps(doc.model_dump(mode="json"), indent=2))


def _validate_pid_input(pid: Optional[str], pids_file: Optional[str]):
    if pid is None and pids_file is None:
        typer.echo("Please provide either --pid or --pids-file.", err=True)
        raise typer.Exit(code=1)


def _plan_process(
    ctx: typer.Context,
    client: KrameriusClient,
    type: ProcessType,
    params: ProcessParams | None = None,
):
    retry_timeout = client._base.config.retry_timeout

    while (
        client.Processing.get_num_active()
        >= client._base.config.max_active_processes
    ):
        _echo_log(
            ctx,
            "Maximum number of active processes reached. "
            "Waiting for some to finish...",
        )
        sleep(retry_timeout)

    return client.Processing.plan(type, params)


def _run_process(
    ctx: typer.Context,
    client: KrameriusClient,
    type: ProcessType,
    params: ProcessParams | None = None,
    skip_retries: bool = False,
):
    plan_response = _plan_process(ctx, client, type, params)
    uuid = plan_response.uuid
    state = plan_response.state

    _echo_log(ctx, f"Process of type {type.value} and UUID {uuid} started.")

    fail_count = 0
    max_retries = client._base.config.max_retries
    retry_timeout = client._base.config.retry_timeout

    while state in [ProcessState.Planned, ProcessState.Running]:
        sleep(retry_timeout)
        state = client.Processing.get(uuid=uuid).process.state

        if skip_retries:
            continue

        _echo_log(
            ctx, f"Process with UUID '{uuid}' is in state: {state.value}."
        )

        if state == ProcessState.Failed:
            fail_count += 1
            _echo_log(
                ctx,
                f"Process with UUID '{uuid}' failed "
                f"({fail_count}/{max_retries}).",
            )

            if fail_count >= max_retries:
                _echo_log(ctx, "Process failed too many times. Aborting.")
                raise typer.Exit(code=1)

            plan_response = _plan_process(ctx, client, type, params)
            uuid = plan_response.uuid
            state = plan_response.state

            _echo_log(
                ctx, f"Process of type {type.value} and UUID {uuid} started."
            )

        elif state != ProcessState.Running:
            _echo_log(
                ctx,
                f"Process with UUID '{uuid}' "
                f"is in unexpected state: {state.value}.",
                err=True,
            )
            raise typer.Exit(1)

    _echo_log(ctx, f"Process of type {type.value} and UUID {uuid} finished.")


def _run_process_for_pidlist(
    ctx: typer.Context,
    client: KrameriusClient,
    type: ProcessType,
    params: PidOrPidlistParams,
    skip_retries: bool = False,
):
    pidlist_size = ctx.obj.get("pidlist_size", MAX_PID_LIST_SIZE)

    pid_list = params.pidlist
    num_chunks = ceil(len(pid_list) / pidlist_size)
    i = 1

    _echo_log(ctx, f"Processing {len(pid_list)} PIDs in {num_chunks} chunks.")

    for pid_chunk in chunked(pid_list, pidlist_size):
        params_copy = params.model_copy(
            deep=True, update={"pidlist": pid_chunk}
        )
        _echo_log(
            ctx,
            f"Processing chunk {i}/{num_chunks} with {len(pid_chunk)} PIDs.",
        )
        _run_process(ctx, client, type, params_copy, skip_retries)
        i += 1


@app.command()
def get_document(
    ctx: typer.Context,
    pid: Optional[str] = PidOption,
    pids_file: Optional[str] = PidsFileOption,
):
    client: KrameriusClient = ctx.obj["client"]

    _validate_pid_input(pid, pids_file)

    def _process_pid(pid: str):
        pid = validate_pid(pid)
        if pid is None:
            typer.echo('{"pid": ' + pid + ', "message": "Invalid PID"}')
            return
        document = client.Search.get_document(pid)
        if document:
            _echo_pydantic(document)
        else:
            typer.echo('{"pid": ' + pid + ', "message": "Not found"}')

    if pid:
        _process_pid(pid)

    if pids_file:
        with open(pids_file, "r") as file:
            for pid in file:
                _process_pid(pid)


@app.command()
def get_num_found(
    ctx: typer.Context,
    query: str = QueryArg,
):
    client: KrameriusClient = ctx.obj["client"]

    typer.echo(f"Number of documents found: {client.Search.num_found(query)}.")


@app.command()
def search_for(
    ctx: typer.Context,
    query: str = QueryArg,
    fl: Optional[List[str]] = FlOption,
):
    client: KrameriusClient = ctx.obj["client"]

    results = client.Search.search(query, fl=fl)
    for doc in results:
        _echo_pydantic(doc)


@app.command()
def get_sdnnt_changes(
    ctx: typer.Context,
):
    client: KrameriusClient = ctx.obj["client"]

    typer.echo(
        "Sdnnt sync timestamp: "
        f"{client.Sdnnt.get_sdnnt_timestamp().isoformat()}.",
        err=True,
    )

    for record in client.Sdnnt.iterate_sdnnt_changes():
        if len(record.sync_actions) > 1:
            typer.echo(f"Multiple actions in record: {record}.", err=True)
        elif record.sync_actions[0] == SdnntSyncAction.PartialChange:
            for granularity in client.Sdnnt.get_sdnnt_granularity(record.id):
                _echo_pydantic(granularity)
        elif len(record.sync_actions) == 1:
            _echo_pydantic(record)
        else:
            typer.echo(f"No sync actions in record: {record}.", err=True)


@app.command()
def run_sdnnt_sync(
    ctx: typer.Context,
):
    client: KrameriusClient = ctx.obj["client"]

    _run_process(ctx, client, ProcessType.SdnntSync)


@app.command()
def get_process(
    ctx: typer.Context,
    process_id: str = ProcessIdArg,
):
    client: KrameriusClient = ctx.obj["client"]

    process = client.Processing.get(id=process_id)
    if process:
        _echo_pydantic(process)
    else:
        typer.echo(
            '{"process_id": ' + process_id + ', "message": "Not found"}'
        )


# TODO: Implement search_statistics command
@app.command()
def search_statistics(
    ctx: typer.Context,
    query: str = QueryArg,
    facet: bool = typer.Option(False, help="Whether to include facet counts"),
    facet_field: Optional[str] = typer.Option(
        None, help="Field to use for faceting"
    ),
):
    client: KrameriusClient = ctx.obj["client"]

    params = SearchParams(query=query, facet=facet, facet_field=facet_field)

    for doc in client.Statistics.search(params):
        typer.echo(json.dumps(doc, indent=2))


@app.command()
def add_license(
    ctx: typer.Context,
    license: str = LicenseArg,
    pid: Optional[str] = PidOption,
    pids_file: Optional[str] = PidsFileOption,
):
    client: KrameriusClient = ctx.obj["client"]

    _validate_pid_input(pid, pids_file)

    if pid:
        _run_process(
            client,
            ProcessType.AddLicense,
            AddLicenseParams(pid=validate_pid(pid, True), license=license),
        )
    if pids_file:
        with open(pids_file, "r") as file:
            valid_pids = [validate_pid(line) for line in file]
            valid_pids = [pid for pid in valid_pids if pid is not None]
        _run_process_for_pidlist(
            ctx,
            client,
            ProcessType.AddLicense,
            AddLicenseParams(pidlist=valid_pids, license=license),
            True,
        )


@app.command()
def remove_license(
    ctx: typer.Context,
    license: str = LicenseArg,
    pid: Optional[str] = PidOption,
    pids_file: Optional[str] = PidsFileOption,
):
    client: KrameriusClient = ctx.obj["client"]

    _validate_pid_input(pid, pids_file)

    if pid:
        _run_process(
            client,
            ProcessType.RemoveLicense,
            AddLicenseParams(pid=validate_pid(pid, True), license=license),
        )
    if pids_file:
        with open(pids_file, "r") as file:
            valid_pids = [validate_pid(line) for line in file]
            valid_pids = [pid for pid in valid_pids if pid is not None]
        _run_process_for_pidlist(
            ctx,
            client,
            ProcessType.RemoveLicense,
            AddLicenseParams(pidlist=valid_pids, license=license),
            True,
        )


@app.command()
def get_image(
    ctx: typer.Context,
    target_dir: str = TargetDirArg,
    pid: Optional[str] = PidOption,
    pids_file: Optional[str] = PidsFileOption,
):
    client: KrameriusClient = ctx.obj["client"]

    _validate_pid_input(pid, pids_file)

    pids = [pid] if pid else []
    if pids_file:
        with open(pids_file, "r") as file:
            pids.extend(line.strip() for line in file if line.strip())

    for pid in pids:
        pid = validate_pid(pid)
        try:
            image_data = client.Items.get_image(pid)
            if target_dir:
                os.makedirs(target_dir, exist_ok=True)
                uuid = pid.replace("uuid:", "")
                image_path = os.path.join(target_dir, f"{uuid}.jpg")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_data)
                _echo_log(
                    ctx, f"Image for PID '{pid}' saved to '{image_path}'."
                )
            else:
                _echo_log(
                    ctx, f"Image for PID '{pid}' retrieved successfully."
                )
        except Exception as e:
            _echo_log(ctx, f"Failed to retrieve image for PID '{pid}': {e}")


@app.command()
def index_upgrade(
    ctx: typer.Context,
    indexer_version: str = typer.Argument(
        ..., help="Index version for upgrading"
    ),
):
    client: KrameriusClient = ctx.obj["client"]

    try:
        for level in range(0, MAX_LEVEL + 1):
            pids = [
                doc.pid
                for doc in client.Search.search(
                    F(KrameriusField.Level, level)
                    & ~F(KrameriusField.Model, Model.Collection)
                    & ~F(KrameriusField.IndexerVersion, indexer_version),
                    fl=[KrameriusField.Pid.value],
                )
                if doc.pid
            ]
            _echo_log(
                ctx,
                f"Level {level}: Found {len(pids)} PIDs "
                f"without indexer version {indexer_version}."
                f"{'' if pids else ' Skipping.'}",
            )
            if not pids:
                continue
            _run_process_for_pidlist(
                ctx,
                client,
                ProcessType.Index,
                IndexParams(
                    pidlist=pids,
                    type=IndexationType.TreeAndFosterTrees,
                    ignoreInconsistentObjects=True,
                ),
                True,
            )
    except Exception as e:
        _echo_log(ctx, f"Index upgrade failed: {e}", err=True)
        _echo_log(ctx, "Retrying in 10 minutes...")
        sleep(600)
        index_upgrade(ctx, indexer_version)


if __name__ == "__main__":
    app()
