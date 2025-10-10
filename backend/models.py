"""
Models module for the backend.

This module defines the model functions for LLM extraction.
"""

import json
from openai import OpenAI
from backend.schemas import ExtractResponse, CleanedExtractResponse
from backend.config import OPENAI_API_KEY

def get_openai_client():
    """
    Set up the OpenAI client.
    """
    return OpenAI(api_key=OPENAI_API_KEY)

#Run the exploratory approach (LLM picks the names)
def run_extraction_basic(title: str, description: str) -> ExtractResponse:
    """
    Extract basic attributes from product content using OpenAI GPT-4.1-mini
    Returns a Pydantic model ExtractResponse
    """
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract product specification attributes from the provided product content and return a structured output.\n\n"
                            "# Steps\n\n"
                            "1. Identify Key Specifications: Focus on objective specs such as dimensions, weight, material, colour, finish, size, capacity, model number, voltage, IP rating, etc. Do not include features, benefits, applications, marketing copy, or purposes.\n\n"
                            "2. Analyze Context: Use context and industry terminology to extract precise specifications.\n\n"
                            "3. Extract and Categorize: Propose clear attribute names and map the corresponding value(s) found in the content.\n\n"
                            "4. Ensure Completeness: Prefer high-signal specs; avoid overly long or random attribute lists.\n\n"
                            "5. Format for Consistency: Output values as a list of strings. If unknown, use ['N/A'].\n\n"
                            "# Output Format\n\n"
                            "Return JSON as an array of {name, value} objects where value is List[str].\n\n"
                            "# Notes\n\n"
                            "- Do NOT create attributes named 'Title', 'Description', 'Brand', or other metadata fields.\n"
                            "- Extract only attributes applicable to this specific product; do not include options for other variants or the product family.\n"
                            "- Consider synonyms only when certainty is high.\n"
                            "- Handle ranges appropriately; when in doubt, return the range as it appears (e.g., '10-20 cm').\n"
                            "- If multiple values exist (e.g., colours), return each as a separate string in the list (no semicolons).\n"
                            "- Attribute names are 1-4 words, never sentences; keep labels concise and standard.\n"
                            "- Ensure values are in a tidied up casing"
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{title}\n\n{description}"
                    }
                ]
            }
        ],
        temperature=1.05,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "attributes",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "attributes": {
                            "type": "array",
                            "description": "A list of attributes consisting of name-value pairs.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "The name of the attribute."
                                    },
                                    "value": {
                                        "type": "array",
                                        "description": "The value(s) of the attribute as a list of strings.",
                                        "items": {"type": "string"},
                                        "minItems": 1
                                    }
                                },
                                "required": ["name", "value"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["attributes"],
                    "additionalProperties": False
                }
            }
        }
    )

    # Extract and parse JSON from response
    message_content = response.choices[0].message.content
    data = json.loads(message_content)

    # Return as Pydantic model
    return ExtractResponse(**data)

