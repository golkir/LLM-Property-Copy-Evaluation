import json
import re
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
from inspect_ai.scorer import scorer, Scorer, Target, Score
from inspect_ai.solver import TaskState
from inspect_ai.model import get_model, ChatMessageUser
from property_listing.models import MarketingCopy, GroundednessEval
from property_listing.services.llm import LLMProviderService
from property_listing.services.llm import GeminiService

class EvaluationJudgeOutput(BaseModel):
    reasoning: str = Field(description="Step-by-step audit comparing copy claims against source fields.")
    grade: int = Field(description="The numeric score assigned based strictly on the provided rubric.")

GROUNDEDNESS_RUBRIC = """
You are an expert quality assurance auditor evaluating a real estate property marketing assistant.
Compare the GENERATED MARKETING COPY against the verified RAW PROPERTY DATA and evaluate it for GROUNDEDNESS.

<property_data>
{source_data}
</property_data>

<generated_marketing_copy>
{generated_copy}
</generated_marketing_copy>

---
CRITERIA FOR SCORING:
- 5 (Perfectly Grounded): Every single claim in the marketing copy maps directly to an explicit field in the input data.
- 3 (Minor Extrapolation): The text includes minor subjective flair but makes no structural or numeric misstatements.
- 1 (Severe Hallucination): The model completely invented non-existent data points.
"""



# @scorer(metrics=[])
# def groundedness_scorer(judge_service: LLMProviderService) -> Scorer:
#     """
#     Custom Inspect AI Scorer that checks if marketing copy is strictly 
#     grounded in the underlying data structure.
#     """
#     async def score(state: TaskState, target: Target) -> Score:
#         source_data = state.metadata.get("raw_input_data")
#         generated_copy = state.output.text
#         prompt = GROUNDEDNESS_RUBRIC.format(
#             source_data=source_data,
#             generated_copy=generated_copy)
#         model = get_model(judge_service)
#         response = await model.generate([ChatMessageUser(content=prompt)])
#         judge_output = response.text
        
#         final_score = 1
#         if "GRADE: 5" in judge_output:
#             final_score = 5
#         elif "GRADE: 3" in judge_output:
#             final_score = 3
            
#         return Score(
#             value=final_score,
#             explanation=judge_output
#         )
#     return score


@scorer(metrics=[])
def groundedness_scorer_cot() -> Scorer:
    """
    Evaluates groundedness using LLM-as-a-Judge extracting each claim. 
    Groundedness assessment is done based on LLM per-claim verdict aggregation
    """
    async def score(state: TaskState, target: Target) -> Score:
        raw_source_data = state.metadata.get("raw_input_data")
        generated_copy_text = state.metadata["generated_copy_json"]
        
        if not raw_source_data or not generated_copy_text:
            return Score(value=0.0, explanation="Missing source data or generated output in state context.")

        evaluation_prompt = f"""
        You are a strict compliance quality control auditor. Your task is to evaluate the GROUNDEDNESS of the GENERATED MARKETING COPY against the verified RAW PROPERTY DATA.

        <property_data>
        {json.dumps(raw_source_data, indent=2, default=str)}
        <property_data>

        <generated_marketing_copy>
        {generated_copy_text}
        </generated_marketing_copy>

        ---
        INSTRUCTIONS:
        1. Read the marketing copy carefully. Identify and isolate every single distinct factual claim made (e.g., specific amenities, bed/bath metrics, location rules, proximity assertions).
        2. For each claim you extract, immediately check it against the raw property data.
        3. Populate the required schema where 'verdict' is true ONLY if the raw data explicitly confirms the claim. If the claim is missing, exaggerated, or invented, set 'verdict' to false.
        """

        judge_service = GeminiService(model_name="gemini-2.5-flash")
        
        evaluation_data = judge_service.generate_structured(
            prompt=evaluation_prompt,
            system_instruction="You are an expert AI data auditor that performs strict compliance verification.",
            response_schema=GroundednessEval
        )
        
        checks = evaluation_data.get("audit_checks", [])

        if not checks:
            return Score(value=1.0, explanation="Passed audit: The text contained no testable factual assertions.")

        total_claims = len(checks)
        grounded_claims = sum(1 for check in checks if check.get("verdict") is True)
        
        final_score = grounded_claims / total_claims

        audit_log = "\n".join([
            f"- [{ 'PASSED' if c.get('verdict') else 'FAILED' }] {c.get('claim')} -> {c.get('reason')}"
            for c in checks
        ])
        
        explanation_summary = (
            f"Groundedness Score: {final_score:.2f} ({grounded_claims}/{total_claims} claims verified in a single step).\n\n"
            f"Detailed Audit Log:\n{audit_log}"
        )

        return Score(
            value=final_score,
            explanation=explanation_summary,
            metadata={
                "audit_checks": checks, 
                "total_claims": total_claims, 
                "failed_claims": total_claims - grounded_claims
            }
        )

    return score

# @scorer(metrics=[])
# def structure_scorer() -> Scorer:
#     """
#     Validates if the generated marketing copy strictly adheres to 
#     the structure specified by the target Pydantic model schema.
#     """
#     async def score(state: TaskState, target: Target) -> Score:
#         raw_output = state.output.text.strip()
        
#         try:
#             if "```json" in raw_output:
#                 raw_output = raw_output.split("```json")[1].split("```")[0].strip()
            
#             json_data = json.loads(raw_output)
            
#             MarketingCopy(**json_data)
            
#             if len(json_data.get("amenity_highlights", [])) != 3:
#                 return Score(
#                     value=3, 
#                     explanation="Output is valid JSON but failed structural constraints (did not equal 3 highlights)."
#                 )
                
#             return Score(value=5, explanation="Perfectly structured valid JSON matching Pydantic schema.")
            
#         except (json.JSONDecodeError, ValidationError) as e:
#             return Score(value=1, explanation=f"Structural breakdown: Failed to parse valid JSON. Error: {str(e)}")

#     return score