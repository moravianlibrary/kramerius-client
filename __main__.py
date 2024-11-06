import argparse
import os
from .client import KrameriusClient
from .search import KrameriusSearch


def main():
    parser = argparse.ArgumentParser(description="Kramerius Search Client")
    parser.add_argument(
        "action",
        choices=["GetDocument", "GetNumFound", "SearchFor"],
        help="Action to perform: GetDocument, GetNumFound, or SearchFor",
    )
    parser.add_argument("--pid", type=str, help="PID of a document")
    parser.add_argument(
        "--pids-file", type=str, help="File containing a list of PIDs"
    )
    parser.add_argument("--query", type=str, help="Search query string")
    parser.add_argument(
        "--fl", nargs="*", help="Optional fields list for search results"
    )

    args = parser.parse_args()

    client = KrameriusClient(
        args.host or os.getenv("K7_HOST"),
        args.username or os.getenv("K7_USERNAME"),
        args.password or os.getenv("K7_PASSWORD"),
    )
    k_search = KrameriusSearch(client)

    if args.action == "GetDocument":
        if args.pid:
            document = k_search.get_document(args.pid)
            if document:
                print(document)
            else:
                print(f"Document with PID '{args.pid}' not found.")
        elif args.pids_file:
            with open(args.pids_file, "r") as file:
                for pid in file:
                    pid = pid.strip()
                    document = k_search.get_document(pid)
                    if document:
                        print(document)
                    else:
                        print(f"Document with PID '{pid}' not found.")
        else:
            print("Please provide either --pid or --pids-file.")
            exit(1)

    elif args.action == "GetNumFound":
        if args.query:
            num_found = k_search.num_found(args.query)
            print(f"Number of documents found: {num_found}")
        else:
            print("Please provide a query string with --query.")
            exit(1)

    elif args.action == "SearchFor":
        if args.query:
            for doc in k_search.search(args.query, fl=args.fl):
                print(doc)
        else:
            print("Please provide a query string with --query.")
            exit(1)


if __name__ == "__main__":
    main()
