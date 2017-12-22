
import os

from .exceptions import FilePathNotInRoot

from npath import File
from .TaggablePath import TaggablePath

class TaggableDirectory(File, TaggablePath):
    '''Path to a directory that can be tagged'''
