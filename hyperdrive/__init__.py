"""
hyperdrive - run your python projects at light speed.
"""
import os

__version__ = '0.1.1.beta2'
__author__ = 'William Myers'
__licence__ = 'MIT'

verbosity = 0

default_docker_manager_hostname = 'monster.cs.byu.edu'
default_docker_manager_url = os.environ.get(
    'HYPERDRIVE_DOCKER_MANAGER_URL',
    'tcp://{}:2375'.format(default_docker_manager_hostname))

default_docker_base_image_gpu = os.environ.get('HYPERDRIVE_DOCKER_BASE_IMAGE',
                                               'pccl/base:gpu')
default_docker_base_image_cpu = os.environ.get('HYPERDRIVE_DOCKER_BASE_IMAGE',
                                               'pccl/base:cpu')

docker_registry = '127.0.0.1:5000'
