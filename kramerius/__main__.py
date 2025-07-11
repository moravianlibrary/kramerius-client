import os
from enum import Enum
from time import sleep
from typing import List, Optional

import typer

from kramerius.custom_types.processing import ProcessState

from .client import KrameriusClient
from .custom_types import ProcessType, SdnntSyncAction, validate_pid
from .custom_types.kramerius import Pid
from .parsers import chunked
from .schemas import AddLicenseParams, KrameriusConfig, SearchParams

app = typer.Typer(help="Kramerius CLI")


MAX_ACTIVE_PROCESSES = 2
MAX_LICENSE_CHANGES_PER_PROCESS = 3000
MAX_RETRIES = 5
SUSPEND_TIME = 30


class Action(Enum):
    GetDocument = "GetDocument"
    GetNumFound = "GetNumFound"
    SearchFor = "SearchFor"
    GetSdnntChanges = "GetSdnntChanges"
    RunSdnntSync = "RunSdnntSync"
    GetProcess = "GetProcess"
    SearchStatistics = "SearchStatistics"
    AddLicense = "AddLicense"
    RemoveLicense = "RemoveLicense"
    GetImage = "GetImage"


@app.command()
def main(
    host: Optional[str] = typer.Option(None, help="Kramerius server host"),
    keycloak_host: Optional[str] = typer.Option(
        None, help="Keycloak server host"
    ),
    client_id: Optional[str] = typer.Option(None, help="Keycloak client ID"),
    client_secret: Optional[str] = typer.Option(
        None, help="Keycloak client secret"
    ),
    username: Optional[str] = typer.Option(
        None, help="Username for authentication"
    ),
    password: Optional[str] = typer.Option(
        None, help="Password for authentication"
    ),
    action: Action = typer.Argument(..., help="Action to perform"),
    pid: Optional[str] = typer.Option(
        None, help="PID of a document to retrieve"
    ),
    pids_file: Optional[str] = typer.Option(
        None, help="File containing a list of PIDs to retrieve"
    ),
    query: Optional[str] = typer.Option(None, help="Search query string"),
    fl: Optional[List[str]] = typer.Option(
        None, help="Optional fields list for search results"
    ),
    process_id: Optional[str] = typer.Option(
        None, help="ID of a process to retrieve"
    ),
    license: Optional[str] = typer.Option(
        None, help="License to add or remove"
    ),
    target_dir: Optional[str] = typer.Option(
        None, help="Target directory for saving"
    ),
):
    config = KrameriusConfig(
        host=host or os.getenv("K7_HOST"),
        keycloak_host=keycloak_host or os.getenv("K7_KEYCLOAK_HOST"),
        client_id=client_id or os.getenv("K7_CLIENT_ID"),
        client_secret=client_secret or os.getenv("K7_CLIENT_SECRET"),
        username=username or os.getenv("K7_USERNAME"),
        password=password or os.getenv("K7_PASSWORD"),
    )

    client = KrameriusClient(config)

    if action == Action.GetDocument:
        if pid:
            pid = validate_pid(pid)
            document = client.Search.get_document(pid)
            if document:
                print(document)
            else:
                print(f"Document with PID '{pid}' not found.")
        elif pids_file:
            with open(pids_file, "r") as file:
                for pid in file:
                    pid = validate_pid(pid.strip())
                    document = client.Search.get_document(pid)
                    if document:
                        print(document)
                    else:
                        print(f"Document with PID '{pid}' not found.")
        else:
            print("Please provide either --pid or --pids-file.")
            exit(1)

    elif action == Action.GetNumFound:
        if query:
            num_found = client.Search.num_found(query)
            print(f"Number of documents found: {num_found}")
        else:
            print("Please provide a query string with --query.")
            exit(1)

    elif action == Action.SearchFor:
        if query:
            for doc in client.Search.search(query, fl=fl):
                print(doc)
        else:
            print("Please provide a query string with --query.")
            exit(1)

    elif action == Action.GetSdnntChanges:
        print(f"Sdnnt sync timestamp: {client.Sdnnt.get_sdnnt_timestamp()}")
        for record in client.Sdnnt.iterate_sdnnt_changes():
            if len(record.sync_actions) > 1:
                print(f"Multiple actions in record: {record}")
            elif record.sync_actions[0] == SdnntSyncAction.PartialChange:
                for granularity in client.Sdnnt.get_sdnnt_granularity(
                    record.id
                ):
                    print(granularity)
            elif len(record.sync_actions) == 1:
                print(record)
            else:
                print(f"No sync actions in record: {record}")

    elif action == Action.RunSdnntSync:
        plan_response = client.Processing.plan(ProcessType.SdnntSync)
        uuid = plan_response.uuid
        state = plan_response.state
        fail_count = 0

        while state != ProcessState.Finished:
            sleep(SUSPEND_TIME)
            state = client.Processing.get(uuid=uuid).process.state

            print(f"Process with UUID '{uuid}' is in state: {state.value}")
            if state == ProcessState.Failed:
                fail_count += 1
                print(
                    f"Process with UUID '{uuid}' failed "
                    f"({fail_count}/{MAX_RETRIES})."
                )

                if fail_count >= MAX_RETRIES:
                    print("Process failed too many times. Aborting.")
                    exit(1)

                plan_response = client.Processing.plan(ProcessType.SdnntSync)
                uuid = plan_response.uuid
                state = plan_response.state

    elif action == Action.GetProcess:
        if process_id:
            process = client.Processing.get(process_id)
            print(process.model_dump_json(exclude_none=True, indent=2))
        else:
            print("Please provide a process ID with --process-id.")
            exit(1)

    elif action == Action.SearchStatistics:
        if not query:
            print("Please provide a query string with --query.")
            exit(1)
        print(
            client.Statistics.search(
                SearchParams(query=query, facet=True, facet_field="ip_address")
            )
        )

    elif action == Action.GetImage:
        if not target_dir:
            print("Please provide a target directory with --target-dir.")
            exit(1)

        pids = [pid] if pid else []
        if pids_file:
            with open(pids_file, "r") as file:
                pids.extend(line.strip() for line in file if line.strip())
        if not pids:
            print("Please provide either --pid or --pids-file.")
            exit(1)

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
                    print(f"Image for PID '{pid}' saved to '{image_path}'.")
                else:
                    print(f"Image for PID '{pid}' retrieved successfully.")
            except Exception as e:
                print(f"Failed to retrieve image for PID '{pid}': {e}")

    elif action in [Action.AddLicense, Action.RemoveLicense]:
        process_type = (
            ProcessType.AddLicense
            if action == Action.AddLicense
            else ProcessType.RemoveLicense
        )
        action_name = (
            "added to" if action == Action.AddLicense else "removed from"
        )

        if pid and license:
            client.Processing.plan(
                process_type,
                AddLicenseParams(pid=pid, license=license),
            )
            print(
                f"License '{license}' {action_name} document with PID '{pid}'."
            )
        elif pids_file and license:
            with open(pids_file, "r") as file:
                valid_pids = [
                    Pid(line.strip()) for line in file if line.strip()
                ]

            for pid_chunk in chunked(
                valid_pids, MAX_LICENSE_CHANGES_PER_PROCESS
            ):
                while (
                    client.Processing.get_num_active() >= MAX_ACTIVE_PROCESSES
                ):
                    print(
                        "Maximum number of active processes reached. "
                        "Waiting for some to finish..."
                    )
                    sleep(SUSPEND_TIME)
                process = client.Processing.plan(
                    process_type,
                    AddLicenseParams(pidlist=pid_chunk, license=license),
                )
                print(
                    f"License '{license}' {action_name} {len(pid_chunk)} "
                    f"documents in process {process.get("uuid", None)}."
                )
        else:
            print(
                "Please provide either --pid and --license "
                "or --pids-file and --license."
            )
            exit(1)


if __name__ == "__main__":
    app()
