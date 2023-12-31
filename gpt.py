from openai import OpenAI
from pathlib import Path
import os, requests, base64, sys

API_KEY = ""

def set_api_key():
  global API_KEY
  not "OPENAI_API_KEY" in os.environ and sys.exit("Open AI API key not set. Set it using the OPENAI_API_KEY environment variable") 
  API_KEY = os.environ.get("OPENAI_API_KEY") if API_KEY == "" else API_KEY
    
def image_to_name(image_path: str, args) -> str:
  structure: str = args.structure

  set_api_key()
  # Function to encode the image
  def encode_image(image_path: str):
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')


  # Getting the base64 string
  base64_image = encode_image(image_path)
  _, image_ext = os.path.splitext(image_path)
  image_ext = image_ext[1:] # remove leading period

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
            "text": f"Give this image a filename, precisely following the form '{structure}'. Respond with the filename without the filetype extension, nothing else."
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/{image_ext};base64,{base64_image}",
              "detail": "low"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
  }

  for i in range(args.error_retries + 1):
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_json = response.json()

    try:
      return response_json['choices'][0]['message']['content']
    except:
      print("OpenAI Unexpected Response:", response_json['error']['message'])
      i < args.error_retries and print("retrying...\n")

  if args.ignore_error_fail:
    return Path(image_path).stem
  sys.exit("\nOpenAI unexpected response {} time(s), quitting.".format(args.error_retries + 1))

def name_validation(name: str, structure: str):
  set_api_key()
  client = OpenAI()

  completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
      {"role": "system", "content": f"You are a data validator. You will be given a filename, and you need to ensure it precisely follows the structure '{structure}'. It should follow this structure exactly, but the content you can be more lenient with. If it does not, respond with 'NO'. If it does, respond with 'YES'"},
      {"role": "user", "content": f"{name}"}
    ]
  )

  return completion.choices[0].message.content == "YES"
