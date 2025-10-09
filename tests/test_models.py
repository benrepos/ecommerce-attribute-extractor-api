from backend.models import run_extraction_basic, run_targeted_prompt, run_hybrid_prompt
from backend.schemas import ExtractResponse, ExtractRequestTargeted, ExtractRequest, ExtractRequestHybrid, CleanedExtractResponse

def test_extraction_basic():
    attributes = run_extraction_basic("Red T-shirt Cotton 2XL", "One workwear t-shirt made from cotton, in size 2XL.")
    assert attributes is not None
    assert len(attributes.attributes) > 0
    assert attributes.attributes[0].name is not None
    assert attributes.attributes[0].value is not None
    assert len(attributes.attributes[0].value) > 0
    assert attributes.attributes[0].value[0] is not None

def test_targeted_extraction():
    attributes = run_targeted_prompt("Red T-shirt Cotton 2XL", "One workwear t-shirt made from cotton, in size 2XL.", ["Colour",'Material', "Size"])
    assert attributes is not None
    assert len(attributes.attributes) > 0
    assert attributes.attributes[0].name is not None
    assert attributes.attributes[0].value is not None
    assert len(attributes.attributes[0].value) > 0
    assert attributes.attributes[0].value[0] is not None

def test_hybrid_extraction():
    targeted_output = run_targeted_prompt("Red T-shirt Cotton 2XL", "One workwear t-shirt made from cotton, in size 2XL.", ["Colour", "Size"])
    non_targeted_output = run_extraction_basic("Red T-shirt Cotton 2XL", "One workwear t-shirt made from cotton, in size 2XL.")
    attributes = run_hybrid_prompt("Red T-shirt Cotton 2XL", "One workwear t-shirt made from cotton, in size 2XL.", ["Colour", "Size"], non_targeted_output, targeted_output)
    assert attributes is not None
    assert len(attributes.attributes) > 0
    assert attributes.attributes[0].name is not None
    assert attributes.attributes[0].value is not None
    assert len(attributes.attributes[0].value) > 0
    assert attributes.attributes[0].value[0] is not None

