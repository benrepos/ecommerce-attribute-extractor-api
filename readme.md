# Ecommerce Attribute Extractor API

A lightweight API that turns messy product titles/descriptions into clean, structured specification attributes. This helps ecommerce teams tags products with attribute data (e.g., Colour, Size, Material, IP Rating), power filters/search, and improve product discovery and analytics.

## Quick Start

### Requirements
- Python 3.11
- OpenAI API key

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `API_KEY`: Internal API key used for requests to this API (required) but can be set in env variables

### Install & Run (local, no Docker)
```bash
# Create & activate a virtual environment (example path)
/usr/bin/python3 -m venv .venv_clean
source .venv_clean/bin/activate

# Install dependencies
pip install -r requirements.txt

# Export env vars (example)
export OPENAI_API_KEY=your_openai_key
export API_KEY=your_internal_key

# Start the server
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

Open the docs at http://localhost:8080/docs

### Run with Docker (optional)
```bash
docker build -t ecommerce-attribute-extractor-api:latest .
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your_openai_key \
  -e API_KEY=your_internal_key \
  ecommerce-attribute-extractor-api:latest
```

### Deploy to Cloud Run (optional)
```bash
# Build remotely with Cloud Build (Artifact Registry suggested)
PROJECT_ID=your_project_id
AR_LOCATION=us
REPO=containers
IMAGE_URI="${AR_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/ecommerce-attribute-extractor-api:latest"

gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com

gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$AR_LOCATION" \
  --description="App containers" || true

gcloud builds submit --tag "$IMAGE_URI"

gcloud run deploy ecommerce-attribute-extractor-api \
  --image "$IMAGE_URI" \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_openai_key,API_KEY=your_internal_key
```

## API
All endpoints require the header `x-api-key: <API_KEY>`.

### POST /extract
- **Purpose**: Exploratory extraction. The model selects relevant specification attributes based on the product content.
- **Request body**:
```json
{
  "title": "string",
  "description": "string"
}
```
- **Response**: `ExtractResponse`
```json
{
  "attributes": [
    { "name": "Color", "value": ["Red", "White"] }
  ]
}
```
- Notes: Values are always a list of strings. Unknown values come back as ["N/A"].

### POST /extract-targeted
- **Purpose**: Targeted extraction. You supply attribute names; the model finds values for those names only.
- **Request body**:
```json
{
  "title": "string",
  "description": "string",
  "schema_attributes": ["Color", "Size", "Material"]
}
```
- **Response**: `ExtractResponse` (same shape as `/extract`).
- Notes: Only specified attributes are returned.

### POST /extract-hybrid
- **Purpose**: Hybrid cleaned output. Runs both exploratory and targeted extractions, then merges/cleans results with method provenance.
- **Request body**:
```json
{
  "title": "string",
  "description": "string",
  "schema_attributes": ["Color", "Size", "Material"],
  "non_targeted_output": {},
  "targeted_output": {}
}
```
- The endpoint internally runs both extractions and returns a cleaned, prioritized result.
- **Response**:
```json
{
  "attributes": [
    { "name": "Color", "value": ["Red", "White"], "method": "non targeted; targeted" }
  ]
}
```

## Notes
- Responses are strict JSON based on server-enforced schemas.
- Attribute names are concise (1–4 words). Values are normalized lists; multi-values appear as separate strings.
- If the model is uncertain or a value doesn’t exist, it returns ["N/A"].
- Tech used: OpenAI, FastAPI, Pydnatic with options for deployment using Docker and Cloud Run
