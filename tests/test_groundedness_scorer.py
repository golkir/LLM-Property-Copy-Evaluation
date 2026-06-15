import pytest
from inspect_ai.scorer import Target
from inspect_ai.solver import TaskState

from property_listing.generator import PropertyCopyGenerator
from property_listing.eval.scorers import groundedness_scorer_cot

from fixtures import sample_property, sample_output, mock_llm, groundedness_output


@pytest.mark.asyncio
async def test_groundedness_scorer(sample_property, sample_output, mock_llm, groundedness_output):
    mock_llm.generate_structured.return_value = groundedness_output
    scorer = groundedness_scorer_cot(mock_llm)
    state = TaskState(
        metadata={
            "raw_input_data": sample_property,
            "generated_copy_json": sample_output
        },
        output=None,
        model = "fake",
        sample_id= 5,
        epoch=2,
        input = "",
        messages=[]

    )
    
    score = await scorer(state, "")
    
    assert score.value <= 0.7 # 2 correct claims, 1 incorrect = 2/3
    assert "Detailed Audit Log" in score.explanation
    assert "PASSED" in score.explanation


