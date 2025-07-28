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
