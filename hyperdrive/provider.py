import docker
import dockerfile
import getpass
import hyperdrive
import os
import os.path
import re
import uuid


class Docker:

    def __init__(self, base_url, name=None):
        self.base_url = base_url
        self.client = docker.DockerClient(base_url=base_url)
        self.image = self.client.image.get(name) if name else None

    @property
    def repository(self):
        return self.image[0].attrs['RepoTags'][-1] if self.image else None

    def _dockerfile_content(self, base_image, command, dockerfile_path,
                            add_pip_cmd):
        content = []

        try:
            has_base_image_cmd = False
            has_copy_cmd = False
            has_pip_cmd = False
            cmd_instructions_count = 0

            for instruction in dockerfile.parse_file(str(dockerfile_path)):
                if instruction.cmd == 'from':
                    has_base_image_cmd = True
                elif instruction.cmd == 'copy':
                    has_copy_cmd = True
                elif instruction.cmd in ('cmd', 'entrypoint'):
                    cmd_instructions_count += 1
                elif instruction.cmd == 'run':
                    if not has_pip_cmd and re.search(
                            "pip.*install.*requirements", instruction.original,
                            re.IGNORECASE):
                        has_pip_cmd = True
                content.append('{}\n'.format(instruction.original))

            if not has_base_image_cmd:
                content.insert(0, 'FROM {}\n'.format(base_image))
            if not has_copy_cmd:
                content.insert(1, 'COPY . .\n')
            if cmd_instructions_count == 0 and command:
                content.append('CMD {}\n'.format(command))
                cmd_instructions_count = 1
            if add_pip_cmd and not has_pip_cmd:
                content.insert(
                    len(content) - cmd_instructions_count,
                    'RUN pip install -r ./requirements.txt\n')
        except dockerfile.GoIOError:
            content = [
                'FROM {}\n'.format(base_image),
                'COPY . .\n',
            ]
            if add_pip_cmd:
                content.append('RUN pip install -r ./requirements.txt\n')
            if command:
                content.append('CMD {}\n'.format(command))

        return content

    def build(self,
              base_image,
              path=os.getcwd(),
              tag='{}/hyperdrive-{}-{}'.format(hyperdrive.docker_registry,
                                               getpass.getuser(),
                                               os.path.basename(os.getcwd())),
              command=None,
              pull=True,
              rm=True,
              shmsize=1000000000,
              **kwargs):
        dockerfile_path = os.path.join(path, 'Dockerfile')
        add_pip_cmd = os.path.isfile(os.path.join(path, 'requirements.txt'))
        dockerfile_content = self._dockerfile_content(
            base_image, command, dockerfile_path, add_pip_cmd)

        # TODO: make this atomic
        with open(dockerfile_path, 'w') as f:
            f.writelines(dockerfile_content)

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

    def list(self, **kwargs):
        return self.client.services.list(**kwargs)

    def logs(self, stdout=True, stderr=True, **kwargs):
        return self.service.logs(stdout=stdout, stderr=stderr, **kwargs)

    def status(self):
        return self.service.tasks()

    def remove(self):
        self.service.remove()
        super(Pccl, self).remove()
