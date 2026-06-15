import pytest
from property_listing.generator import PropertyCopyGenerator, run_generation_pipeline
from property_listing.models import MarketingCopy


def test_property_copy_generator(sample_property, mock_llm):
    generator = PropertyCopyGenerator(llm_service=mock_llm)

    result = generator.generate(sample_property)

    assert isinstance(result, MarketingCopy)
    assert result.slug_headline == "Stay in Madrid"
    assert len(result.amenity_highlights) == 3
    assert "Check-in after 3pm" in result.guest_expectations


def test_llm_called_with_correct_args(sample_property, mock_llm):
    generator = PropertyCopyGenerator(llm_service=mock_llm)

    generator.generate(sample_property)

    mock_llm.generate_structured.assert_called_once()

    _, kwargs = mock_llm.generate_structured.call_args

    assert kwargs["response_schema"] == MarketingCopy
    assert "prompt" in kwargs
    assert "system_instruction" in kwargs


@pytest.mark.asyncio
async def test_solver_stage(mock_llm, sample_property):
    generator = PropertyCopyGenerator(llm_service=mock_llm)

    stage = run_generation_pipeline(generator)

    class MockState:
        metadata = {"property": sample_property.model_dump(mode="json")}

    state = MockState()

    result = await stage(state, None)

    assert "generated_copy_json" in result.metadata
    assert "raw_input_data" in result.metadata
