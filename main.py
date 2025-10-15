"""
Main FastAPI application module.

This module defines the FastAPI app and its endpoints for handling requests.
"""
import os
from fastapi import FastAPI, HTTPException, Header
from backend.config import API_KEY
from backend.models import run_targeted_prompt, run_extraction_basic, run_hybrid_prompt
from backend.schemas import (
    ExtractResponse,
    ExtractRequestTargeted,
    ExtractRequest,
    ExtractRequestHybrid,
    CleanedExtractResponse
)

app = FastAPI(title="Attribute Extraction API")

@app.post("/extract", response_model=ExtractResponse)
async def extract_endpoint(request: ExtractRequest, x_api_key: str = Header(None)):
    """
    Endpoint to extract attributes from a product title and description.

    Args:
        request (ExtractRequest): The request body containing `title` and `description`.
        x_api_key (str, optional): API key sent in the header for authentication.

    Raises:
        HTTPException: Returns 403 if the API key is invalid.

    Returns:
        ExtractResponse: Extracted attributes as a Pydantic model.
    """
    # API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Run the extraction function (returns a Pydantic model)
    attributes = run_extraction_basic(request.title, request.description)
    return attributes

@app.post("/extract-targeted", response_model=ExtractResponse)
async def extract_targeted_endpoint(request: ExtractRequestTargeted, x_api_key: str = Header(None)):
    """
    Endpoint to extract attributes from a product title and description using a targeted approach.

    Args:
        request (ExtractRequestTargeted): The request body containing `title` and `description`.
        x_api_key (str, optional): API key sent in the header for authentication.

    Raises:
        HTTPException: Returns 403 if the API key is invalid.

    Returns:
        ExtractResponse: Extracted attributes as a Pydantic model.
    """
    # API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Run the extraction function (returns a Pydantic model)
    attributes = run_targeted_prompt(
        title=request.title,
        description=request.description,
        schema_attributes=request.schema_attributes
    )

    return attributes

@app.post("/extract-hybrid", response_model=CleanedExtractResponse)
async def extract_hybrid_endpoint(request: ExtractRequestHybrid, x_api_key: str = Header(None)):
    """
    Endpoint to extract attributes from a product title and description using a hybrid approach.

    Args:
        request (ExtractRequestHybrid): The request body containing `title` and `description`.
        x_api_key (str, optional): API key sent in the header for authentication.

    Raises:
        HTTPException: Returns 403 if the API key is invalid.

    Returns:
        CleanedExtractResponse: Extracted attributes as a Pydantic model.
    """
    # API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Run the extraction function (returns a Pydantic model)
    non_targeted_output = run_extraction_basic(request.title, request.description)
    targeted_output = run_targeted_prompt(
        title=  request.title,
        description=request.description,
        schema_attributes=request.schema_attributes
    )

    attributes = run_hybrid_prompt(
        title=request.title,
        description=request.description,
        non_targeted_output=non_targeted_output,
        targeted_output=targeted_output
    )

    return attributes


port = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
