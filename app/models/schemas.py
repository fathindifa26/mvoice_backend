from pydantic import BaseModel
from typing import List, Dict, Optional

class FilterOptions(BaseModel):
    business_units: List[str]
    brands: List[str]
    talent_types: List[str]
    date_range: Dict[str, Optional[str]]

class BrandMetric(BaseModel):
    name: str
    value: str

class TopBrandsResponse(BaseModel):
    our_brands: List[BrandMetric]
    competitor_brands: List[BrandMetric]

class CreativeItem(BaseModel):
    creative_id: str
    brand: str
    views: int
    date_post: str
    topic: Optional[str] = None
    hook_type: Optional[str] = None
    # Add other fields as needed
