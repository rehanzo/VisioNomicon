import os, json, copy, glob
from args_handler import *
from gpt import *
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
  if args.undo is not None or args.execute is not None:
    arg = args.execute if args.execute is not None else args.undo
    mapping_fp = get_mapping_name(arg)

    og_filepaths: list[str] = []
    new_filepaths: list[str] = []

    with open(mapping_fp) as f:
      data = json.load(f)
      og_filepaths += list(data.keys())
      new_filepaths += list(data.values())

    from_fps = og_filepaths if args.execute is not None else new_filepaths
    to_fps = new_filepaths if args.execute is not None else og_filepaths
      
    for i in range(len(from_fps)):
      _, filename = os.path.split(to_fps[i])
      print("Renaming {} to {}".format(from_fps[i], '.../' + filename))
      os.rename(from_fps[i], to_fps[i])
    

def get_mapping_name(cli_fp: str):
  if cli_fp != NO_VAL:
    return cli_fp
  else:
    # Join the directory with the file pattern
    file_pattern = os.path.join(DATA_DIR, 'mapping-*.json')

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
  return args.output if args.output else DATA_DIR + datetime.now().strftime("mapping-%Y-%m-%d-%H-%M-%S.json")
  
def generate_mapping(args) -> list[str]:
  og_filepaths: list[str] = args.files
  new_filepaths: list[str] = copy.deepcopy(og_filepaths)

  for i in range(len(new_filepaths)):
    slicepoint = new_filepaths[i].rindex("/") + 1
    new_filepaths[i] = new_filepaths[i][:slicepoint]

  for i in range(len(og_filepaths)):
    image_path = og_filepaths[i]
    for j in range(args.retries):
      print("Generating name...")
      new_name = image_to_name(image_path, args)
      print("Generated name {}".format(new_name))
      if args.skip_validation:
        break
      elif name_validation(new_name, args.structure):
        print("Name validated".format(new_name))
        break
      elif j == args.retries - 1:
        sys.exit("Failed validation {} times, aborting...".format(args.retries))

      print("Generated name failed validation, regenerating...")

    _, image_ext = os.path.splitext(image_path)
    new_name = new_name + image_ext
    new_fp = new_filepaths[i] + new_name
    new_name_suffixed = new_name
    num_suffix = 1
    while new_fp in new_filepaths:
      new_name_suffixed = new_name + f"_{num_suffix}"
      new_fp = new_filepaths[i] + new_name_suffixed
      num_suffix += 1

    new_filepaths[i] = new_fp

    print("File {} mapped to name {}\n".format(og_filepaths[i], new_name_suffixed))
  return new_filepaths

if __name__ == "__main__":
    main()
