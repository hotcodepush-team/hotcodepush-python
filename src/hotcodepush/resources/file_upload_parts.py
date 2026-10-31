from __future__ import annotations

from .._http import UploadBody, resolve_path
from ..models import UploadedPart
from ._base import BaseResource


class FileUploadPartsResource(BaseResource):
    def upload(
        self,
        *,
        app_id: str,
        body: UploadBody,
        content_length: int | None = None,
        part_number: int,
        sha256: str,
        upload_id: str,
    ) -> UploadedPart:
        """Uploads one part of a multipart upload.

        Pass the returned `etag` and `part_number` to complete the upload. A file object `body`
        needs its `content_length`.
        """
        return self._http_client.fetch_upload(
            resolve_path(
                "/v1/apps/{appId}/files/{sha256}/uploads/{uploadId}/parts/{partNumber}",
                appId=app_id,
                partNumber=part_number,
                sha256=sha256,
                uploadId=upload_id,
            ),
            UploadedPart,
            body=body,
            content_length=content_length,
            content_type="application/gzip",
        )
