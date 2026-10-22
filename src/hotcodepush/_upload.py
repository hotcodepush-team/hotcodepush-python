"""The single-or-parts rule of an upload: bytes above the single-upload limit go up in parts."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import TypeGuard, TypeVar

from ._http import UploadBody
from .models import MultipartUpload, UploadedPart

PART_SIZE_BYTES = 10 * 1024 * 1024
"""Every part but the last is this size: at least five mebibytes and all of one size, the bucket's
rule."""
SINGLE_UPLOAD_LIMIT_BYTES = 64 * 1024 * 1024
"""Bytes go up in one request up to this size and in parts above it, well under the request-body
cap of the API's plan."""

T = TypeVar("T")


def is_above_single_upload_limit(body: UploadBody) -> TypeGuard[bytes]:
    """A file object is read once and cannot be split, so only bytes go up in parts."""
    return isinstance(body, bytes) and len(body) > SINGLE_UPLOAD_LIMIT_BYTES


def upload_in_parts(
    body: bytes,
    *,
    complete: Callable[[str, list[UploadedPart]], T],
    create: Callable[[], MultipartUpload],
    delete: Callable[[str], None],
    upload_part: Callable[[str, int, bytes], UploadedPart],
) -> T:
    """Uploads bytes in parts of `PART_SIZE_BYTES`, numbered from 1, then completes the upload;
    a failed part or completion deletes the upload and re-raises.

    Each callable is one call of the multipart upload the files and the pack share, bound to the
    path parameters of its target.
    """
    upload_id = create().upload_id
    try:
        uploaded_parts = [
            upload_part(upload_id, part_number, body[start : start + PART_SIZE_BYTES])
            for part_number, start in enumerate(range(0, len(body), PART_SIZE_BYTES), start=1)
        ]
        return complete(upload_id, uploaded_parts)
    except Exception:
        with suppress(Exception):
            delete(upload_id)
        raise
