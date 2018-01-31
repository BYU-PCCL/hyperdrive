import docker
import errno
import hyperdrive
import os
import os.path
import uuid


class Docker:



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


class Pccl(Docker):

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
