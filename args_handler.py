import argparse
import os

def parse_cli_args():
    # TODO: Better help and description messages
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('-f', type=str, nargs='*', help='The input file paths') # if not used, empty array
    parser.add_argument('-c', type=str, nargs='?', help='Mapping file to create', const='')
    parser.add_argument('-x', type=str, nargs='?', help='Execute on given mapping', const='')

    # if flag with value, equals value
    # if flag with no value, equals default value
    # if flag not used, equals None
    
    args = parser.parse_args()

    # TODO: Argument pairings, etc.
    # -f with -c (no val) should create mapping at default location
    # -f with -c (val) creates mapping at given location
        # -c without -f should error
        # -f without -c should error
    # -x can be with others or alone
        # allows for doing everything at once
    if (
        ((args.c is not None) and (args.f is None or len(args.f) == 0))
        or ((args.f is not None and len(args.f) != 0) and (args.c is None))
    ):
        parser.error('-f and -c must be used together')

    if args.f is not None and len(args.f) != 0:
        args.f = [os.path.abspath(path) for path in args.f]

    if args.c is not None and args.c != '':
        args.c = os.path.abspath(args.c)

    if args.x is not None and args.x != '':
        args.x = os.path.abspath(args.x)
    
    return args
