import pytest
from services.guardrails.role_leakage import leakage_check

@pytest.mark.asyncio
async def test_leakage_check_finance():
    passed, msg = await leakage_check("Revenue is $1,000", ["finance"], "finance")
    assert passed

@pytest.mark.asyncio
async def test_leakage_check_marketing_blocked():
    passed, msg = await leakage_check("def calculate_budget(): pass", ["engineering"], "marketing")
    assert not passed
