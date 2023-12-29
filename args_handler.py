import argparse, os, sys

# makes sure arg is alone, hard to read
# used for -u
class EnsureIsolatedAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(EnsureIsolatedAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if any(other_arg_present for arg_dest in parser._option_string_actions
               for other_arg_present in sys.argv if arg_dest in other_arg_present and arg_dest != option_string):
            parser.error(f"{option_string} must be used alone; no other arguments allowed")
        setattr(namespace, self.dest, values)

def parse_cli_args():
    # TODO: Better help and description messages
    # TODO: fix argparse usage message
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('-f', type=str, nargs='*', help='The input file paths')
    parser.add_argument('-o', type=str, nargs='?', help='Mapping file to create')
    parser.add_argument('-x', type=str, nargs='?', help='Execute on given mapping', const='')
    parser.add_argument('-ox', type=str, nargs='?', help='Map and execute on mapping', const='')
    parser.add_argument('-u', action=EnsureIsolatedAction, type=str, nargs='?', help='Undoes given mapping', const='')
    parser.add_argument('-s', type=str, nargs='?', help='Structure to generate name from', default='[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement].jpg')

    # if flag with value, equals value
    # if flag with no value, equals const value
    # if flag not used, equals None
    
    args = parser.parse_args()

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

    for image_path in args.f:
        _, image_ext = os.path.splitext(image_path)
        if image_ext not in supported_ext:
            parser.error('Filetype {} not supported'. format(image_ext))

    #
    # get absolute paths where we need them
    #
    if args.f is not None:
        args.f = [os.path.abspath(path) for path in args.f]

    if args.o is not None and args.o != '':
        args.o = os.path.abspath(args.o)

    if args.x is not None and args.x != '':
        args.x = os.path.abspath(args.x)

    if args.u is not None and args.u != '':
        args.u = os.path.abspath(args.u)
    
    return args
