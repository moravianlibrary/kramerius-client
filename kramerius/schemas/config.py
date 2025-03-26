from pydantic import BaseModel


class KrameriusConfig(BaseModel):
    host: str
    keycloak_host: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    username: str | None = None
    password: str | None = None
    timeout: int | None = None
    max_retries: int | None = None
    retry_timeout: int | None = None
