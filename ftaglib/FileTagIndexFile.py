import os
import json

from .exceptions import FileTagIndexCorrupt


def normalize_path_for_index(path):
    return os.path.normpath(path).replace('\\', '/')


class FileTagIndexFile(object):
    '''Index file that stores all the tags'''

    def __init__(self, path=None):
        '''
        :param path: Path to the index file (typically named .file-tags.json)
        '''
        self.path = None
        self.tags = dict()  # [tag] = set(paths)

        if path is not None:
            self.load(path)


    def load(self, path):
        '''Load tags from file'''
        if path is None:
            path = self.path
        if path is None:
            raise Exception("Must specify path")
        try:
            with open(path, 'r') as fh:
                data = json.load(fh)
                if data.__class__ is not dict:
                    return Exception("JSON data is %s, not a dict" % (
                        data.__clas__.__name__))
                self.tags = dict()
                for tag, paths in data.items():
                    self.tags[tag] = set(paths)
            self.path = path
        except Exception as e:
            raise FileTagIndexCorrupt("Failed to read %s: %s" % (
                os.path.abspath(path), str(e)))


    def save(self, path=None):
        '''Save tags to file'''
        if path is None:
            path = self.path
        if path is None:
            raise Exception("Must specify path")
        try:
            with open(path, 'w') as fh:
                data = dict()
                for tag, paths in self.tags.items():
                    data[tag] = list(paths)
                json.dump(data, fh)
        except Exception as e:
            raise FileTagIndexCorrupt("Failed to save tags to %s: %s" % (
                os.path.abspath(path), str(e)))


    def add_tag(self, path, tag):
        path = normalize_path_for_index(path)
        try:
            self.tags[tag].add(path)
        except KeyError:
            self.tags[tag] = set()
            self.tags[tag].add(path)

