from __future__ import annotations

from .._http import HttpClient, resolve_path
from ..models import MultipartUpload, UploadedBundlePack, UploadedPart
from ._base import BaseResource
from .bundle_pack_upload_parts import BundlePackUploadPartsResource


class BundlePackUploadsResource(BaseResource):
    """The multipart upload of a pack above the request body limit.

    Create the upload, upload the parts, then complete it, or delete it to abort.
    """

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.parts = BundlePackUploadPartsResource(http_client)

    def complete(
        self, *, app_id: str, bundle_id: str, parts: list[UploadedPart], upload_id: str
    ) -> UploadedBundlePack:
        """Assembles the parts into the pack, replacing any pack uploaded before.

        Never retried, since R2 refuses a second completion.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads/{uploadId}/complete",
                appId=app_id,
                bundleId=bundle_id,
                uploadId=upload_id,
            ),
            body={"parts": parts},
            response_type=UploadedBundlePack,
        )

    def create(self, *, app_id: str, bundle_id: str) -> MultipartUpload:
        """Starts a multipart upload of the pack.

        All parts but the last must have the same size, at least 5 MiB. Retried, since the start
        holds no state and the bucket expires an unused upload.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads",
                appId=app_id,
                bundleId=bundle_id,
            ),
            is_retryable=True,
            response_type=MultipartUpload,
        )

    def delete(self, *, app_id: str, bundle_id: str, upload_id: str) -> None:
        """Aborts a multipart pack upload and discards its parts."""
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads/{uploadId}",
                appId=app_id,
                bundleId=bundle_id,
                uploadId=upload_id,
            ),
        )
