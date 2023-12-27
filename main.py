from dotenv import load_dotenv
import os
import base64
import requests

load_dotenv()  # take environment variables from .env.
# OpenAI API Key
api_key = os.environ.get("OPENAI_KEY")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "/home/Rehan/Pictures/Backgrounds/paintings/current.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Give this image a filename, following the form '[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement]_[Number].jpg'. Respond with the full filename, nothing else."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 300
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())
