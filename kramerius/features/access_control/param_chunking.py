"""
Rights ``/rights/params`` ``objects`` are stored as a single VARCHAR (e.g. 1024
chars) with a **1-character delimiter** between values. Large actor ``ips``
lists are split into multiple param rows (and matching actor copies) with
descriptions ``"{base} - {n}."``.
"""

from __future__ import annotations

import re

from kramerius.features.access_control.models import Actor

# Server / app storage limit for the joined ``objects`` string.
PARAM_OBJECTS_MAX_JOINED_LENGTH: int = 1024
# Delimiter length between serialized object entries in the DB (one char).
PARAM_OBJECTS_DELIMITER_LENGTH: int = 1

# Push suffix for chunk n (1-based). Export merge recognises this pattern.
PARAM_DESCRIPTION_CHUNK_SUFFIX_RE = re.compile(r"^(.+) - (\d+)\.$")


def joined_objects_storage_length(
    parts: list[str],
    *,
    delimiter_length: int = PARAM_OBJECTS_DELIMITER_LENGTH,
) -> int:
    """Length of ``parts`` joined with a ``delimiter_length`` separator."""
    if not parts:
        return 0
    return sum(len(p) for p in parts) + delimiter_length * (len(parts) - 1)


def chunk_strings_for_storage_limit(
    items: list[str],
    *,
    max_joined_length: int = PARAM_OBJECTS_MAX_JOINED_LENGTH,
    delimiter_length: int = PARAM_OBJECTS_DELIMITER_LENGTH,
) -> list[list[str]]:
    """
    Partition ``items`` (order preserved) so each chunk's joined length
    is at most ``max_joined_length``.
    """
    if max_joined_length < 1:
        raise ValueError("max_joined_length must be >= 1")
    chunks: list[list[str]] = []
    current: list[str] = []

    for s in items:
        if len(s) > max_joined_length:
            raise ValueError(
                f"Single IP/pattern longer than {max_joined_length} chars: "
                f"{s!r}"
            )
        trial = current + [s]
        trial_len = joined_objects_storage_length(
            trial, delimiter_length=delimiter_length
        )
        if trial_len <= max_joined_length:
            current = trial
        else:
            if current:
                chunks.append(current)
            current = [s]

    if current:
        chunks.append(current)
    return chunks


def format_param_chunk_actor_name(base_name: str, chunk_index: int) -> str:
    """``chunk_index`` is 1-based (``… - 1.``, ``… - 2.``, …)."""
    b = (base_name or "").strip() or "access-control"
    return f"{b} - {chunk_index}."


def expand_actors_for_rights_param_storage(
    actors: list[Actor],
    *,
    max_joined_length: int = PARAM_OBJECTS_MAX_JOINED_LENGTH,
    delimiter_length: int = PARAM_OBJECTS_DELIMITER_LENGTH,
) -> list[Actor]:
    """
    Replace actors with long ``ips`` by several actors (same ``roles`` /
    ``actions``) with chunked ``ips`` and suffixed ``name`` values.

    Single-chunk actors are unchanged. This runs at the start of
    ``push-access-control`` so roles, params, and rights all use the divided
    configuration.
    """
    out: list[Actor] = []
    for a in actors:
        ips = list(a.ips) if a.ips else []
        if not ips:
            out.append(a)
            continue

        chunks = chunk_strings_for_storage_limit(
            ips,
            max_joined_length=max_joined_length,
            delimiter_length=delimiter_length,
        )
        if len(chunks) == 1:
            out.append(a)
            continue

        for i, chunk in enumerate(chunks, start=1):
            out.append(
                a.model_copy(
                    update={
                        "name": format_param_chunk_actor_name(a.name, i),
                        "ips": chunk,
                    }
                )
            )
    return out
