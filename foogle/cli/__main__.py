import argparse

from .cli import SearchEngineShell


def parse_args():
    parser = argparse.ArgumentParser(description='Search engine'
                                                 ' cli interface')
    return parser.parse_args().__dict__


parse_args()
shell = SearchEngineShell()
shell.cmdloop()
