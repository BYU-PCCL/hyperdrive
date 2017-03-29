import abc
from . import CloudProvider
import docker


class Docker(ClusterProvider):
    __metaclass__ = abc.ABCMeta

    def __init__(self, manager_ip):
        self.manager_ip = manager_ip
        self.client = docker.from_env()

    def initialize(self):
        pass

    def deploy(self):
        pass

    def status(self):
        pass

    def destroy(self):
        pass

    @abc.abstractmethod
    def build(self):
        raise NotImplementedError('must implement `build`')

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError('must implement `run`')
