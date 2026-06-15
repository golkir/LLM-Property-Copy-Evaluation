import json
import pytest
from unittest.mock import MagicMock
from property_listing.models import PropertyInput


@pytest.fixture
def sample_property():
    DATA_PATH = "./data/mock_data.json"

    with open(DATA_PATH) as f:
        properties = json.load(f)
    return PropertyInput(**properties[0])


@pytest.fixture
def sample_output():
    return {
        "slug_headline": "Stay in Madrid",
        "hero_paragraph": "Central location. Modern design. Great transport links.",
        "amenity_highlights": [
            "Blazing-fast Internet",
            "Air Conditioning",
            "Fully equipped kitchen",
        ],
        "guest_expectations": "Check-in after 3pm. No smoking.",
    }


@pytest.fixture
def mock_llm(sample_output):
    llm = MagicMock()
    llm.generate_structured.return_value = sample_output
    return llm


@pytest.fixture
def groundedness_output():
    return {
        "audit_checks": [
            {
                "claim": "High-Speed Internet available",
                "verdict": True,
                "reason": "Present in raw data",
            },
            {
                "claim": "Central AC available",
                "verdict": True,
                "reason": "Explicit in amenities",
            },
            {
                "claim": "Free parking included",
                "verdict": False,
                "reason": "Not present in raw data",
            },
        ]
    }