#Run the targeted approach (pass the schema names and the LLM try and match the values)
def run_targeted_prompt(title: str, description: str, schema_attributes: list) -> ExtractResponse:
    """
    Extract specific attributes from product content using OpenAI GPT-4.1-mini
    Returns a Pydantic model ExtractResponse
    """
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract specific product specification attributes from given product content, returning a structured output "
                            "with values matched to requested attributes. Identify and match attributes with certainty, using precise "
                            "attribute names. If an attribute is not found, return ['N/A'].\n\n"
                            "# Steps\n"
                            "1. Input Parsing: Accept a list of specific attribute names and the corresponding product content.\n"
                            "2. Attribute Matching: For each attribute name provided:\n"
                            "   - Search for the corresponding attribute value(s) in the product content.\n"
                            "   - Ensure a high degree of certainty in the match.\n"
                            "3. Fallback: If a match cannot be confidently made, assign ['N/A'] to the attribute.\n"
                            "4. Output Construction: Assemble a structured response with the matched attributes and values.\n\n"
                            "# Output Format\n"
                            "Provide the output in JSON format as an array of objects with 'name' and 'value', where 'value' is a list of strings.\n\n"
                            "# Notes\n"
                            "- Attributes may not make sense for the product; if so, keep as ['N/A'].\n"
                            "- Prioritize exact matches for attribute names to ensure accuracy.\n"
                            "- Consider common synonyms only if certainty is high.\n"
                            "- If multiple values exist (e.g., colors), return each as a separate string in the list.\n"
                            "- For product sets, do not list out all individual pieces.\n"
                            "- Attributes are typically 1-4 words, never sentences.\n"
                            "- Only return the attributes passed into the input list.\n"
                            "- Ensure values are in a tidied up casing"
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Title: {title}\nDescription: {description}\nAttributes: {schema_attributes}"
                    }
                ]
            }
        ],
        temperature=1.05,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "attributes",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "attributes": {
                            "type": "array",
                            "description": "A list of attributes consisting of name-value pairs.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "The name of the attribute."},
                                    "value": {
                                        "type": "array",
                                        "description": "The value(s) of the attribute as a list of strings.",
                                        "items": {"type": "string"},
                                        "minItems": 1
                                    }
                                },
                                "required": ["name", "value"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["attributes"],
                    "additionalProperties": False
                }
            }
        }
    )

    # Extract and parse JSON from response
    message_content = response.choices[0].message.content
    data = json.loads(message_content)

    # Return as Pydantic model
    return ExtractResponse(**data)

# Cleanup/merge approach
def run_hybrid_prompt(title: str, description: str, non_targeted_output: dict, targeted_output: dict) -> CleanedExtractResponse:
    """
    Merge non targeted and targeted extraction outputs, prioritizing targeted, removing N/A values, de-duplicating values, and indicating source method(s).
    """
    client = get_openai_client()

    # Normalize inputs to plain dicts for safe JSON serialization
    def to_plain_dict(obj):
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if isinstance(obj, dict):
            return obj
        return json.loads(json.dumps(obj, default=lambda o: getattr(o, "__dict__", str(o))))

    non_targeted_dict = to_plain_dict(non_targeted_output)
    targeted_dict = to_plain_dict(targeted_output)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Combine and cleanse two attribute extraction outputs in JSON format."
                            "Ensure values appear only once; consolidate duplicates that differ only in casing or minor wording. "
                            "If an attribute appears in both, retain a single attribute entry. Remove any values equal to 'N/A'. "
                            "Return name, value (List[str]), and method used ('non targeted', 'targeted', or 'non targeted; targeted').\n\n"
                            "# Steps\n"
                            "1. Input Capture: Receive two JSON inputs, one labeled 'non targeted' and another 'targeted'.\n"
                            "2. Attribute Prioritisation: Prefer attributes present in targeted over non targeted.\n"
                            "3. Duplicate Removal: Merge duplicate values across methods into a single list, normalizing trivial differences (e.g., casing, hyphens).\n"
                            "4. N/A Removal: Remove any values equal to 'N/A'. If no values remain, drop the attribute.\n"
                            "5. Output Compilation: Produce cleaned attributes with method provenance.\n\n"
                            "# Output Format\n"
                            # "A JSON object with 'attributes': Array<{name: string, value: List<string>, method: string}>."
                        )
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Title: {title}\nDescription: {description}\n\nNon targeted extraction JSON: {json.dumps(non_targeted_dict)}\n\nTargeted extraction JSON: {json.dumps(targeted_dict)}"
                    }
                ]
            }
        ],
        temperature=1.05,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "product_attributes",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "attributes": {
                            "type": "array",
                            "description": "Cleaned and prioritized attributes with method provenance.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Attribute name."},
                                    "value": {
                                        "type": "array",
                                        "description": "Attribute value(s) as list of strings.",
                                        "items": {"type": "string"},
                                        "minItems": 1
                                    },
                                    "method": {
                                        "type": "string",
                                        "description": "Source method(s) for this attribute.",
                                        "enum": ["non targeted", "targeted", "non targeted; targeted"]
                                    }
                                },
                                "required": ["name", "value", "method"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["attributes"],
                    "additionalProperties": False
                }
            }
        }
    )

    message_content = response.choices[0].message.content
    data = json.loads(message_content)
    return CleanedExtractResponse(**data)
