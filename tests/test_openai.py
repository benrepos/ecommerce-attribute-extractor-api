# test_openai.py
from openai import OpenAI
from backend.config import OPENAI_API_KEY  # Make sure backend/config.py exists

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Make a test request
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": "Hello, how are you?"}]
)

# Print the assistant response
print(response.choices[0].message.content)
