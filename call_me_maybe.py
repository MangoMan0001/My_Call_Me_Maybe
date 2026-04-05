#!user/bin/env python3
"""Main execution script for the project."""
# プロジェクトのメイン実行スクリプト。

from utils import get_args
from parser import validation
from model import LimitationModel


def main() -> None:
    """Validate arguments and run the JSON generation model."""
    # 引数を検証し、JSON生成モデルを実行する。
    args = get_args()
    validation(args)
    limitaion = LimitationModel(args)
    limitaion.run()


if __name__ == '__main__':
    main()
