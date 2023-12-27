import os
import sys
import base64
import requests
from args_handler import parse_cli_args
import json
from datetime import datetime
import copy

API_KEY = ""
DATA_DIR = ""

def main():
  # get api key
  global API_KEY
  API_KEY = os.environ.get("OPENAI_KEY")

  # get data dir
  global DATA_DIR
  DATA_DIR = (os.environ.get("XDG_DATA_HOME") if "XDG_DATA_HOME" in os.environ else os.path.abspath("~/.local/share")) + "/visionomicon/"

  # make data dir if doesn't exist
  not os.path.exists(DATA_DIR) and os.makedirs(DATA_DIR)

  args = parse_cli_args()

  og_filepaths = args.input_files
  new_filepaths: list[str] = generate_mapping(og_filepaths)

  # have new and old, put them together into a json and save
  save_mapping(og_filepaths, new_filepaths)

def save_mapping(og_filepaths: list[str], new_filepaths: list[str]):
  data = dict(zip(og_filepaths, new_filepaths))
  # data ready to dump, need to get mapping filename
  mapping_filename = get_mapping_name()

  with open(DATA_DIR + mapping_filename, 'w') as file:
    json.dump(data, file, indent=4)

def get_mapping_name() -> str:
  return datetime.now().strftime("mapping-%Y-%m-%d-%H-%M-%S.json")
  
def generate_mapping(og_filepaths: list[str]) -> list[str]:
  new_filepaths: list[str] = copy.deepcopy(og_filepaths)

  for i in range(len(new_filepaths)):
    slicepoint = new_filepaths[i].rindex("/") + 1
    new_filepaths[i] = new_filepaths[i][:slicepoint]

  # TODO: allow user to set structure
  structure = "[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement].jpg"

  for i in range(len(og_filepaths)):
    image_path = og_filepaths[i]
    new_name = image_to_name(image_path, structure)
    new_filepaths[i] = new_filepaths[i] + new_name

    # TODO: better message
    print("File {} mapped to name {}".format(og_filepaths[i], new_name))
  return new_filepaths

# TODO: validation of generated name - if not valid, regenerate
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
            "text": f"Give this image a filename, precisely following the form '{structure}'. Respond with the full filename, nothing else."
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
