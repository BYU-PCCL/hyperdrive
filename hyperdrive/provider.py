import abc
import os.path
import uuid
import os
import errno
import docker
import hyperdrive


class Provider(object):
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

    @abc.abstractmethod
    def build(self, path):
        raise NotImplementedError('must implement `build`')

    @abc.abstractmethod
    def run(self, command):
        raise NotImplementedError('must implement `run`')


class Docker(Provider):

    def __init__(self, base_url, client=None):
        if client is None:
            client = docker.DockerClient(base_url=base_url)
        self.client = client
        self.image = None

    def build(self,
              base_image,
              path='./',
              tag='pccl/hyperdrive-{}'.format(str(uuid.uuid4())[:8]),
              pull=True,
              shmsize=1000000000,
              **kwargs):
        dockerfile = os.path.join(path, 'Dockerfile')
        try:
            handle = os.open(dockerfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        else:
            with os.fdopen(handle, 'w') as f:
                f.writelines([
                    'FROM {}\n'.format(base_image),
                    'COPY . .\n',
                ])

        self.image = self.client.images.build(path=path, tag=tag, pull=pull)
        return self.image

    def run(self, command, remove=True, shm_size=1000000000, **kwargs):
        return self.client.containers.run(
            self.image,
            command=command,
            remove=remove,
            shm_size=shm_size,
            **kwargs)


class Pccl(Docker, Provider):

    def __init__(self, base_url):
        super(self.__class__, self).__init__(base_url)
        self.service = None

    def deploy(self,
               name='hyperdrive-{}'.format(str(uuid.uuid4())[:8]),
               mode=docker.types.ServiceMode('replicated', replicas=1),
               restart_policy=docker.types.RestartPolicy(condition='none'),
               **kwargs):
        self.service = self.client.services.create(
            self.image.attrs['RepoTags'][0],  # TODO: best way to get image?
            name=name,
            mode=mode,
            restart_policy=restart_policy,
            **kwargs)
        return self.service

    def status(self):
        return self.service.tasks()

    def destroy(self):
        return self.service.remove()
