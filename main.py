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
  if args.o is not None:
    new_filepaths: list[str] = generate_mapping(args)

    # have new and old, put them together into a json and save
    save_mapping(args, new_filepaths)

  # if executing or undoing
  if args.u is not None or args.x is not None:
    arg = args.x if args.x is not None else args.u
    mapping_fp = get_mapping_name(arg)

    og_filepaths: list[str] = []
    new_filepaths: list[str] = []

    with open(mapping_fp) as f:
      data = json.load(f)
      og_filepaths += list(data.keys())
      new_filepaths += list(data.values())

    from_fps = og_filepaths if args.x is not None else new_filepaths
    to_fps = new_filepaths if args.x is not None else og_filepaths
      
    for i in range(len(from_fps)):
      # TODO/NOTE: probably better to have first be full path, next be name of file
      # since being in the same directory is implied. Makes it easier to read
      # can use `head, tail = os.path.split()`, tail being the end name
      print("renaming {} to {}".format(from_fps[i], to_fps[i]))
      os.rename(from_fps[i], to_fps[i])
    

def get_mapping_name(cli_fp: str):
  if cli_fp != '':
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
  og_filepaths: list[str] = args.f
  data = dict(zip(og_filepaths, new_filepaths))
  # data ready to dump, need to get mapping filename
  mapping_filename = generate_mapping_name(args)

  with open(mapping_filename, 'w') as file:
    json.dump(data, file, indent=4)

def generate_mapping_name(args) -> str:
  return args.o if args.o != '' else DATA_DIR + datetime.now().strftime("mapping-%Y-%m-%d-%H-%M-%S.json")
  
def generate_mapping(args) -> list[str]:
  og_filepaths: list[str] = args.f
  new_filepaths: list[str] = copy.deepcopy(og_filepaths)

  for i in range(len(new_filepaths)):
    slicepoint = new_filepaths[i].rindex("/") + 1
    new_filepaths[i] = new_filepaths[i][:slicepoint]

  for i in range(len(og_filepaths)):
    image_path = og_filepaths[i]
    # TODO: retries
    for j in range(3):
      print("Generating name...")
      new_name = image_to_name(image_path, args.s)
      # TODO: Make validation optional
      if name_validation(new_name, args.s):
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
