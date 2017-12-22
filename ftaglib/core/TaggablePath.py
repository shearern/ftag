import os
import collections

from npath import Path

from .exceptions import FilePathNotInRoot


class NoTagDatabase(collections.MutableSet):

    def __iter__(self):
        return iter(list())

    def __len__(self):
        return 0

    def add(self, value):
        pass

    def __str__(self):
        return str(list())

    def __repr__(self):
        return "NoTagDatabase()"

    def discard(self, value):
        pass

    def __contains__(self, x):
        return False


class TagAccessor(collections.MutableSet):
    '''Containter like object to access tags'''

    def __init__(self, tag_db, path):
        self.db = tag_db
        self.path = path


    def all(self):
        '''
        All assigned tags as a list
        '''
        return self.db.get_tags_for(self.path)


    def __iter__(self):
        return iter(self.all())

    def __len__(self):
        return len(self.all())

    def add(self, tag):
        self.db.add_tag(self.path, tag)

    def __str__(self):
        return ", ".join(self.all)

    def __repr__(self):
        return repr(self.all())

    def discard(self, value):
        raise NotImplementedError()

    def __contains__(self, tag):
        return tag in self.all()


class TaggablePath(object):
    '''Path to a file that can be tagged'''

    def _link_ftag(self, explorer, database=None):
        self.__explorer = explorer
        self.__db = database
        self.__tag_path = Path(self).abs.make_relative_to(self.__db.root).s


    @property
    def taggable(self):
        return self.__db is not None


    @property
    def tags(self):
        if self.taggable:
            return TagAccessor(self.__db, self.__tag_path)
        else:
            return NoTagDatabase()


