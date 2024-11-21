import argparse
import os
from .client import KrameriusClient
from .datatypes import validate_pid, SdnntSyncAction


def main():
    parser = argparse.ArgumentParser(description="Kramerius Search Client")
    parser.add_argument(
        "action",
        choices=["GetDocument", "GetNumFound", "SearchFor", "GetSdnntChanges"],
        help="Action to perform: GetDocument, GetNumFound, SearchFor,"
        " or GetSdnntChanges",
    )
    parser.add_argument("--pid", type=str, help="PID of a document")
    parser.add_argument(
        "--pids-file", type=str, help="File containing a list of PIDs"
    )
    parser.add_argument("--query", type=str, help="Search query string")
    parser.add_argument(
        "--fl", nargs="*", help="Optional fields list for search results"
    )
    parser.add_argument("--host", type=str, help="Kramerius host")
    parser.add_argument("--username", type=str, help="Kramerius username")
    parser.add_argument("--password", type=str, help="Kramerius password")

    args = parser.parse_args()

    client = KrameriusClient(
        args.host or os.getenv("K7_HOST"),
        args.username or os.getenv("K7_USERNAME"),
        args.password or os.getenv("K7_PASSWORD"),
    )

    if args.action == "GetDocument":
        if args.pid:
            pid = validate_pid(args.pid)
            document = client.Search.get_document(pid)
            if document:
                print(document)
            else:
                print(f"Document with PID '{pid}' not found.")
        elif args.pids_file:
            with open(args.pids_file, "r") as file:
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

    elif args.action == "GetNumFound":
        if args.query:
            num_found = client.Search.num_found(args.query)
            print(f"Number of documents found: {num_found}")
        else:
            print("Please provide a query string with --query.")
            exit(1)

    elif args.action == "SearchFor":
        if args.query:
            for doc in client.Search.search(args.query, fl=args.fl):
                print(doc)
        else:
            print("Please provide a query string with --query.")
            exit(1)

    elif args.action == "GetSdnntChanges":
        for record in client.Sdnnt.iterate_sdnnt_changes():
            if len(record.sync_actions) > 1:
                print(f"Multiple actions in record: {record}")
            elif record.sync_actions[0] == SdnntSyncAction.PartialChange:
                for granularity in client.Sdnnt.get_sdnnt_granularity(record.id):
                    print(granularity)
            elif len(record.sync_actions) == 1:
                print(record)
            else:
                print(f"No sync actions in record: {record}")


if __name__ == "__main__":
    main()
