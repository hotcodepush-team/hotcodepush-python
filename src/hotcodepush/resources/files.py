from __future__ import annotations

from .._http import HttpClient, UploadBody, resolve_path
from .._upload import is_above_single_upload_limit, upload_in_parts
from ..models import AppFile
from ._base import BaseResource
from .file_uploads import FileUploadsResource


class FilesResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.uploads = FileUploadsResource(http_client)

    def upload(
        self,
        *,
        app_id: str,
        body: UploadBody,
        content_length: int | None = None,
        sha256: str,
    ) -> AppFile:
        """Uploads one file of the app.

        The body is the gzip-compressed file, and `sha256` is the hash of the uncompressed
        content. A hash the app already holds answers the existing file.

        Bytes above `SINGLE_UPLOAD_LIMIT_BYTES` go up in parts. A file object goes up in one
        request, so it must stay within that limit and needs its `content_length`.
        """
        if is_above_single_upload_limit(body):
            return upload_in_parts(
                body,
                complete=lambda upload_id, parts: self.uploads.complete(
                    app_id=app_id, parts=parts, sha256=sha256, upload_id=upload_id
                ),
                create=lambda: self.uploads.create(app_id=app_id, sha256=sha256),
                delete=lambda upload_id: self.uploads.delete(
                    app_id=app_id, sha256=sha256, upload_id=upload_id
                ),
                upload_part=lambda upload_id, part_number, part: self.uploads.parts.upload(
                    app_id=app_id,
                    body=part,
                    part_number=part_number,
                    sha256=sha256,
                    upload_id=upload_id,
                ),
            )
        return self._http_client.fetch_upload(
            resolve_path("/v1/apps/{appId}/files/{sha256}", appId=app_id, sha256=sha256),
            AppFile,
            body=body,
            content_length=content_length,
            content_type="application/gzip",
        )
