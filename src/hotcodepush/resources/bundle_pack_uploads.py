from __future__ import annotations

from .._http import HttpClient, resolve_path
from ..models import MultipartUpload, UploadedBundlePack, UploadedPart
from ._base import BaseResource
from .bundle_pack_upload_parts import BundlePackUploadPartsResource


class BundlePackUploadsResource(BaseResource):
    """The multipart upload of a pack above the request body limit: create, upload the parts,
    complete, or delete to abort.
    """

    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.parts = BundlePackUploadPartsResource(http_client)

    def complete(
        self, *, app_id: str, bundle_id: str, parts: list[UploadedPart], upload_id: str
    ) -> UploadedBundlePack:
        """Assembles the parts into the pack, replacing one uploaded before.

        R2 refuses a second completion, so the call is never retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads/{uploadId}/complete",
                appId=app_id,
                bundleId=bundle_id,
                uploadId=upload_id,
            ),
            UploadedBundlePack,
            body={"parts": parts},
        )

    def create(self, *, app_id: str, bundle_id: str) -> MultipartUpload:
        """Starts a multipart upload of the pack; every part but the last is at least five
        mebibytes, all of one size.

        The start holds no state, and an upload a repeat leaves unused expires by the bucket's
        default, so the call is retried.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads",
                appId=app_id,
                bundleId=bundle_id,
            ),
            MultipartUpload,
            is_retryable=True,
        )

    def delete(self, *, app_id: str, bundle_id: str, upload_id: str) -> None:
        """Aborts a multipart pack upload, discarding its parts."""
        self._http_client.fetch_status(
            "DELETE",
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack/uploads/{uploadId}",
                appId=app_id,
                bundleId=bundle_id,
                uploadId=upload_id,
            ),
        )
