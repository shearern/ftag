import os

from . import FileTagIndexFile


class FileTagRoot(object):
    '''Directory that all the file tag paths are relative to'''

    def __init__(self, path, index_path=None):
        self.__path = path

        if index_path is None:
            index_path = os.path.join(self.__path, '.file-tags.json')
        self.__index = FileTagIndexFile(index_path)


    def is_parent_of(self, path):
        return os.path.abspath(path).startswith(os.path.abspath(self.__path))


    @property
    def index(self):
        return self.__index

