import os

from .exceptions import FilePathNotInRoot

class TaggedFilePath(object):
    '''Path to a file that can be tagged'''

    def __init__(self, root, path):
        '''
        :param root: FileTagRoot
        :param path: Path to the file (relative to the root)
        '''
        self.__root = root
        self.__path = path

        # Check path belongs to the root
        if not root.is_parent_of(self.__path):
            raise FilePathNotInRoot("%s not under %s" % (self.__path, self.__root.path))


    def tags(self):
        return self.__root.index.get_tags_for_file(self.__idx_path)


    def add_tag(self, tag):
        self.__root.index.add_tag(self.__path, tag)

