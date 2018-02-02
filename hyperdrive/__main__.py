#!/usr/bin/env python
"""The main entry point. Invoke as `hyperdrive' or `python -m hyperdrive'.
"""
from __future__ import print_function
import argparse
import docker
import hyperdrive.provider
import sys

ports = {}
resources = {}


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
        '-m',
        '--manager',
        dest='manager_url',
        default=hyperdrive.default_docker_manager_url,
        help='the url of a manager host for the cluster')

    subparsers = parser.add_subparsers(
        dest='command', help='interact with jobs on the cluster')
    subparsers.required = True

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

    deploy_parser = subparsers.add_parser('deploy', help='deploy a job')
    deploy_parser.add_argument(
        '-c', '--command', dest='cmd', help='command to run for the job')
    deploy_parser.add_argument(
        '--from',
        dest='base_image',
        default=hyperdrive.default_docker_base_image,
        help='the docker image to base built images from')
    deploy_parser.add_argument(
        '-p',
        '--publish',
        dest='ports',
        metavar='EXTERNAL_PORT:CONTAINER_PORT',
        default={},
        action=StorePort,
        help='ports to publish to make them available externally'
        ' (example: `-p 8888:8888 -p 8081:8080`'
        ' maps external port 8888 to docker image port 8888 and 8081 to 8080)')
    deploy_parser.add_argument(
        '-r',
        '--resources',
        metavar='RESOURCE',
        default={},
        action=StoreResource,
        help='resources necessary for the job'
        ' (example: `-r gpu=1` requests one gpu')

    remove_parser = subparsers.add_parser('remove', help='remove jobs')
    remove_parser.add_argument('job', nargs='+', help='the name of the job')

    return parser.parse_known_args()


def run():
    args, _ = parse_args()

    if args.command == 'status':
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)

            from pprint import pprint
            pprint(pccl.status())
    elif args.command == 'logs':
        for j in args.job:
            pccl = hyperdrive.provider.Pccl(base_url=args.manager_url, name=j)

            print(j)
            for line in pccl.logs(follow=args.follow, tail=args.lines):
                print(line.decode())
    elif args.command == 'deploy':
        pccl = hyperdrive.provider.Pccl(base_url=args.manager_url)

        pccl.build(args.base_image, path='./', command=args.cmd)

        pccl.push()

        r = docker.types.Resources(generic_reservations=args.resources)
        e = docker.types.EndpointSpec(mode='vip', ports=args.ports)
        pccl.deploy(resources=r, endpoint_spec=e)

        print(pccl.service.name)
    elif args.command == 'remove':
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
