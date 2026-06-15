import json
from inspect_ai import Task, task
from inspect_ai.dataset import json_dataset, FieldSpec, Sample, MemoryDataset
from inspect_ai.scorer import multi_scorer

from property_listing.generator import PropertyCopyGenerator, run_generation_pipeline
from property_listing.services.llm import GeminiService
from property_listing.eval.scorers import groundedness_scorer_cot

with open("../../data/mock_data.json") as f:
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
        scorer = groundedness_scorer_cot()
        # scorer=multi_scorer(
        #     scorers=[
        #         groundedness_scorer_cot()
        #         # structure_scorer()
        #     ],
        #     reducer="mean"
        # )
    )


def run_eval():
    evaluation_results = eval(tasks="src/property_listing/eval/eval_pipeline.py")
    print(f"Evaluation Complete! Log written to: {evaluation_results[0].location}")
    return evaluation_results