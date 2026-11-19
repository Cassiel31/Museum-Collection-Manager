from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.models.staff import StaffCreate
from app.models.restoration import RestorationCreate
from app.models.condition_history import ConditionHistoryCreate

from app.services import staff, restoration, condition
from app.routes.conservation_pages import router


# Fake Supabase query: no real database operations are performed.
class FakeQuery:
    def __init__(self, data=None):
        self.data = data if data is not None else []
        self.calls = []

    def select(self, *args, **kwargs):
        self.calls.append(("select", args, kwargs))
        return self

    def order(self, *args, **kwargs):
        self.calls.append(("order", args, kwargs))
        return self

    def eq(self, *args, **kwargs):
        self.calls.append(("eq", args, kwargs))
        return self

    def limit(self, *args, **kwargs):
        self.calls.append(("limit", args, kwargs))
        return self

    def insert(self, data):
        self.calls.append(("insert", data))
        return self

    def update(self, data):
        self.calls.append(("update", data))
        return self

    def delete(self):
        self.calls.append(("delete",))
        return self

    def execute(self):
        return SimpleNamespace(data=self.data)


class FakeSupabase:
    def __init__(self, data=None):
        self.query = FakeQuery(data)
        self.tables = []

    def table(self, name):
        self.tables.append(name)
        return self.query


# MODEL VALIDATION TESTS

def test_valid_staff_member():
    staff_member = StaffCreate(
        full_name="Aarav Sharma",
        email="aarav@example.com",
        role="Conservator",
        date_joined=date(2025, 1, 10),
    )
    assert staff_member.full_name == "Aarav Sharma"


def test_staff_name_must_have_at_least_two_characters():
    with pytest.raises(ValidationError):
        StaffCreate(
            full_name="A",
            email="a@example.com",
            role="Curator",
        )


def test_staff_role_must_be_valid():
    with pytest.raises(ValidationError):
        StaffCreate(
            full_name="Aarav Sharma",
            email="a@example.com",
            role="Director",
        )


def test_valid_restoration_record():
    record = RestorationCreate(
        artifact_id="ART-001",
        staff_id="STAFF-001",
        damage_description="Surface damage",
        restoration_start_date=date(2025, 2, 1),
        restoration_cost=Decimal("250.00"),
        status="Pending",
    )
    assert record.status == "Pending"


def test_restoration_cost_cannot_be_negative():
    with pytest.raises(ValidationError):
        RestorationCreate(
            artifact_id="ART-001",
            staff_id="STAFF-001",
            damage_description="Surface damage",
            restoration_start_date=date(2025, 2, 1),
            restoration_cost=Decimal("-10"),
        )


def test_restoration_status_must_be_valid():
    with pytest.raises(ValidationError):
        RestorationCreate(
            artifact_id="ART-001",
            staff_id="STAFF-001",
            damage_description="Surface damage",
            restoration_start_date=date(2025, 2, 1),
            status="Unknown",
        )


def test_valid_condition_history():
    record = ConditionHistoryCreate(
        artifact_id="ART-001",
        previous_condition="Good",
        new_condition="Fair",
        recorded_date=date(2025, 3, 1),
    )
    assert record.new_condition == "Fair"


def test_condition_history_rejects_invalid_condition():
    with pytest.raises(ValidationError):
        ConditionHistoryCreate(
            artifact_id="ART-001",
            previous_condition="Good",
            new_condition="Broken",
            recorded_date=date(2025, 3, 1),
        )


# SERVICE TESTS - MOCK DATABASE

def test_create_staff_calls_insert(monkeypatch):
    fake = FakeSupabase([{"staff_id": "STAFF-001"}])
    monkeypatch.setattr(staff, "supabase", fake)

    payload = StaffCreate(
        full_name="Aarav Sharma",
        email="aarav@example.com",
        role="Conservator",
    )

    result = staff.create_staff(payload)

    assert result["staff_id"] == "STAFF-001"
    assert fake.tables == ["staff"]
    assert fake.query.calls[0][0] == "insert"


def test_create_restoration_calls_insert(monkeypatch):
    fake = FakeSupabase([{"restoration_id": "REST-001"}])
    monkeypatch.setattr(restoration, "supabase", fake)

    payload = RestorationCreate(
        artifact_id="ART-001",
        staff_id="STAFF-001",
        damage_description="Surface damage",
        restoration_start_date=date(2025, 2, 1),
    )

    result = restoration.create_restoration(payload)

    assert result["restoration_id"] == "REST-001"
    assert fake.tables == ["restorations"]
    assert fake.query.calls[0][0] == "insert"


def test_delete_restoration_returns_true(monkeypatch):
    fake = FakeSupabase([{"restoration_id": "REST-001"}])
    monkeypatch.setattr(restoration, "supabase", fake)

    result = restoration.delete_restoration("REST-001")

    assert result is True
    assert fake.tables == ["restorations"]
    assert any(call[0] == "delete" for call in fake.query.calls)


def test_get_artifact_condition_history_filters_by_artifact(monkeypatch):
    fake = FakeSupabase([{"artifact_id": "ART-001"}])
    monkeypatch.setattr(condition, "supabase", fake)

    result = condition.get_artifact_condition_history("ART-001")

    assert len(result) == 1
    assert ("eq", ("artifact_id", "ART-001"), {}) in fake.query.calls


# ROUTE REGISTRATION TEST

def test_all_conservation_routes_are_registered():
    paths = {route.path for route in router.routes}

    expected = {
        "/conservation",
        "/conservation/restorations",
        "/conservation/restorations/create",
        "/conservation/staff",
        "/conservation/staff/create",
        "/conservation/condition-history",
        "/conservation/condition-history/create",
    }

    assert expected.issubset(paths)
