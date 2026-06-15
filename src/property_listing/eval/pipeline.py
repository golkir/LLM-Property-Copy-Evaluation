import json
from pathlib import Path
from typing import List


from inspect_ai import Task, task, eval
from inspect_ai.dataset import Sample, MemoryDataset

from property_listing.generator import PropertyCopyGenerator, run_generation_pipeline
from property_listing.services.llm import AnthropicService
from property_listing.eval.scorers import groundedness_scorer_cot, structure_scorer

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "mock_data.json"


def load_properties(path: Path) -> List[dict]:
    with open(path, "r") as f:
        return json.load(f)


def build_dataset(properties: List[dict]) -> MemoryDataset:
    return MemoryDataset(
        [
            Sample(
                id=str(p["property_id"]),
                input="",
                metadata={"property": p},
            )
            for p in properties
        ]
    )


@task
def property_copy_eval() -> Task:
    llm_service = AnthropicService()
    property_generator = PropertyCopyGenerator(llm_service=llm_service)

    properties = load_properties(DATA_PATH)
    dataset = build_dataset(properties)

    return Task(
        dataset=dataset,
        plan=[run_generation_pipeline(generator=property_generator)],
        scorer=[groundedness_scorer_cot(), structure_scorer()],
    )


def run_eval():
    evaluation_results = eval(tasks=[property_copy_eval])
    print(f"Evaluation Complete! Log written to: {evaluation_results[0].location}")
    return evaluation_results


if __name__ == "__main__":
    run_eval()
