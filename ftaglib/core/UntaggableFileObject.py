import os

from .exceptions import FilePathNotInRoot

from npath import InvalidFileObject

from .TaggablePath import TaggablePath

class UntaggableFileObject(InvalidFileObject, TaggablePath):
    '''
    Path to a file that can be tagged

    Note: Inherits TaggablePath, but .taggable == False
    '''


