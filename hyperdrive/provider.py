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

        # TODO: there has to be a better way to construct the Dockerfile content
        try:
            instructions = []

            def last_index(item, items, default_index=-1):
                index = default_index
                try:
                    index = max(i for i, v in enumerate(items) if v == item)
                except ValueError:
                    pass
                return index

            for instruction in dockerfile.parse_file(dockerfile_path):
                cmd = instruction.cmd

                if instruction.cmd == 'run' and re.search(
                        "pip.*install.*requirements", instruction.original,
                        re.IGNORECASE):
                    cmd = 'pip'
                content.append('{}\n'.format(instruction.original))
                instructions.append(cmd)

            from_cmd = 'FROM {}\n'.format(base_image)
            from_index = last_index('from', instructions)
            if from_index < 0:
                content.insert(0, from_cmd)
                instructions.insert(0, 'from')
            # TODO: find a better way to figure out if we should override 'FROM'
            elif base_image not in (
                    hyperdrive.default_docker_base_image_gpu,
                    hyperdrive.default_docker_base_image_cpu):
                content[from_index] = from_cmd

            workdir_index = last_index('workdir', instructions)
            if workdir_index < 0:
                workdir_loc = last_index('from', instructions) + 1
                content.insert(workdir_loc, 'WORKDIR /opt/\n')
                instructions.insert(workdir_loc, 'workdir')

            copy_index = last_index('copy', instructions)
            if copy_index < 0:
                copy_loc = last_index('workdir', instructions) + 1
                content.insert(copy_loc, 'COPY . .\n')
                instructions.insert(copy_loc, 'copy')

            if command:
                cmd = 'CMD {}\n'.format(command)
                cmd_index = last_index('cmd', instructions)
                if cmd_index < 0:
                    content.append(cmd)
                    instructions.append('cmd')
                else:
                    content[cmd_index] = cmd
                    instructions[cmd_index] = cmd

            if add_pip_cmd and last_index('pip', instructions) < 0:
                i = len(content) - 1
                first_cmd_instruction = min(
                    last_index('cmd', instructions, default_index=i),
                    last_index('entrypoint', instructions, default_index=i))
                content.insert(
                    first_cmd_instruction,
                    'RUN pip install -r ./requirements.txt\n')
        except dockerfile.GoIOError:
            content = [
                'FROM {}\n'.format(base_image),
                'WORKDIR /opt/\n',
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
        self.client.images.remove()
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

    def deploy(
            self,
            name='hyperdrive_{}_{}'.format(getpass.getuser(),
                                           str(uuid.uuid4())[:8]),
            mode=docker.types.ServiceMode('replicated', replicas=1),
            restart_policy=docker.types.RestartPolicy(condition='none'),
            mounts=['/mnt/pccfs:/mnt/pccfs:rw', '/home/remote:/home/remote:rw'],
            **kwargs):
        self.service = self.client.services.create(
            self.repository,
            name=name,
            mode=mode,
            restart_policy=restart_policy,
            mounts=mounts,
            **kwargs)
        return self.service

    def list(self, **kwargs):
        return self.client.services.list(**kwargs)

    def logs(self, stdout=True, stderr=True, **kwargs):
        return self.service.logs(stdout=stdout, stderr=stderr, **kwargs)

    def status(self):
        return self.service.tasks()

    def remove(self, **kwargs):
        self.service.remove()
        # super(Pccl, self).remove(**kwargs)  # FIXME
