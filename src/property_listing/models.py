from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from property_listing.utils import CleanedHTMLString
class PropertyDescription(BaseModel):
    name: str
    headline: str
    description: CleanedHTMLString 

class RentalInfo(BaseModel):
    max_guests: int
    bedrooms: int
    bathrooms: int

class PropertyLocation(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float

class PropertyPolicies(BaseModel):
    cancellation_policy: Optional[str] = None
    payment_schedule: Optional[str] = None
    damage_deposit: Optional[str] = None

class HouseRules(BaseModel):
    check_in_time: str
    check_out_time: str


class PropertyInput(BaseModel):
    property_id: int
    property_name: str
    property_type: str
    description: PropertyDescription
    amenities: List[str]
    image_urls: List[HttpUrl] 
    reviews: List[str]
    num_of_reviews: int
    average_review_score: float
    rental_info: RentalInfo
    location: PropertyLocation
    policies: PropertyPolicies
    house_rules: HouseRules

class MarketingCopy(BaseModel):
    slug_headline: str = Field(description="A compelling marketing headline.")
    hero_paragraph: str = Field(description="A 3-sentence description emphasizing the location and vibe.")
    amenity_highlights: List[str] = Field(description="Exactly 3 key highlights mapped to verified amenities.")
    guest_expectations: str = Field(description="A brief summary of check-in/out and key rules.")



# Eval schemas

class ClaimAudit(BaseModel):
    claim: str = Field(
        description="A specific factual statement extracted from the marketing copy."
    )
    verdict: bool = Field(
        description="True if the claim is explicitly supported by the raw data; False if it is invented or exaggerated."
    )
    reason: str = Field(
        description="A brief explanation citing where the fact is located in the data, or explaining why it is a hallucination."
    )

class GroundednessEval(BaseModel):
    audit_checks: List[ClaimAudit] = Field(
        description="The complete list of factual claims extracted from the copy and immediately verified against the raw data."
    )

