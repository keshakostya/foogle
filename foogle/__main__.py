import argparse

from searcher.web.server import create_server
from searcher.cli.cli import SearchEngineShell


def parse_args():
    parser = argparse.ArgumentParser(description='Search engine')
    subparsers = parser.add_subparsers(help='mode')
    cli = subparsers.add_parser('cli', help='Console interface')
    cli.set_defaults(mode='cli')
    web = subparsers.add_parser('web', help='Web interface')
    web.set_defaults(mode='web')
    web.add_argument('--host', help='Web server host', default='127.0.0.1')
    web.add_argument('--port', help='Web server port', default='5000')
    web.add_argument('--debug', help='Web server debug option',
                     action='store_true')
    return parser.parse_args().__dict__


if __name__ == '__main__':
    args = parse_args()
    if 'mode' not in args:
        print('usage: __main__.py [-h] {cli,web}')
        exit(1)
    mode = args.pop('mode')
    if mode == 'web':
        server = create_server()
        server.run(**args)
    else:
        shell = SearchEngineShell()
        shell.cmdloop()
