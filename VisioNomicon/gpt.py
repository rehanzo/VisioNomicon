import openai
import json
import io
from pathlib import Path
import os
import requests
import base64
import sys
from constants import API_KEY, NAMING_PROMPT, MODEL

RETRIEVED_JSON = {}


def set_api_key():
    global API_KEY
    "OPENAI_API_KEY" not in os.environ and sys.exit(
        "Open AI API key not set. Set it using the OPENAI_API_KEY environment variable"
    )
    API_KEY = os.environ.get("OPENAI_API_KEY") if API_KEY == "" else API_KEY


def batch(filepaths: list[str], base64_strs: list[str], template: str, data_dir: str):
    batch_reqs = []
    for filepath, base64_str in zip(filepaths, base64_strs):
        batch_reqs.append(
            {
                "custom_id": filepath,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": NAMING_PROMPT.format(template=template),
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": base64_str,
                                        "detail": "auto",
                                    },
                                },
                            ],
                        }
                    ],
                    "temperature": 0.7,
                },
            }
        )

    set_api_key()
    bytes_buffer = io.BytesIO()
    # write to bytes buffer
    # doing this to avoid having to write file to disk then pull back from disk to send
    for entry in batch_reqs:
        json_line = json.dumps(entry) + "\n"
        bytes_buffer.write(json_line.encode("utf-8"))

    # reset buffer position to prepare to send
    bytes_buffer.seek(0)

    file_upload_response = openai.files.create(file=bytes_buffer, purpose="batch")

    # create batch request from uploaded requests file
    # only 24h completion window is available for now
    batch = openai.batches.create(
        input_file_id=file_upload_response.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    # write batch id to file to retrieve later
    with open(f"{data_dir}/batch_id", "w") as file:
        file.write(batch.id)


def image_to_name_retrieve(image_path: str) -> str:
    global RETRIEVED_JSON

    if not RETRIEVED_JSON:
        # get file_id for completed responses
        file_id = ""
        # get batch id from file
        data_dir = os.environ.get("XDG_DATA_HOME")
        data_dir = (
            data_dir if data_dir else os.path.abspath("~/.local/share")
        ) + "/visionomicon/"
        with open(f"{data_dir}/batch_id", "r") as f:
            file_id = openai.batches.retrieve(f.read()).output_file_id

        # could occur if batch not complete yet
        if file_id is None:
            print("Error during batch retrieval, maybe the job isn't complete yet.")
            sys.exit()

        try:
            # get responses in a json str
            response_str = openai.files.content(file_id).content.decode("utf-8")
        # output file for responses may be expired or deleted
        except openai.NotFoundError:
            print("Error during batch retrieval, output file could not be retrieved.")
            sys.exit()
        # each response in own json
        response_jsons = [json.loads(s) for s in response_str.split("\n") if s.strip()]
        RETRIEVED_JSON = {s["custom_id"]: s for s in response_jsons}
    return RETRIEVED_JSON[image_path]["response"]["body"]["choices"][0]["message"][
        "content"
    ].strip()


def image_to_name(image_path: str, args) -> str:
    template: str = args.template

    set_api_key()

    # Function to encode the image
    def encode_image(image_path: str):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    # Getting the base64 string
    base64_image = encode_image(image_path)
    _, image_ext = os.path.splitext(image_path)
    image_ext = image_ext[1:]  # remove leading period

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": NAMING_PROMPT.format(template=template),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_ext};base64,{base64_image}",
                            "detail": "low",
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    for i in range(args.error_retries + 1):
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response_json = response.json()

        try:
            return response_json["choices"][0]["message"]["content"]
        except KeyError:
            print("OpenAI Unexpected Response:", response_json["error"]["message"])
            i < args.error_retries and print("retrying...\n")

    if args.ignore_error_fail:
        return Path(image_path).stem
    sys.exit(
        "\nOpenAI unexpected response {} time(s), quitting.".format(
            args.error_retries + 1
        )
    )


def name_validation(name: str, template: str):
    set_api_key()

    completion = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"Act as a validator to ensure that a generated filename complies with the specified template structure '{template}'. Without access to the corresponding image, assess whether the filename reflects what could plausibly stem from the image contents based on the components stipulated in the template. For example, if the template is '[MainSubject]', filenames like 'Puppy' or 'Sunflower' could be valid, assuming the primary subject in the image aligns with these nouns. Evaluate if the filename is succinct, follows the intended format, and seems plausible as a descriptor for an unseen image. Reply with 'VALID' if the filename correctly adheres to the template and represents a feasible image content descriptor or 'INVALID' if it fails to meet these conditions. Provide only the validation outcome as your response.",
            },
            {"role": "user", "content": f"{name}"},
        ],
    )

    return completion.choices[0].message.content == "VALID"
