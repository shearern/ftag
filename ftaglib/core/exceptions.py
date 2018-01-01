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