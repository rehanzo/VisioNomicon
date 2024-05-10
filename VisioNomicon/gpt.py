from openai import OpenAI
from pathlib import Path
import os, requests, base64, sys

API_KEY = ""


def set_api_key():
    global API_KEY
    not "OPENAI_API_KEY" in os.environ and sys.exit(
        "Open AI API key not set. Set it using the OPENAI_API_KEY environment variable"
    )
    API_KEY = os.environ.get("OPENAI_API_KEY") if API_KEY == "" else API_KEY


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
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Generate a filename for an image by analyzing its content and utilizing a user-provided template. Placeholders enclosed in square brackets (e.g., [Subject], [Color], [Action]) will be used, which represent specific elements to be incorporated in the filename. Replace the placeholders accurately and succinctly with terms pulled from the image content, removing the brackets in the final filename. For instance, if the template reads '[MainSubject]_in_[Setting]', the filename might be 'Cat_in_Garden'. Construct the filename omitting the file extension and any other text. Assure that every placeholder is filled with precise, image-derived information, conforming to typical filename length restrictions. The given template is '{template}'.",
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
        except:
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
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": f"Act as a validator to ensure that a generated filename complies with the specified template structure '{template}'. Without access to the corresponding image, assess whether the filename reflects what could plausibly stem from the image contents based on the components stipulated in the template. For example, if the template is '[MainSubject]', filenames like 'Puppy' or 'Sunflower' could be valid, assuming the primary subject in the image aligns with these nouns. Evaluate if the filename is succinct, follows the intended format, and seems plausible as a descriptor for an unseen image. Reply with 'VALID' if the filename correctly adheres to the template and represents a feasible image content descriptor or 'INVALID' if it fails to meet these conditions. Provide only the validation outcome as your response.",
            },
            {"role": "user", "content": f"{name}"},
        ],
    )

    return completion.choices[0].message.content == "VALID"
