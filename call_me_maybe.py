#!user/bin/env python3

from utils import get_args
from parser import validation
from model import LimitationModel


def main() -> None:
    args = get_args()
    validation(args)
    limitaion = LimitationModel(args)
    limitaion.run()


if __name__ == '__main__':
    main()
