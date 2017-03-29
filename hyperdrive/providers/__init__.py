import abc


class ClusterProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self):
        raise NotImplementedError('must implement `initialize`')

    @abc.abstractmethod
    def deploy(self):
        raise NotImplementedError('must implement `deploy`')

    @abc.abstractmethod
    def status(self):
        raise NotImplementedError('must implement `status`')


    @abc.abstractmethod
    def destroy(self):
        raise NotImplementedError('must implement `destroy`')
