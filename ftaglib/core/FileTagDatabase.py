import os
import sqlite3

from .exceptions import FileTagIndexCorrupt


def normalize_path_for_index(path):
    return os.path.normpath(path).replace('\\', '/')


class FileTagDatabase(object):
    '''
    Index file that stores all the tags
    '''

    FILENAME='.file-tags.db'

    def __init__(self, path=None):
        '''
        :param path: Path to the index file (typically named .file-tags.json)
        '''
        self.path = None
        self.tags = dict()  # [tag] = set(paths)

        if path is not None:
            self.load(path)


    @staticmethod
    def initialize_new_db(path):

        if os.path.exists(path):
            os.unlink(path)

        db = sqlite3.connect(path)

        # Create tables
        c = db.cursor()
        c.execute('''
          create table paths
          (
            id      integer primary key,  -- Note: autoincrements
            path    text not null,
            type    char(1) not null,
            
            CONSTRAINT unique_path UNIQUE (path)
          )''')
        c.execute('''
          create table tags
          (
            id      integer primary key,  -- Note: autoincrements
            tag     varchar(30) not null,
            
            CONSTRAINT unique_tags UNIQUE (tag)
          )''')
        c.execute('''
          create table path_tags
          (
            path_id integer,  -- Note: autoincrements
            tag_id  integer,
            
            CONSTRAINT unique_path_tags UNIQUE (path_id, tag_id)
          )''')

        # Performence Indexes
        c.execute('''
          create index path_tags_path_id
          on path_tags (path_id)
        ''')
        # TODO: Keep?  Will probably just table scan anyways
        # TODO: Better to define foreign keys?
        c.execute('''
          create index path_tags_tag_id
          on path_tags (tag_id)
        ''')

        db.commit()
        db.close()


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

