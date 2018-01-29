#!/usr/bin/env python
"""The main entry point. Invoke as `hyperdrive' or `python -m hyperdrive'.
"""
import sys
import argparse
import hyperdrive.provider


def _port(arg):
    host_port, container_port = arg.split(':')
    return '{}/tcp'.format(host_port), container_port


def main():
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
    parser.add_argument(
        '--from',
        dest='base_image',
        default=hyperdrive.default_docker_base_image,
        help='the docker image to base built images from')
    parser.add_argument(
        '-p',
        '--publish',
        dest='port',
        action='append',
        type=_port,
        help='ports to publish to make them available externally'
        ' (example: `-p 8888:8888 -p 8081:8080`'
        ' maps external port 8888 to docker image port 8888 and 8081 to 8080)')

    args, _ = parser.parse_known_args()

    pccl = hyperdrive.provider.Pccl(base_url=args.manager_url)
    pccl.build(args.base_image, path='./', ports=dict(args.port or []))
    pccl.deploy()


if __name__ == '__main__':
    sys.exit(main())
