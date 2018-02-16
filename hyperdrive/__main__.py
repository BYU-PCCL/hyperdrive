#!/usr/bin/env python
"""The main entry point. Invoke as `hyperdrive' or `python -m hyperdrive'.
"""
from __future__ import print_function
import argparse
import docker
import hyperdrive.provider
import yaml
import sys
from halo import Halo

ports = {}
resources = {}


class CommandAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ' '.join(values))


class StorePort(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        for kv in values.split(","):
            k, v = kv.split(":")
            ports[int(k)] = int(v)
        setattr(namespace, self.dest, ports)


class StoreResource(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        for kv in values.split(","):
            k, v = kv.split("=")
            try:
                resources[k] = int(v)
            except ValueError:
                resources[k] = v
        setattr(namespace, self.dest, resources)


def parse_args():
    parser = argparse.ArgumentParser(
        description=hyperdrive.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {}'.format(hyperdrive.__version__))

    parser.add_argument(
        '-v', '--verbose', action='count', default=0, help='increase verbosity')

    parser.add_argument(
        '-m',
        '--manager',
        dest='manager_url',
        default=hyperdrive.default_docker_manager_url,
        help='the url of a manager host for the cluster')

    subparsers = parser.add_subparsers(
        dest='command', help='interact with jobs on the cluster')
    subparsers.required = True

    deploy_parser = subparsers.add_parser('deploy', help='deploy a job')
    deploy_parser.add_argument('command', type=str, nargs='?',
                               help='command to run for the job')
    # HACK so help output only shows one command
    deploy_parser.add_argument('_command', type=str, nargs='*',
                               action=CommandAction,
                               help=argparse.SUPPRESS)

    deploy_parser.add_argument(
        '--from',
        dest='base_image',
        help='the docker image to base built images from (default: {} or {})'
             ''.format(hyperdrive.default_docker_base_image_cpu,
                       hyperdrive.default_docker_base_image_gpu))
    deploy_parser.add_argument(
        '-p',
        '--publish',
        dest='ports',
        metavar='EXTERNAL_PORT:CONTAINER_PORT',
        default={},
        action=StorePort,
        help='ports to publish to make them available externally'
             ' (example: `-p 8888:8888 -p 8081:8080` maps external port 8888'
             ' to docker image port 8888 and 8081 to 8080)')
    deploy_parser.add_argument(
        '-r',
        '--resources',
        metavar='RESOURCE',
        default={},
        action=StoreResource,
        help='resources necessary for the job'
             ' (example: `-r gpu=1` requests one gpu')

    subparsers.add_parser(
        'ls',
        help='list jobs, see also: http://{}:8080'.format(
            hyperdrive.default_docker_manager_hostname),
        aliases=['list'])

    status_parser = subparsers.add_parser('status', help='get status of jobs')
    status_parser.add_argument('job', nargs='+', help='the name of the job')

    logs_parser = subparsers.add_parser('logs', help='get logs for jobs')
    logs_parser.add_argument('job', nargs='+', help='the name of the job')
    logs_parser.add_argument(
        '-f',
        '--follow',
        action='store_true',
        help='keep connection open to read logs as they are sent from docker')
    logs_parser.add_argument(
        '-n', '--lines', default='all', help='number of log lines to print')

    remove_parser = subparsers.add_parser(
        'rm', help='remove jobs', aliases=['remove', 'delete', 'destroy'])
    remove_parser.add_argument('job', nargs='+', help='the name of the job')

    return parser.parse_known_args()


def run():
    args, _ = parse_args()

    hyperdrive.verbosity = args.verbose

    if args.command == 'deploy':
        pccl = hyperdrive.provider.Pccl(base_url=args.manager_url)

        with Halo(text='building image, this could take a while...') as loader:
            base_image = args.base_image
            if not base_image:
                base_image = hyperdrive.default_docker_base_image_cpu
                if any(True for r in args.resources if 'gpu' in r):
                    base_image = hyperdrive.default_docker_base_image_gpu

            # HACK so help output only shows one command
            cmd = args.command + ' ' + args._command if args.command else None
            pccl.build(base_image, path='./', command=cmd)
            loader.succeed('built image')

        with Halo(text='pushing image, this could take a while...') as loader:
            pccl.push()
            loader.succeed('pushed image')

        with Halo(text='deployging image...') as loader:
            r = docker.types.Resources(generic_reservations=args.resources)
            e = docker.types.EndpointSpec(mode='vip', ports=args.ports)
            pccl.deploy(resources=r, endpoint_spec=e)
            loader.succeed('deployed image')

        print(pccl.service.name)
    elif args.command in ('list', 'ls'):
        pccl = hyperdrive.provider.Pccl(base_url=args.manager_url)

        for service in pccl.list(filters={'name': 'hyperdrive'}):
            print(service.name)
            if hyperdrive.verbosity > 0:
                print(yaml.dump(service.attrs), end='\n')

    elif args.command == 'status':
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)
            print(yaml.dump(pccl.status()))
    elif args.command == 'logs':
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)

            print(j)
            for line in pccl.logs(follow=args.follow, tail=args.lines):
                print(line.decode())
    elif args.command in ('rm', 'remove', 'delete', 'destroy'):
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)
            pccl.remove()
            print(j)


def main():
    try:
        run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # TODO: log verbose error
        print(getattr(e, 'explanation', e))


if __name__ == '__main__':
    sys.exit(main())
