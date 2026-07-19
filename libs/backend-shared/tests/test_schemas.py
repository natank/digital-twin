"""Tests for base schemas and the API response envelope."""

from backend_shared.schemas import ApiResponse, BaseSchema, PaginationMeta


class _Sample(BaseSchema):
    name: str


class _FakeOrmObject:
    """Stands in for a SQLAlchemy row (attribute access, not a dict)."""

    def __init__(self, name: str) -> None:
        self.name = name


def test_base_schema_reads_from_orm_attributes():
    schema = _Sample.model_validate(_FakeOrmObject("digital-twin"))
    assert schema.name == "digital-twin"


def test_ok_response_shape():
    response = ApiResponse.ok({"id": 1}, request_id="req_123")
    assert response.status == "success"
    assert response.data == {"id": 1}
    assert response.error is None
    assert response.meta.request_id == "req_123"
    assert response.meta.timestamp is not None


def test_fail_response_shape():
    response = ApiResponse.fail("AUTH_001", "Invalid credentials")
    assert response.status == "error"
    assert response.data is None
    assert response.error is not None
    assert response.error.code == "AUTH_001"
    assert response.error.message == "Invalid credentials"


def test_fail_response_carries_details():
    response = ApiResponse.fail("VALIDATION_001", "bad", details={"field": "email"})
    assert response.error is not None
    assert response.error.details == {"field": "email"}


def test_response_serializes_to_documented_envelope():
    payload = ApiResponse.ok({"x": 1}).model_dump()
    assert set(payload) == {"status", "data", "error", "meta"}
    assert set(payload["meta"]) == {"timestamp", "request_id"}


def test_pagination_has_more_is_true_when_records_remain():
    assert PaginationMeta(total=100, limit=20, offset=0).has_more is True


def test_pagination_has_more_is_false_on_last_page():
    assert PaginationMeta(total=100, limit=20, offset=80).has_more is False


def test_pagination_has_more_is_false_when_page_exceeds_total():
    assert PaginationMeta(total=5, limit=20, offset=0).has_more is False
