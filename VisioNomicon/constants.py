import os

API_KEY = ""

NAMING_PROMPT = "Generate a filename for the image by analyzing its content and utilizing a user-provided template. Placeholders enclosed in square brackets (e.g., [Subject], [Color], [Action]) will be used, which represent specific elements to be incorporated in the filename. Replace the placeholders accurately and succinctly with terms pulled from the image content, removing the brackets in the final filename. For instance, if the template reads '[MainSubject]_in_[Setting]', the filename might be 'Cat_in_Garden'. Construct the filename omitting the file extension and any other text. Assure that every placeholder is filled with precise, image-derived information, conforming to typical filename length restrictions. The given template is '{template}'."

DATA_DIR = ""
MODEL = "gpt-4o"


def get_data_dir() -> str:
    global DATA_DIR
    if not DATA_DIR:
        xdg_data_home: str | None = os.environ.get("XDG_DATA_HOME")
        DATA_DIR = (
            xdg_data_home if xdg_data_home else os.path.abspath("~/.local/share")
        ) + "/visionomicon/"
    return DATA_DIR
