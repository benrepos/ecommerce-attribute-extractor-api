from typing import List
from pydantic import BaseModel

class ExtractRequest(BaseModel):
    title: str
    description: str

class ExtractRequestTargeted(BaseModel):
    title: str
    description: str
    schema_attributes: List[str]

# Pydantic model for a single attribute
class Attribute(BaseModel):
    name: str
    value: List[str]

# Pydantic model for extraction response
class ExtractResponse(BaseModel):
    attributes: List[Attribute]

# Cleaned models including method attribution
class CleanedAttribute(BaseModel):
    name: str
    value: List[str]
    method: str  # 'non targeted', 'targeted', or 'non targeted; targeted'

class CleanedExtractResponse(BaseModel):
    attributes: List[CleanedAttribute]

class ExtractRequestHybrid(BaseModel):
    title: str
    description: str
    schema_attributes: List[str]
