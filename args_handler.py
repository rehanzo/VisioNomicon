import argparse
import os

def parse_cli_args():
    # TODO: Better help and description messages
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('input_files', type=str, nargs='+', help='The input file paths')
    parser.add_argument('-c', type=str, help='Mapping file to create')
    parser.add_argument('-x', type=str, help='Execute on given mapping')
    
    args = parser.parse_args()

    if args.input_files is not None:
        args.input_files = [os.path.abspath(path) for path in args.input_files]

    if args.c is not None:
        args.c = os.path.abspath(args.c)
    
    return args
