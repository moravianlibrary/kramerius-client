"""Access-control YAML models and export from Kramerius admin API."""

from kramerius.features.access_control.push import push_access_control

__all__ = [
    "push_access_control",
]
