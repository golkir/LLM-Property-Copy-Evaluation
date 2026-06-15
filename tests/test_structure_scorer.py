import asyncio
import pytest
import json


from property_listing.eval.scorers import structure_scorer


class MockState:
    def __init__(self, metadata):
        self.metadata = metadata


class MockTarget:
    pass


def run_scorer(payload):
    scorer_fn = structure_scorer()
    state = MockState(metadata={"generated_copy_json": payload})
    target = MockTarget()
    return pytest.run(asyncio.run(scorer_fn(state, target)))


@pytest.mark.asyncio
async def test_invalid_json():
    scorer_fn = structure_scorer()

    state = MockState({"generated_copy_json": "{invalid json"})
    target = MockTarget()

    result = await scorer_fn(state, target)

    assert result.value == 0.0
    assert "Invalid JSON" in result.explanation


@pytest.mark.asyncio
async def test_schema_invalid():
    scorer_fn = structure_scorer()

    payload = json.dumps(
        {
            "slug_headline": "Nice stay",
            # missing required fields
        }
    )

    state = MockState({"generated_copy_json": payload})
    target = MockTarget()

    result = await scorer_fn(state, target)

    assert result.value == 0.0
    assert "Schema validation failed" in result.explanation


@pytest.mark.asyncio
async def test_constraint_violation():
    scorer_fn = structure_scorer()

    payload = json.dumps(
        {
            "slug_headline": "Nice stay",
            "hero_paragraph": "A great place. Very central. Close to transport.",
            "amenity_highlights": ["WiFi", "Pool"],  # invalid: only 2
            "guest_expectations": "Check-in after 3pm",
        }
    )

    state = MockState({"generated_copy_json": payload})
    target = MockTarget()

    result = await scorer_fn(state, target)

    assert result.value == 0.5
    assert "wrong amenity count" in result.explanation


@pytest.mark.asyncio
async def test_valid_output():
    scorer_fn = structure_scorer()

    payload = json.dumps(
        {
            "slug_headline": "Luxury stay in Madrid",
            "hero_paragraph": "Central location. Stylish interiors. Walkable neighborhood.",
            "amenity_highlights": ["WiFi", "Gym", "Pool"],
            "guest_expectations": "Check-in after 3pm. No smoking.",
        }
    )

    state = MockState({"generated_copy_json": payload})
    target = MockTarget()

    result = await scorer_fn(state, target)

    assert result.value == 1.0
    assert "satisfied" in result.explanation.lower()
