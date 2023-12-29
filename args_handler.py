import argparse
import os

def parse_cli_args():
    # TODO: Better help and description messages
    # TODO: fix argparse usage message
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('-f', type=str, nargs='*', help='The input file paths')
    parser.add_argument('-o', type=str, nargs='?', help='Mapping file to create', const='')
    parser.add_argument('-x', type=str, nargs='?', help='Execute on given mapping', const='')
    parser.add_argument('-ox', type=str, nargs='?', help='Map and execute on mapping', const='')
    parser.add_argument('-u', type=str, nargs='?', help='Undoes given mapping', const='')

    # if flag with value, equals value
    # if flag with no value, equals default value
    # if flag not used, equals None
    
    args = parser.parse_args()

    # HACK: errors if args.u isn't alone
    # turns args list into dict, then pops u, then checks for nones
    args_dict = vars(args).copy()
    args_dict.pop('u')  # Remove the '-u' arg to check others

    if args.u is not None and not all(x is None for x in args_dict.values()):
        parser.error("use -u by itself")

    if args.f is not None and len(args.f) == 0:
        parser.error("-f requires a value")

    if args.o is not None and args.x is not None:
        parser.error("instead of using -o along with -x, use -ox")
        
    if args.ox is not None:
        if args.o is not None or args.x is not None:
            parser.error("-ox should be used without -o or -x")

        args.o = args.ox
        args.x = args.ox

        
    if ((args.o is None) != (args.f is None)): #XOR
        parser.error('-f and -o must be used together')

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
