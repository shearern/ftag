import os
import collections

from npath import Path

from .FileTagDatabase import FileTagDatabase
from .TaggableFile import TaggableFile
from .TaggableDirectory import TaggableDirectory
from .UntaggableFileObject import UntaggableFileObject

from .utils import LRUCache
from .utils import all_parents

class FtagExplorer(object):
    '''
    Utility to explore the file system and access tags

    This class is primarily responsible for transparently finding
    the tag databases for files and returning TaggableFile and
    TaggableDirectory objects to set and get tags.
    '''

    MAX_OPEN_DBS = 5

    def __init__(self):

        self._dbs = collections.OrderedDict()  # [path] = FileTagDatabase
        self._db_lookup_cache = LRUCache(1000)



    def find_db_for(self, path):
        '''
        Determine the tag database to use for tagging a give path

        :param path: Path to file or directory to be tagged
        :return: FileTagDatabase
        '''

        # Start with directory
        if not os.path.isdir(path):
            path = os.path.dirname(path)

        # Search up directory tree until we find a database
        db_path = self.__find_db_for_dir(path, set())
        if db_path is None:
            return None

        # See if DB is already open
        if db_path in self._dbs:
            return self._dbs[db_path]
        else:
            return self._open_db(db_path)


    def _open_db(self, path):

        path = os.path.normpath(os.path.abspath(path))

        # Before opening, see if we have too many open
        if len(self._dbs) >= self.MAX_OPEN_DBS:
            path, db = self.cache.popitem(last=False)
            db.close()

        # Open new db
        self._dbs[path] = FileTagDatabase(path)
        return self._dbs[path]


    def __find_db_for_dir(self, path, visited):
        '''recursive helper to find_db_for()'''

        visited.add(path)

        # Check in cache
        try:
            return self._db_lookup_cache[path]
        except KeyError:
            pass # Cache miss

        # Look to see if DB is here
        db_path = os.path.join(path, FileTagDatabase.FILENAME)
        if not os.path.exists(db_path):

            # Travel up file tree to find DB
            parent = os.path.dirname(path)
            if parent not in visited:
                db_path = self.__find_db_for_dir(parent, visited)

        # Cache results
        self._db_lookup_cache[path] = db_path
        return db_path


    def get(self, path):
        '''
        Get a taggable file object for the given path

        :param path: path to file to be acted on
        :return: TaggableFile or TaggableDirectory
        '''
        # Always work with abs
        path = Path(path).abs
        if not path.exists:
            raise OSError("File %s doesn't exist" % (path))

        # Find the appropriate database
        db = self.find_db_for(path.s)

        # Encapsulate in appropriate object
        if path.is_file:
            path = TaggableFile(path)
            path._link_ftag(explorer=self, database=db)
            return path
        elif path.is_dir:
            path = TaggableDirectory(path)
            path._link_ftag(explorer=self, database=db)
            return path
        else:
            path = UntaggableFileObject(path)
            path._link_ftag(explorer=self)
            return path

