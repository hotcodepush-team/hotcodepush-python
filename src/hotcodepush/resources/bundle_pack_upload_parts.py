from __future__ import annotations

from .._http import UploadBody, resolve_path
from ..models import UploadedPart
from ._base import BaseResource


class BundlePackUploadPartsResource(BaseResource):
    def upload(
        self,
        *,
        app_id: str,
        body: UploadBody,
        bundle_id: str,
        content_length: int | None = None,
        part_number: int,
        upload_id: str,
    ) -> UploadedPart:
        """Uploads one part of a multipart pack upload; its `etag` and `part_number` complete
        the upload.

        A file object `body` needs its `content_length`; bytes carry their own.
        """
        return self._http_client.fetch_upload(
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads/{uploadId}/parts/{partNumber}",
                appId=app_id,
                bundleId=bundle_id,
                partNumber=part_number,
                uploadId=upload_id,
            ),
            UploadedPart,
            body=body,
            content_length=content_length,
            content_type="application/x-tar",
        )
