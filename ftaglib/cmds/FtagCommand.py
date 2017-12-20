from abc import ABCMeta, abstractmethod, abstractproperty


class FtagCommand(object):
    '''Base for sub-commands for ftag.py'''
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        '''Return the default name for this command'''


    def aliases(self):
        '''List of additional command names that can be used to invoke this command'''
        return tuple()