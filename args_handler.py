import argparse, os, sys

NO_VAL = object()

def parse_cli_args():
    # TODO: Better help and description messages
    # TODO: fix argparse usage message
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('-f', type=str, nargs='*', help='The input file paths')
    parser.add_argument('-o', type=str, nargs='?', help='Mapping file to create')
    parser.add_argument('-x', type=str, nargs='?', help='Execute on given mapping', const=NO_VAL)
    parser.add_argument('-ox', type=str, nargs='?', help='Map and execute on mapping', const=NO_VAL)
    parser.add_argument('-u', type=str, nargs='?', help='Undoes given mapping', const=NO_VAL)
    parser.add_argument('-s', type=str, nargs='?', help='Structure to generate name from', default='[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement].jpg')

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
    if args.u is not None:
        # Check if any other arg changed from default
        non_default_args = [arg for arg in args_dict if args_dict[arg] != defaults[arg]]
    
        # Remove checked key since we don't need to check it against itself
        non_default_args.remove('u')
    
        # If any other arguments changed, error
        if non_default_args:
            parser.error('-u must not be used with any other arguments.')
    ####################################################################################

    parser.error("STOP")
    if args.f is not None and len(args.f) == 0:
        parser.error("-f requires a value")

    if args.o is not None and args.x is not None:
        parser.error("instead of using -o along with -x, use -ox")
        
    if args.ox is not None:
        if args.o is not None or args.x is not None:
            parser.error("-ox should be used without -o or -x")

        args.o = args.ox
        args.x = args.ox

        
    if args.o is not None and args.f is None:
        parser.error('-o must be used with -f')

    if args.s is None:
        parser.error('used -s with no value')

    supported_ext = ['.png', '.jpeg', '.jpg', '.webp', '.gif']


    #
    # get absolute paths where we need them
    #
    # TODO: Ignore directories
    if args.f is not None:
        args.f = [os.path.abspath(path) for path in args.f]

        for image_path in args.f:
            _, image_ext = os.path.splitext(image_path)
            if image_ext not in supported_ext:
                parser.error('Filetype {} not supported'.format(image_ext))

    if args.o is not None and args.o != NO_VAL:
        args.o = os.path.abspath(args.o)

    if args.x is not None and args.x != NO_VAL:
        args.x = os.path.abspath(args.x)

    if args.u is not None and args.u != NO_VAL:
        args.u = os.path.abspath(args.u)
    
    return args
