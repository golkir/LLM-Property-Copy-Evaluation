import json
from pydantic import BaseModel, Field, ValidationError
from inspect_ai.scorer import scorer, Scorer, Target, Score
from inspect_ai.solver import TaskState
from property_listing.models import MarketingCopy, GroundednessEval
from property_listing.services.llm import LLMProviderService
from property_listing.services.llm import GeminiService
from pydantic import ValidationError


@scorer(metrics=[])
def groundedness_scorer_cot(judge_service: LLMProviderService) -> Scorer:
    """
    Evaluates groundedness using LLM-as-a-Judge extracting each claim. 
    Groundedness assessment is done based on LLM per-claim verdict aggregation
    """

    judge_service = judge_service if judge_service else GeminiService(model_name="gemini-2.5-flash")

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



@scorer(metrics=[])
def structure_scorer() -> Scorer:
    """
    0.0 = Invalid JSON
    0.25 = Valid JSON but schema invalid
    0.6 = Valid schema but constraint violation
    1.0 = Fully correct output
    """

    async def score(state: TaskState, target: Target) -> Score:
        prop_copy = state.metadata.get("generated_copy_json", "")

        try:
            model = MarketingCopy.model_validate_json(prop_copy)
            amenity_count = len(model.amenity_highlights)
            if amenity_count != 3:
                return Score(
                    value=0.5,
                    explanation=f"Valid schema but wrong amenity count: {amenity_count} (expected 3)."
                )

            return Score(
                value=1,
                explanation="Valid JSON + schema + structural constraints satisfied."
            )

        except ValidationError as e:
            return Score(
                value=0.0,
                explanation=f"Schema validation failed: {str(e)}"
            )

    return score