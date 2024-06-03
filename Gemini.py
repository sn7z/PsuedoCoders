# Install the Google AI Python SDK
#!pip install google-generativeai

# See the getting started guide for more information:
# https://ai.google.dev/gemini-api/docs/get-started/python

# Import the Google AI Python SDK
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCLZMT3xhqG9r3MVQxcRf2nKrm2j8XBJAk")

# Create the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Generate content
prompt = "Write a story about a magic backpack."
response = model.generate_content(prompt)

# Print the response
print(response.text)