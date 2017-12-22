import os
import sqlite3

from .exceptions import FileTagIndexCorrupt


def normalize_path_for_index(path):
    path = os.path.normpath(path).replace('\\', '/').lstrip('/')
    return '/' + path


class FileTagDatabase(object):
    '''
    Index file that stores all the tags
    '''

    FILENAME='.file-tags.db'

    def __init__(self, path):
        '''
        :param path: Path to the index file
        '''
        self.path = path
        self.__db = sqlite3.connect(path)


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
            --type    char(1) not null,
            
            CONSTRAINT unique_path UNIQUE (path)
          )''')
        c.execute('''
          create table tags
          (
            id      integer primary key,  -- Note: autoincrements
            name    varchar(30) not null,
            
            CONSTRAINT unique_tags UNIQUE (name)
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


    @property
    def root(self):
        return os.path.abspath(os.path.dirname(self.path))


    def get_tags_for(self, path):
        '''
        Get any tags assigned to the given path

        TODO: sqlite3 doesn't seem to respect multiple cursors at
              times, so in general pull all tags at once for now.
              Maybe switch to generator in case a file has lots of tags?

        :param path: Path to retrieve for already normalized
        :return: list of tags
        '''
        path = normalize_path_for_index(path)
        sql = '''\
            select
                t.name
            from paths p
            left join path_tags pt on pt.path_id = p.id
            left join tags t on t.id = pt.tag_id
            where p.path = :path
        '''
        curs = self.__db.cursor()
        results = curs.execute(sql, {"path": path})
        results = [str(row[0]) for row in results.fetchall()]
        return results


    def _tag_id(self, tag):
        sql = '''
            select id
            from tags
            where name = :tag'''
        curs = self.__db.cursor()
        results = curs.execute(sql, {'tag': tag}).fetchone()
        if results is not None:
            return results[0]
        return None


    def _path_id(self, path):
        sql = '''
            select id
            from paths
            where path = :path'''
        curs = self.__db.cursor()
        results = curs.execute(sql, {'path': path}).fetchone()
        if results is not None:
            return results[0]
        return None


    def add_tag(self, path, tag):
        path = normalize_path_for_index(path)

        curs = self.__db.cursor()

        tag_id = self._tag_id(tag)
        if tag_id is None:
            curs.execute("""\
              insert into tags (name) values(:tag)
              """, {'tag': tag})
            tag_id = self._tag_id(tag)

        path_id = self._path_id(path)
        if path_id is None:
            curs.execute("""\
              insert into paths (path) values(:path)
              """, {'path': path})
            path_id = self._path_id(path)

        # TODO: Catch duplicate error
        try:
            curs.execute('''\
              insert into path_tags (path_id, tag_id)
              values (:path_id, :tag_id)
              ''', {'path_id': path_id, 'tag_id': tag_id})

        # Integrity error if duplicate
        except sqlite3.IntegrityError, e:
            if 'unique' not in str(e).lower():
                raise e

        self.__db.commit()



