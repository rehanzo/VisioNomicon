import os
import sys
import base64
import requests

API_KEY = ""

def main():
  # Function to get openai api key
  global API_KEY
  API_KEY = os.environ.get("OPENAI_KEY")

  print(image_to_name("/home/Rehan/Pictures/Backgrounds/paintings/current.jpg", "[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement]_[Number].jpg"))


def image_to_name(image_path: str, structure: str) -> str:
  # Function to encode the image
  def encode_image(image_path: str):
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')


  # Getting the base64 string
  base64_image = encode_image(image_path)

  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
  }

  payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": f"Give this image a filename, following the form '{structure}'. Respond with the full filename, nothing else."
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

  # TODO: let user modify number of retries
  retries = 3
  for i in range(retries):
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()

    # TODO: flag to skip errors, mapping the filename to original name, changing nothing
    try:
      return response_json['choices'][0]['message']['content']
    except:
      print("OpenAI Unexpected Response:", response_json['error']['message'])
      i < retries - 1 and print("retrying...\n")

  sys.exit("\nOpenAI unexpected response {} times, quitting.".format(retries))

if __name__ == "__main__":
    main()
