from __future__ import annotations

from .._http import HttpClient, resolve_path
from .._types import NOT_GIVEN, NotGiven
from ..models import App, Framework
from ._base import BaseResource
from .binaries import BinariesResource
from .bundles import BundlesResource
from .channels import ChannelsResource
from .devices import DevicesResource
from .files import FilesResource
from .releases import ReleasesResource
from .signing_keys import SigningKeysResource
from .statistics import StatisticsResource


class AppsResource(BaseResource):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.binaries = BinariesResource(http_client)
        self.bundles = BundlesResource(http_client)
        self.channels = ChannelsResource(http_client)
        self.devices = DevicesResource(http_client)
        self.files = FilesResource(http_client)
        self.releases = ReleasesResource(http_client)
        self.signing_keys = SigningKeysResource(http_client)
        self.statistics = StatisticsResource(http_client)

    def delete(self, *, app_id: str) -> None:
        """Soft-deletes an app: gone at once, hard-deleted after seven days.

        An API token answers `forbidden`; sign in with a session.
        """
        self._http_client.fetch_status("DELETE", resolve_path("/v1/apps/{appId}", appId=app_id))

    def get(self, *, app_id: str) -> App:
        return self._http_client.fetch_json(
            "GET", resolve_path("/v1/apps/{appId}", appId=app_id), App
        )

    def transfer(self, *, app_id: str, organization_id: str) -> App:
        """Moves an app to another organization the caller is an Admin of.

        A repeat answers `validation`, the app being in the target already, so the call is
        never retried.

        An API token answers `forbidden`; sign in with a session.
        """
        return self._http_client.fetch_json(
            "POST",
            resolve_path("/v1/apps/{appId}/transfer", appId=app_id),
            App,
            body={"organizationId": organization_id},
        )

    def update(
        self,
        *,
        app_id: str,
        channel_link_template: str | None | NotGiven = NOT_GIVEN,
        default_channel_id: str | NotGiven = NOT_GIVEN,
        framework: Framework | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
    ) -> App:
        """Edits the name, the framework, the default channel or the deep-link template behind
        the QR surfaces, a URI with a scheme and `{channelId}` exactly once.
        """
        return self._http_client.fetch_json(
            "PATCH",
            resolve_path("/v1/apps/{appId}", appId=app_id),
            App,
            body={
                "channelLinkTemplate": channel_link_template,
                "defaultChannelId": default_channel_id,
                "framework": framework,
                "name": name,
            },
        )
