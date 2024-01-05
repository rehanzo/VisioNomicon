import os, json, copy, glob
from .args_handler import *
from .gpt import *
from datetime import datetime

DATA_DIR = ""

def main():
  # get data dir
  global DATA_DIR
  DATA_DIR = (os.environ.get("XDG_DATA_HOME") if "XDG_DATA_HOME" in os.environ else os.path.abspath("~/.local/share")) + "/visionomicon/"

  # make data dir if doesn't exist
  not os.path.exists(DATA_DIR) and os.makedirs(DATA_DIR)

  args = parse_cli_args()

  # if creating mapping
  if args.files is not None:
    new_filepaths: list[str] = generate_mapping(args)

    # have new and old, put them together into a json and save
    save_mapping(args, new_filepaths)

  # if executing or undoing
  if args.undo or args.execute:
    rel_mapping_fp = args.execute if args.execute else args.undo
    rename_from_mapping(rel_mapping_fp, args.undo is not None)

def rename_from_mapping(rel_mapping_fp: str, undo: bool = False):
  mapping_fp = get_mapping_name(rel_mapping_fp)
  og_filepaths: list[str] = []
  new_filepaths: list[str] = []

  with open(mapping_fp) as f:
    data = json.load(f)
    og_filepaths += list(data.keys())
    new_filepaths += list(data.values())

  from_fps, to_fps = (new_filepaths, og_filepaths) if undo else (og_filepaths, new_filepaths)
  
  for i in range(len(from_fps)):
    _, filename = os.path.split(to_fps[i])
    print("Renaming {} to {}".format(from_fps[i], '.../' + filename))
    os.rename(from_fps[i], to_fps[i])

def get_mapping_name(cli_fp: str):
  if cli_fp != NO_VAL:
    return cli_fp
  else:
    # Join the directory with the file pattern
    file_pattern = os.path.join(DATA_DIR, '*.json')

    # Get list of files matching the file pattern
    files = glob.glob(file_pattern)

    # Sort files by creation time and get the last one
    mapping = max(files, key=os.path.getctime)
    return mapping

def save_mapping(args, new_filepaths: list[str]):
  og_filepaths: list[str] = args.files
  data = dict(zip(og_filepaths, new_filepaths))
  # data ready to dump, need to get mapping filename
  mapping_filename = generate_mapping_name(args)

  with open(mapping_filename, 'w') as file:
    json.dump(data, file, indent=4)

def generate_mapping_name(args) -> str:
  return args.output if args.output != NO_VAL else DATA_DIR + datetime.now().strftime("mapping-%Y-%m-%d-%H-%M-%S.json")
  
def generate_mapping(args) -> list[str]:
  og_filepaths: list[str] = args.files
  new_filepaths: list[str] = copy.deepcopy(og_filepaths)

  for i in range(len(new_filepaths)):
    slicepoint = new_filepaths[i].rindex("/") + 1
    new_filepaths[i] = new_filepaths[i][:slicepoint]

  for i in range(len(og_filepaths)):
    image_path = og_filepaths[i]
    for j in range(args.validation_retries + 1):
      print("Generating name...")
      new_name = image_to_name(image_path, args)
      print("Generated name {}".format(new_name))

      _, image_ext = os.path.splitext(image_path)
      new_filename = new_name + image_ext
      new_fp = new_filepaths[i] + new_filename

      # if new_fp == image_path, that means image_to_name errored past retry limit
      # mapping the file to the exact same name, keeping it the same
      # this means it would not follow the template and fail validation, so we skip
      if new_fp == image_path:
        break
      elif name_validation(new_name, args.template):
        print("Name validated".format(new_name))
        break
      elif j == args.validation_retries:
        if args.ignore_validation_fail:
          print("Failed validation {} time(s), leaving filename unchanged".format(args.validation_retries + 1))
          new_fp = image_path
        else:
          sys.exit("Failed validation {} time(s), aborting...".format(args.validation_retries + 1))
      else:
        print("Generated name failed validation, regenerating...")

    new_filename_suffixed = new_filename
    num_suffix = 1
    while new_fp in new_filepaths:
      new_filename_suffixed = new_name + f"_{num_suffix}" + image_ext
      new_fp = new_filepaths[i] + new_filename_suffixed
      num_suffix += 1

    new_filepaths[i] = new_fp

    print("File {} mapped to name {}\n".format(og_filepaths[i], new_filename_suffixed))
  return new_filepaths

if __name__ == "__main__":
    main()
