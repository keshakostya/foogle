class SearcherError(Exception):
    message: str


class QueryError(SearcherError):

    message = 'error: query string is wrong'


class IndexEmptyError(SearcherError):
    message = 'error: you dont have index right now, built it before search'


class IndexBrokenError(SearcherError):
    message = 'error: your saved index is broken and cant be loaded,' \
              ' it was deleted'


class IndexNotExistError(SearcherError):
    message = 'error: you dont have a saved index'


class IndexOutDatedError(SearcherError):

    def __init__(self, msg: str):
        self.message = self.message.format(msg)

    message = 'error: your index for "{}" is outdated' \
              ' please, create new index'


class InvalidRootDirectory(SearcherError):

    def __init__(self, msg: str):
        self.message = self.message.format(msg)

    message = 'error: "{}" doesnt exist '


class RobotTxtNotFound(SearcherError):

    def __init__(self, msg):
        self.message = self.message.format(msg)

    message = 'error: robot.txt file "{}" want found'
