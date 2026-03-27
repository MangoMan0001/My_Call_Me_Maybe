import argparse
from pathlib import Path


def get_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(prog='Call_Me_Maybe',
                                     description='LLMの制約デコーディングプログラム')
    parser.add_argument('-f', '--functions_definition',
                        type=Path,
                        action='store',
                        default='data/input/functions_definition.json')
    parser.add_argument('-i', '--input',
                        type=Path,
                        action='store',
                        default='data/input/function_calling_tests.json')
    parser.add_argument('-o', '--output',
                        type=Path,
                        action='store',
                        default='data/output/function_calls.json')

    return parser.parse_args()
