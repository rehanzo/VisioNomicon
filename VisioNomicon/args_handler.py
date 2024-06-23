import argparse
import os

NO_VAL = object()


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="A utility leveraging GPT-4V for image file renaming based on content."
    )
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs="*",
        help="Specify file paths of the images to create mapping for",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        nargs="?",
        help="Provide file path for the JSON mapping file",
    )
    parser.add_argument(
        "-x",
        "--execute",
        type=str,
        nargs="?",
        help="Execute on given mapping",
        const=NO_VAL,
    )
    parser.add_argument(
        "-ox",
        "--mapex",
        type=str,
        nargs="?",
        help="Map and execute on mapping at given location",
        const=NO_VAL,
    )
    parser.add_argument(
        "-u", "--undo", type=str, nargs="?", help="Undo given mapping", const=NO_VAL
    )
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        nargs="?",
        help="Define the template for renaming image files, without file extension",
        default="[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement]",
    )
    parser.add_argument(
        "-e",
        "--validation-retries",
        type=int,
        help="Number of times to retry if validation not passed",
        default=3,
    )
    parser.add_argument(
        "-v",
        "--error-retries",
        type=int,
        help="Number of times to retry if error response recieved from OpenAI",
        default=3,
    )
    parser.add_argument(
        "-E",
        "--ignore-validation-fail",
        action="store_true",
        help="If validation retries limit is reached, map file to original name instead of returning an error",
    )
    parser.add_argument(
        "-V",
        "--ignore-error-fail",
        action="store_true",
        help="If error retries limit is reached, map file to original name instead of returning an error",
    )
    parser.add_argument(
        "-b",
        "--create-batch",
        action="store_true",
        help="Create batch job through OpenAI API",
    )
    parser.add_argument(
        "-B",
        "--retrieve-batch",
        action="store_true",
        help="Retrieve batch job output through OpenAI API. Run this 24 hours after creating the batch job.",
    )

    # if flag with value, equals value
    # if flag with no value, equals const value
    # if flag not used, equals None

    # capture initial defaults before parsing
    # this is for the below 'hack'
    defaults = {action.dest: action.default for action in parser._actions}

    args = parser.parse_args()
    args_dict = vars(args)

    ####################################################################################
    ### NOTE: this section is here to make sure if -u is used, its by itself
    ###       It is a bit hacky and hard to understand, but it seems there is
    ###       no way to do this thats not hacky or unclear
    if args.undo is not None:
        # Check if any other arg changed from default
        non_default_args = [arg for arg in args_dict if args_dict[arg] != defaults[arg]]

        # Remove checked key since we don't need to check it against itself
        non_default_args.remove("undo")

        # If any other arguments changed, error
        if non_default_args:
            parser.error("-u/--undo must not be used with any other arguments.")
    ####################################################################################

    if args.files == NO_VAL:
        parser.error("-f/--files requires a value")

    if args.output and args.execute:
        parser.error(
            "instead of using -o/--output along with -x/--execute, use -ox/--mapex"
        )

    if args.mapex:
        if args.output or args.execute:
            parser.error(
                "-ox/--mapex should be used without -o/--output or -x/--execute"
            )

        args.output = args.mapex
        args.execute = args.mapex

    if args.output and not args.files:
        parser.error("-o/--output must be used with -f/--files")

    if args.create_batch and not args.files:
        parser.error("-b/--create-batch must be used with -f/--files")

    if args.template == NO_VAL:
        parser.error("used -t/--template with no value")

    supported_ext = [".png", ".jpeg", ".jpg", ".webp", ".gif"]

    #
    # get absolute paths where we need them
    #
    if args.files:
        args.files = [os.path.abspath(path) for path in args.files]
        clean_paths = args.files.copy()

        for image_path in args.files:
            if os.path.isdir(image_path):
                print("{} is directory, skipping...".format(image_path))
                clean_paths.remove(image_path)
            elif not os.path.exists(image_path):
                parser.error("{} doesn't exist".format(image_path))

        for image_path in clean_paths:
            _, image_ext = os.path.splitext(image_path)
            if image_ext not in supported_ext:
                parser.error("Filetype {} not supported".format(image_ext))
        args.files = clean_paths

    if args.output and args.output != NO_VAL:
        args.output = os.path.abspath(args.output)

    if args.execute and args.execute != NO_VAL:
        args.execute = os.path.abspath(args.execute)

    if args.undo and args.undo != NO_VAL:
        args.undo = os.path.abspath(args.undo)

    return args
