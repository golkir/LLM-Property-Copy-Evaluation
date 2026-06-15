from abc import ABC, abstractmethod
from property_listing.models import PropertyInput, MarketingCopy
from inspect_ai.solver import solver, Solver, TaskState, Generate
from property_listing.services.llm import LLMProviderService


class BaseGenerationPipeline(ABC):

    def __init__(self, llm_service: LLMProviderService):
        self.llm_service = llm_service

    @abstractmethod
    def generate(self, input_data: PropertyInput) -> MarketingCopy:
        pass


class PropertyCopyGenerator(BaseGenerationPipeline):

    def __init__(self, llm_service: LLMProviderService):

        super().__init__(llm_service=llm_service)

    def _build_prompt(self, property_data: PropertyInput) -> str:
        serialized_json = property_data.model_dump_json(indent=2)

        return f"""
You are an expert real estate copywriter specializing in vacation rentals. Your task is to transform raw property data into high-converting marketing copy.

Here is the verified data for the property you must write about:
<property_data>
{serialized_json}
</property_data>

CRITICAL INSTRUCTIONS AND RULES:
1. Grounding: You must ONLY use facts provided inside the <property_data> block. Do not invent amenities, nearby attractions, or scenery that is not explicitly supported by the input data.
2. Tone matching: Ensure the tone matches the `property_type` (e.g., an urban "NormalApartment" should feel convenient, while a "Villa" should feel exclusive/luxury).
3. Amenity Mapping: For the `amenity_highlights`, select exactly 3 items from the `amenities` array provided. Translate their internal codes (e.g., "InternetBroadband") into customer-facing phrases (e.g., "Blazing-fast High-Speed Internet").
4. Guest Expectations: Synthesize the `house_rules` and `policies` into a concise summary.

Generate the marketing copy based on these instructions and using provided output format in the tool arguments.
"""

    def generate(self, input_data: PropertyInput) -> MarketingCopy:
        prompt = self._build_prompt(input_data)
        system_instruction = "You are a professional real estate marketing engine that outputs strict JSON."

        raw_dict = self.llm_service.generate_structured(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=MarketingCopy,
        )

        return MarketingCopy(**raw_dict)


@solver
def run_generation_pipeline(generator: PropertyCopyGenerator) -> Solver:

    async def stage(state: TaskState, generate: Generate) -> TaskState:
       
        property_data = PropertyInput(**state.metadata["property"])
        state.metadata["raw_input_data"] = property_data.model_dump(mode="json")
        generated_copy = generator.generate(property_data)
        state.metadata["generated_copy_json"] = generated_copy.model_dump(mode="json")

        return state

    return stage
