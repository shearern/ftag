class FileTagException(Exception): pass

class FileTagIndexCorrupt(FileTagException): pass
class FilePathNotInRoot(FileTagException): pass
class NoFileTagRoot(FileTagException): pass
class SpecifiedFileDoesNotExist(FileTagException): pass
