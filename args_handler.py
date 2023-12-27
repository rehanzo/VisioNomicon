import argparse
import os

def parse_cli_args():
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('input_files', type=str, nargs='+', help='The input file paths')
    
    args = parser.parse_args()
    args.input_files = [os.path.abspath(path) for path in args.input_files]
    
    return args
