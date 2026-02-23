from pydantic import BaseModel, Field, HttpUrl

DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_TIMEOUT = 15
DEFAULT_MAX_ACTIVE_PROCESSES = 2


class KrameriusConfig(BaseModel):
    host: HttpUrl
    solr_cloud: bool = False
    client_id: str | None = None
    service_account_secret: str | None = None
    keycloak_host: HttpUrl | None = None
    client_secret: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int = Field(
        30, ge=0, le=300, description="Timeout for HTTP requests in seconds."
    )
    max_retries: int = Field(
        5,
        ge=0,
        le=10,
        description="Maximum number of retries for failed requests.",
    )
    retry_timeout: int = Field(
        15, ge=2, le=60, description="Timeout for retries in seconds."
    )
    max_active_processes: int = Field(
        2, ge=1, description="Maximum number of concurrent processes."
    )
