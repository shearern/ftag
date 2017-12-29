import os
import collections

from .exceptions import SpecifiedFileDoesNotExist

def all_parents(path):
    '''
    Return all parent directories to a path
    '''

    found = set()
    parent = os.path.dirname(path)
    while parent not in found:
        yield parent
        found.add(parent)
        parent = os.path.dirname(path)


def find_root(of_path):
    '''
    Walk up the directory tree until we find the folder with .file-tags.json

    :param of_path: Path to start looking under
    :return: Path to root folder
    '''

    # Check provided path
    if os.path.isdir(of_path):
        if os.path.exists(os.path.join(of_path, '.file-tags.json')):
            return of_path

    # Check parents
    for parent in all_parents(of_path):
        if os.path.exists(os.path.join(parent, '.file-tags.json')):
            return parent

    return None


def find_all_files(root):
    '''Return all files under the root (relative to the root)'''

    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isfile(path):
            yield name
        elif os.path.isdir(path):
            for sub_path in find_all_files(path):
                yield os.path.join(name, sub_path)


def expand_paths(paths, recurse=False):
    '''
    Given a set of paths to act on, determine the paths of actual files to work on
    '''
    for path in paths:

        # Error if file doesn't exist
        if not os.path.exists(path):
            raise SpecifiedFileDoesNotExist("File doesn't exist: " + path)

        # For directories, return all files under them if recursing
        if os.path.isdir(path):
            yield path
            if recurse:
                for sub_path in find_all_files(path):
                    yield os.path.join(path, sub_path)


        # For files, just return the file
        elif os.path.isfile(path):
            yield path


# ref: https://www.kunxi.org/blog/2014/05/lru-cache-in-python/
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        '''
        Get cached value

        Throws KeyError on miss
        '''
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

    def __getitem__(self, key):
        return self.get(key)
    def __setitem__(self, key, value):
        self.set(key, value)

