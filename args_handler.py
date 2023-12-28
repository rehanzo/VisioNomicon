import argparse
import os

def parse_cli_args():
    # TODO: Better help and description messages
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('-f', type=str, nargs='*', help='The input file paths')
    parser.add_argument('-c', type=str, help='Mapping file to create')
    parser.add_argument('-x', type=str, nargs='?', help='Execute on given mapping', const='')
    # if flag with value, equals value
    # if flag with no value, equals default value
    # if flag not used, equals None
    
    args = parser.parse_args()

    # TODO: Argument pairings, etc.
    # input files by itself should create mapping at default location
    # input files with -c creates mapping at given location
        # -c with nothing should error
        # -c without input files should error
    # -x should be by itself.....unless?
        # maybe allow usage with -f and -c for a one and done sort of thing?
    if args.f is not None:
        args.f = [os.path.abspath(path) for path in args.f]

    if args.c is not None and args.c != '':
        args.c = os.path.abspath(args.c)

    if args.x is not None and args.x != '':
        args.x = os.path.abspath(args.x)
    
    return args
