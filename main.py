import os
import json
import copy
from args_handler import parse_cli_args
from gpt import image_to_name, name_validation
from datetime import datetime

DATA_DIR = ""

def main():
  # get data dir
  global DATA_DIR
  DATA_DIR = (os.environ.get("XDG_DATA_HOME") if "XDG_DATA_HOME" in os.environ else os.path.abspath("~/.local/share")) + "/visionomicon/"

  # make data dir if doesn't exist
  not os.path.exists(DATA_DIR) and os.makedirs(DATA_DIR)

  args = parse_cli_args()

  og_filepaths = args.input_files
  new_filepaths: list[str] = generate_mapping(og_filepaths)

  # have new and old, put them together into a json and save
  save_mapping(args, new_filepaths)

def save_mapping(args, new_filepaths: list[str]):
  og_filepaths: list[str] = args.input_files
  data = dict(zip(og_filepaths, new_filepaths))
  # data ready to dump, need to get mapping filename
  mapping_filename = get_mapping_name(args)

  with open(mapping_filename, 'w') as file:
    json.dump(data, file, indent=4)

def get_mapping_name(args) -> str:
  return args.c if args.c is not None else DATA_DIR + datetime.now().strftime("mapping-%Y-%m-%d-%H-%M-%S.json")
  
def generate_mapping(og_filepaths: list[str]) -> list[str]:
  new_filepaths: list[str] = copy.deepcopy(og_filepaths)

  for i in range(len(new_filepaths)):
    slicepoint = new_filepaths[i].rindex("/") + 1
    new_filepaths[i] = new_filepaths[i][:slicepoint]

  # TODO: allow user to set structure
  structure = "[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement].jpg"

  for i in range(len(og_filepaths)):
    image_path = og_filepaths[i]
    for j in range(3):
      new_name = image_to_name(image_path, structure)
      if name_validation(new_name, structure):
        print("Generated name {} validated".format(new_name))
        break
      elif j == 2:
        sys.exit("Generated name {} failed validation three times, aborting...".format(new_name))

      print("Generated name failed validation, regenerating...")

    new_filepaths[i] = new_filepaths[i] + new_name

    # TODO: better message
    print("File {} mapped to name {}\n".format(og_filepaths[i], new_name))
  return new_filepaths

if __name__ == "__main__":
    main()
