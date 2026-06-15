import pytest
from unittest.mock import MagicMock
from src.generators import MarketingCopyPipeline
from src.models import GeneratedMarketingCopy

def test_anthropic_generator_pipeline(fake_property_input):
    # 1. ARRANGE: Mock the nested Anthropic message response structure
    mock_client = MagicMock()
    mock_tool_use = MagicMock()
    mock_tool_use.type = "tool_use"
    
    # Fake the dictionary that comes back from Claude's tool block
    mock_tool_use.input = {
        "slug_headline": "Stunning Luxury Villa",
        "hero_paragraph": "Enjoy a beautiful vacation here.",
        "amenity_highlights": ["Fast Wifi", "Pool", "Ocean View"],
        "guest_expectations": "Check-in at 3 PM, no smoking."
    }
    
    mock_response = MagicMock()
    mock_response.content = [mock_tool_use]
    mock_client.messages.create.return_value = mock_response
    
    # 2. ACT: Inject the mock client
    pipeline = MarketingCopyPipeline(llm_client=mock_client)
    result = pipeline.generate(fake_property_input)
    
    # 3. ASSERT: Structural verification
    assert isinstance(result, GeneratedMarketingCopy)
    assert result.slug_headline == "Stunning Luxury Villa"
    assert len(result.amenity_highlights) == 3
    mock_client.messages.create.assert_called_once()