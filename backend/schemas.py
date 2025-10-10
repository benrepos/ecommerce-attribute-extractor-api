"""
Schemas module for the backend.

This module defines the schemas for the backend.
"""

from typing import List
from pydantic import BaseModel

class ExtractRequest(BaseModel):
    """
    Request schema for the extraction endpoint.
    """
    title: str
    description: str

class ExtractRequestTargeted(BaseModel):
    """
    Request schema for the targeted extraction endpoint.
    """
    title: str
    description: str
    schema_attributes: List[str]

# Pydantic model for a single attribute
class Attribute(BaseModel):
    """
    Schema for a single attribute.
    """
    name: str
    value: List[str]

# Pydantic model for extraction response
class ExtractResponse(BaseModel):
    """
    Response schema for the extraction endpoint.
    """
    attributes: List[Attribute]

# Cleaned models including method attribution
class CleanedAttribute(BaseModel):
    """
    Schema for a single cleaned attribute.
    """
    name: str
    value: List[str]
    method: str  # 'non targeted', 'targeted', or 'non targeted; targeted'

class CleanedExtractResponse(BaseModel):
    """
    Response schema for the cleaned extraction endpoint.
    """
    attributes: List[CleanedAttribute]

class ExtractRequestHybrid(BaseModel):
    """
    Request schema for the hybrid extraction endpoint.
    """
    title: str
    description: str
    schema_attributes: List[str]
