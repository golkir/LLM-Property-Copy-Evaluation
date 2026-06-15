import json
from pathlib import Path
from inspect_ai import Task, task, eval
from inspect_ai.dataset import json_dataset, FieldSpec, Sample, MemoryDataset
from inspect_ai.scorer import multi_scorer

from property_listing.generator import PropertyCopyGenerator, run_generation_pipeline
from property_listing.services.llm import GeminiService
from property_listing.eval.scorers import groundedness_scorer_cot, structure_scorer

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "mock_data.json"

with open(DATA_PATH) as f:
    properties = json.load(f)

dataset = MemoryDataset([
    Sample(
        id=str(property["property_id"]),
        input="",
        metadata={
            "property": property
        }
    )
    for property in properties
])


@task
def property_copy_eval() -> Task:
    llm_service = GeminiService(model_name="gemini-2.5-flash")
    property_generator = PropertyCopyGenerator(llm_service=llm_service)
    
    
    return Task(
        dataset=dataset,
        plan=[
            run_generation_pipeline(generator=property_generator)
        ],
        scorer=multi_scorer(
            scorers=[
                groundedness_scorer_cot(),
                structure_scorer()
            ],
            reducer="mean"
        )
    )


def run_eval():
    evaluation_results = eval(tasks=[property_copy_eval])
    print(f"Evaluation Complete! Log written to: {evaluation_results[0].location}")
    return evaluation_results


if __name__ == "__main__":
    run_eval()