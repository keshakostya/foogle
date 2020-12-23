import argparse

from .server import run_server


def parse_args():
    parser = argparse.ArgumentParser(description='Search engine'
                                                 ' web interface')
    parser.add_argument('--host', help='Web server host', default='127.0.0.1')
    parser.add_argument('--port', help='Web server port', default='5000')
    parser.add_argument('--debug', help='Web server debug option',
                        action='store_true')
    return parser.parse_args().__dict__


args = parse_args()
run_server(**args)
