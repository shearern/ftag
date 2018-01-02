import os

from .. import UsageError
from ..core.utils import expand_paths, validate_tag_name
from ..core import FtagExplorer
from .. import NoTagDatabaseForPath

class TagOperation(object):
    '''Add or remove tags from files'''

    def __init__(self, paths, add_tags=None, remove_tags=None):
        '''
        :param paths: Paths to act on (strings, as passed to tag command
        :param add_tags: Tags to add to paths
        :param remove_tags: Tags to remove from paths
        '''
        self.paths = paths
        self.add_tags = add_tags or list()
        self.remove_tags = remove_tags or list()
        self.recurse = False


    def do(self):

        explorer = FtagExplorer()

        # Walk over all supplied paths
        for path in expand_paths(self.paths, recurse=self.recurse):

            if not os.path.exists(path):
                raise UsageError(cmd=self, error="Path doesn't exist: " + path)

            path = explorer.get(path)

            if not path.taggable:
                raise NoTagDatabaseForPath("No tag database found for %s.  Need to run ftag init?" % (path))

            changed = False
            for tag in self.add_tags:
                if tag not in path.tags:
                    path.tags.add(tag)
                    changed = True
            for tag in self.remove_tags:
                if tag in path.tags:
                    path.tags.remove(tag)
                    changed = True

            if changed:
                yield path.s

        explorer.close_dbs()