from fastapi import FastAPI, HTTPException, Header
from backend.config import API_KEY
from backend.models import run_targeted_prompt, run_extraction_basic, run_hybrid_prompt
from backend.schemas import ExtractResponse, ExtractRequestTargeted, ExtractRequest, ExtractRequestHybrid, CleanedExtractResponse

app = FastAPI(title="Attribute Extraction API")

@app.post("/extract", response_model=ExtractResponse)
async def extract_endpoint(request: ExtractRequest, x_api_key: str = Header(None)):
    # API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Run the extraction function (returns a Pydantic model)
    attributes = run_extraction_basic(request.title, request.description)
    return attributes

@app.post("/extract-targeted", response_model=ExtractResponse)
async def extract_endpoint(request: ExtractRequestTargeted, x_api_key: str = Header(None)):
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
async def extract_endpoint(request: ExtractRequestHybrid, x_api_key: str = Header(None)):
    # API key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

    # Run the extraction function (returns a Pydantic model)
    non_targeted_output = run_extraction_basic(request.title, request.description)
    targeted_output = run_targeted_prompt(request.title, request.description, request.schema_attributes)

    attributes = run_hybrid_prompt(request.title, request.description, non_targeted_output, targeted_output)
    return attributes