from textwrap import dedent

class FileTagException(Exception): pass

class UsageError(Exception):
    def __init__(self, error, cmd=None):
        self.cmd = cmd
        super(UsageError, self).__init__(error)

class FileTagIndexCorrupt(FileTagException): pass
class NoTagDatabaseForPath(FileTagException): pass
class NoFileTagRoot(FileTagException): pass
class SpecifiedFileDoesNotExist(FileTagException): pass
class InvalidTagName(FileTagException): pass


class FilterSyntaxError(FileTagException):
    def __init__(self, msg, expression, pos):
        msg = dedent("""\
            Error in expression: {msg}
            {expression}
            {pad}^""".format(
                expression = expression,
                pad = ' '*pos,
                msg = msg))
        super(FilterSyntaxError, self).__init__(msg)