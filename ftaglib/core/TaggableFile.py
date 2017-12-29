import os

from npath import File
from .TaggablePath import TaggablePath

class TaggableFile(File, TaggablePath):
    '''Path to a file that can be tagged'''

