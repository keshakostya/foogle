import cmd

from foogle.engine.controller import Controller


class SearchEngineShell(cmd.Cmd):
    intro = 'Welcome to the search engine shell. ' \
            'Type help or ? to list commands.\n'
    prompt = '> '

    def __init__(self):
        super().__init__()
        self.controller = Controller()

    def do_search(self, arg):
        print(self.controller.execute('search', arg))

    def do_load_index(self, arg):
        print(self.controller.execute('load_index'))

    def do_save_index(self, arg):
        print(self.controller.execute('save_index'))

    def do_build_index(self, arg):
        print(self.controller.execute('build_index', *arg.split(' ')))
