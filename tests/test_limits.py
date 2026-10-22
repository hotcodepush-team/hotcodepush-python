import httpx

from hotcodepush import Limit
from tests.stub_api import StubApi


def test_gets_the_limits_in_effect() -> None:
    api = StubApi(
        httpx.Response(
            200, json={"appCountLimit": {"default": 5, "isOverridden": True, "value": 20}}
        )
    )

    fetched_limits = api.client.organizations.limits.get(organization_id="organization")

    assert fetched_limits == {"appCountLimit": Limit(default=5, is_overridden=True, value=20)}
    assert api.sent_methods_and_urls == [
        "GET https://api.hotcodepush.com/v1/organizations/organization/limits"
    ]
