import argparse

from .cli import SearchEngineShell


def parse_args():
    parser = argparse.ArgumentParser(description='Search engine'
                                                 ' cli interface')
    return parser.parse_args().__dict__


if __name__ == '__main__':
    parse_args()
    shell = SearchEngineShell()
    shell.cmdloop()
