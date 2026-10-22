from __future__ import annotations

from .._http import HttpClient, resolve_path
from ..models import AppFile, MultipartUpload, UploadedPart
from ._base import BaseResource
from .file_upload_parts import FileUploadPartsResource


class FileUploadsResource(BaseResource):
    """The multipart upload of a larger file: create, upload the parts, complete, or delete to
    abort.
    """

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.parts = FileUploadPartsResource(http_client)

    def complete(
        self, *, app_id: str, parts: list[UploadedPart], sha256: str, upload_id: str
    ) -> AppFile:
        """Assembles the parts into the file and checks its hash.

        A hash the app already holds answers the stored file before any assembly, so the call is
        retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/files/{sha256}/uploads/{uploadId}/complete",
                appId=app_id,
                sha256=sha256,
                uploadId=upload_id,
            ),
            AppFile,
            body={"parts": parts},
            is_retryable=True,
        )

    def create(self, *, app_id: str, sha256: str) -> MultipartUpload:
        """Starts a multipart upload; every part but the last is at least five mebibytes, all of
        one size.

        The start holds no state, and an upload a repeat leaves unused expires by the bucket's
        default, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path("/v1/apps/{appId}/files/{sha256}/uploads", appId=app_id, sha256=sha256),
            MultipartUpload,
            is_retryable=True,
        )

    def delete(self, *, app_id: str, sha256: str, upload_id: str) -> None:
        """Aborts a multipart upload, discarding its parts."""
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/apps/{appId}/files/{sha256}/uploads/{uploadId}",
                appId=app_id,
                sha256=sha256,
                uploadId=upload_id,
            ),
        )
