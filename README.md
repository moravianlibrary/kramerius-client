# Kramerius API Client

A Python client library for interacting with the [Kramerius](https://github.com/ceskaexpedice/kramerius) digital library system API.

This client provides convenient access to various Kramerius API modules, including items management, processes, search, SDNNT functionality, and statistics retrieval.

---

## Features

* Supports token-based authentication via Keycloak
* Handles request retries and error handling transparently
* Thread-safe HTTP requests with locking
* Modular sub-clients for:

  * Items management
  * Processes management
  * SDNNT publishing
  * Solr-powered search
  * Repository statistics
* Configurable request timeouts and pagination
* Pydantic-based configuration and data models

---

## Installation

### Installing from GitHub using version tag

You can install **kramerius** library directly from GitHub for a specific version tag:

```bash
pip install git+https://github.com/moravianlibrary/kramerius-client.git@v1.2.3
```

*Replace `v1.2.3` with the desired version tag.*

To always install the most recent version, use the latest tag:

```bash
pip install git+https://github.com/moravianlibrary/kramerius-client.git@latest
```

### Installing local dev environment

Install required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Usage

### As Kramerius client

After installing the package, you can run the CLI directly using:
```bash
kramerius-client
```

To see available options and commands, run:
```bash
kramerius-client --help

 Usage: python -m kramerius [OPTIONS] COMMAND [ARGS]...

 Kramerius CLI

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --host                        TEXT     Kramerius server host [env var: K7_HOST]                                     │
│ --keycloak-host               TEXT     Keycloak server host [env var: K7_KEYCLOAK_HOST]                             │
│ --client-id                   TEXT     Keycloak client ID [env var: K7_CLIENT_ID]                                   │
│ --client-secret               TEXT     Keycloak client secret [env var: K7_CLIENT_SECRET]                           │
│ --username                    TEXT     Username for authentication with Keycloak [env var: K7_USERNAME]             │
│ --password                    TEXT     Password for authentication with Keycloak [env var: K7_PASSWORD]             │
│ --timeout                     INTEGER  Request timeout in seconds [env var: K7_TIMEOUT] [default: 30]               │
│ --max-retries                 INTEGER  Maximum number of retries for failed requests [env var: K7_MAX_RETRIES]      │
│                                        [default: 5]                                                                 │
│ --retry-timeout               INTEGER  Timeout between retries in seconds [env var: K7_RETRY_TIMEOUT] [default: 30] │
│ --max-active-processes        INTEGER  Maximum number of active processes                                           │
│ --log-dir                     PATH     Directory for storing run logs [default: /tmp]                               │
│ --pidlist-size                INTEGER  Maximum size of the PID list [default: 3000]                                 │
│ --install-completion                   Install completion for the current shell.                                    │
│ --show-completion                      Show completion for the current shell, to copy it or customize the           │
│                                        installation.                                                                │
│ --help                                 Show this message and exit.                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ get-document                                                                                                        │
│ get-num-found                                                                                                       │
│ search-for                                                                                                          │
│ get-sdnnt-changes                                                                                                   │
│ run-sdnnt-sync                                                                                                      │
│ get-process                                                                                                         │
│ search-statistics                                                                                                   │
│ add-license                                                                                                         │
│ remove-license                                                                                                      │
│ get-image                                                                                                           │
│ index-upgrade                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Notes:**
- Most CLI options can also be set via environment variables.
- You can use a `.env` file to set CLI options. Make sure to run the CLI from the directory where the `.env` file is located. Refer to `.env.template` in this repository for the correct format.
- Command-line options override environment variable values.

### As library

```python
from kramerius_client import KrameriusClient, KrameriusConfig

# Configure the client
config = KrameriusConfig(
    host="https://kramerius.example.org",
    keycloak_host="https://auth.example.org",
    client_id="my-client-id",
    client_secret="my-client-secret",
    username="user",
    password="pass",
    timeout=30,
    max_retries=5,
)

# Create the client instance
client = KrameriusClient(config)

# Example: Search documents
results = client.Search.query({"fulltext": "Masaryk"})

# Example: Get item metadata
metadata = client.Items.get_metadata("uuid:1234")
```

---

## Configuration

The client uses a `KrameriusConfig` Pydantic model to encapsulate connection parameters, including:

* `host`: Base URL of the Kramerius API
* `keycloak_host`: Base URL of the Keycloak authentication server (optional)
* `client_id`: OAuth client ID (optional)
* `client_secret`: OAuth client secret (optional)
* `username`: Username for Keycloak authentication (optional)
* `password`: Password for Keycloak authentication (optional)
* `timeout`: Request timeout in seconds (default: 30)
* `max_retries`: Maximum number of request retries (default: 5)

---

## Thread Safety

All HTTP requests are locked to ensure thread safety when used in multithreaded environments, particularly for token refresh and retry logic.
