from __future__ import annotations

from .._http import HttpClient, UploadBody, resolve_path
from .._upload import is_above_single_upload_limit, upload_in_parts
from ..models import UploadedBundlePack
from ._base import BaseResource
from .bundle_pack_uploads import BundlePackUploadsResource


class BundlePackResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.uploads = BundlePackUploadsResource(http_client)

    def upload(
        self,
        *,
        app_id: str,
        body: UploadBody,
        bundle_id: str,
        content_length: int | None = None,
    ) -> UploadedBundlePack:
        """Uploads the full pack of the bundle, a tar, before the bundle is completed.

        Bytes above `SINGLE_UPLOAD_LIMIT_BYTES` go up in parts. A file object goes up in one
        request, so it must stay within that limit and needs its `content_length`.
        """
        if is_above_single_upload_limit(body):
            return upload_in_parts(
                body,
                complete=lambda upload_id, parts: self.uploads.complete(
                    app_id=app_id, bundle_id=bundle_id, parts=parts, upload_id=upload_id
                ),
                create=lambda: self.uploads.create(app_id=app_id, bundle_id=bundle_id),
                delete=lambda upload_id: self.uploads.delete(
                    app_id=app_id, bundle_id=bundle_id, upload_id=upload_id
                ),
                upload_part=lambda upload_id, part_number, part: self.uploads.parts.upload(
                    app_id=app_id,
                    body=part,
                    bundle_id=bundle_id,
                    part_number=part_number,
                    upload_id=upload_id,
                ),
            )
        return self._http_client.fetch_upload(
            resolve_path(
                "/v1/apps/{appId}/bundles/{bundleId}/pack", appId=app_id, bundleId=bundle_id
            ),
            UploadedBundlePack,
            body=body,
            content_length=content_length,
            content_type="application/x-tar",
        )
