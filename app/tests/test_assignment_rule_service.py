from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4

from app.services.assignment_rule_service import AssignmentRuleService


class Dummy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_rule_matching_priority_and_stop_processing():
    svc = AssignmentRuleService(None)
    tx = Dummy(
        character_fk=uuid4(),
        is_buy=False,
        type_id=34,
        location_id=60003760,
        client_id=900,
        total_price=Decimal("2000000"),
        date=datetime(2026, 1, 10, tzinfo=UTC),
    )
    rule = Dummy(
        conditions_json={"is_buy": False, "type_ids": [34], "date_from": "2026-01-01", "date_to": "2026-12-31"},
    )
    assert svc._rule_matches_tx(rule, tx)
