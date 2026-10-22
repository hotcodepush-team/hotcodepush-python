import httpx

from hotcodepush import Count
from tests.openapi_document import resolve_response_example
from tests.stub_api import StubApi

AUDIT_LOG_ROWS = resolve_response_example("GET", "/v1/organizations/{organizationId}/audit-logs")
AUDIT_LOGS_URL = "https://api.hotcodepush.com/v1/organizations/organization/audit-logs"


def test_counts_the_rows_of_the_audit_log_under_the_filters() -> None:
    api = StubApi(httpx.Response(200, json={"count": 3}))

    fetched_count = api.client.organizations.audit_logs.count(
        actor_type="system", organization_id="organization", type="channel.*"
    )

    assert fetched_count == Count(count=3)
    assert api.sent_methods_and_urls == [
        f"GET {AUDIT_LOGS_URL}/count?actorType=system&type=channel.%2A"
    ]


def test_downloads_the_audit_log_under_the_filters_as_csv() -> None:
    api = StubApi(
        httpx.Response(
            200, content=b'"id","type"\n', headers={"Content-Type": "text/csv; charset=utf-8"}
        )
    )

    downloaded_csv = api.client.organizations.audit_logs.download_csv(
        organization_id="organization", type="channel.*"
    )

    assert downloaded_csv == b'"id","type"\n'
    assert api.sent_methods_and_urls == [f"GET {AUDIT_LOGS_URL}?format=csv&type=channel.%2A"]


def test_lists_the_audit_log_with_its_users_when_the_user_relation_is_set() -> None:
    api = StubApi(httpx.Response(200, json=AUDIT_LOG_ROWS))

    fetched_audit_logs = api.client.organizations.audit_logs.list(
        organization_id="organization", relations=["user"], user_id="user"
    )

    [fetched_audit_log] = fetched_audit_logs
    assert fetched_audit_log.user is not None
    assert api.sent_methods_and_urls == [f"GET {AUDIT_LOGS_URL}?relations=user&userId=user"]
