#!/usr/bin/env python3
"""Validation module for input files and JSON schemas."""
# 入力ファイルとJSONスキーマのバリデーションモジュール。

from pydantic import BaseModel, ValidationError
import argparse
import sys
import json


class ValidateFunction(BaseModel):
    """Pydantic model for validating function definitions."""
    # 関数定義を検証するためのPydanticモデル。
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: dict[str, str]


class ValidatePrompt(BaseModel):
    """Pydantic model for validating user prompts."""
    # ユーザープロンプトを検証するためのPydanticモデル。
    prompt: str


def validation(args: argparse.Namespace) -> None:
    """Read files and validate JSON data against schemas."""
    # ファイルを読み込み、JSONデータがスキーマに合致するか検証する。
    try:
        f_text = args.functions_definition.read_text(encoding="utf-8")
        i_text = args.input.read_text(encoding="utf-8")

        # 出力ファイルの事前作成（権限チェックを兼ねる）
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("")

        # JSONとしての文法チェック（[ ] や { } の壊れがないか）
        functions = json.loads(f_text)
        prompts = json.loads(i_text)

        # JSONを構造ごとにバリデーション
        for fn in functions:
            ValidateFunction(**fn)
        for pm in prompts:
            ValidatePrompt(**pm)

    # JSON構文エラー
    except json.JSONDecodeError as e:
        print(f"Error: JSON file format is incorrect.: {e}")
        sys.exit(1)
    # JSONのキーとバリューのエラー
    except ValidationError as e:
        print(f"Error: Data does not comply with the formatting rules.: {e}")
        sys.exit(1)

    # 以下 File Path Error
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: Permission denied for writing to '{e.filename}'.")
        sys.exit(1)
    except IsADirectoryError as e:
        print(f"Error: '{e.filename}' is a directory.")
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
