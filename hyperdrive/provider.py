import docker
import errno
import getpass
import hyperdrive
import os
import os.path
import uuid


class Docker:

    def __init__(self, base_url, name=None):
        self.base_url = base_url
        self.client = docker.DockerClient(base_url=base_url)
        self.image = self.client.image.get(name) if name else None

    @property
    def repository(self):
        return self.image[0].attrs['RepoTags'][-1] if self.image else None

    def build(self,
              base_image,
              path='./',
              tag='{}/hyperdrive-{}-{}'.format(hyperdrive.docker_registry,
                                               getpass.getuser(),
                                               os.path.basename(os.getcwd())),
              command=None,
              pull=True,
              rm=True,
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
                content = [
                    '# see: https://docs.docker.com/engine/reference/builder/ for Dockerfile reference\n',
                    'FROM {}\n'.format(base_image),
                    'COPY . .\n',
                ]
                if os.path.isfile(os.path.join(path, 'requirements.txt')):
                    content += [
                        'COPY ./requirements.txt .',
                        'RUN pip install -r ./requirements.txt'
                    ]
                if command:
                    content.append('CMD {}'.format(command))
                f.writelines(content)

        self.image = self.client.images.build(
            path=path, tag=tag, pull=pull, rm=rm, **kwargs)

        return self.image

    def push(self, repository=None, stream=False, **kwargs):
        if repository is None:
            repository = self.repository
        self.client.images.push(repository, stream=stream, **kwargs)

    def run(self, command, remove=True, shm_size=1000000000, **kwargs):
        return self.client.containers.run(
            self.image,
            command=command,
            remove=remove,
            shm_size=shm_size,
            **kwargs)

    def remove(self, image=None, force=True, **kwargs):
        if image is None:
            image = self.image.id
        # TODO: Handle stopping containers
        self.client.images.remove(image, force=force, **kwargs)
        self.client.images.prune()


class Pccl(Docker):

    def __init__(self, base_url, name=None):
        super(self.__class__, self).__init__(base_url)
        self.service = None
        if name:
            self.service = self.client.services.get(name)
            try:
                attrs = self.service.attrs
                img = attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
                self.image = self.client.images.get(img)
            except KeyError:
                pass

    def deploy(self,
               name='hyperdrive_{}_{}'.format(getpass.getuser(),
                                              str(uuid.uuid4())[:8]),
               mode=docker.types.ServiceMode('replicated', replicas=1),
               restart_policy=docker.types.RestartPolicy(condition='none'),
               **kwargs):
        self.service = self.client.services.create(
            self.repository,
            name=name,
            mode=mode,
            restart_policy=restart_policy,
            **kwargs)
        return self.service

    def logs(self, stdout=True, stderr=True, **kwargs):
        return self.service.logs(stdout=stdout, stderr=stderr, **kwargs)

    def status(self):
        return self.service.tasks()

    def remove(self):
        self.service.remove()
        super(Pccl, self).remove()
