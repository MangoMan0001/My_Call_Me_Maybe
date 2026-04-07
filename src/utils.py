#!/usr/bin/env python3
"""Utility module for command-line argument parsing."""
# コマンドライン引数を解析するユーティリティモジュール。

import argparse
from pathlib import Path


def get_args() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    # コマンドライン引数を解析して返す。

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
