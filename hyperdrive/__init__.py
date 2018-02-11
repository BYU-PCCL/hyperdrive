"""
hyperdrive - run your python projects at lightspeed.
"""
import os

__version__ = '0.1.0.beta1'
__author__ = 'William Myers'
__licence__ = 'MIT'

verbosity = 0

default_docker_manager_hostname = 'doctor.cs.byu.edu'
default_docker_manager_url = os.environ.get(
    'HYPERDRIVE_DOCKER_MANAGER_URL',
    'tcp://{}:2375'.format(default_docker_manager_hostname))

default_docker_base_image = os.environ.get('HYPERDRIVE_DOCKER_BASE_IMAGE',
                                           'pccl/base')

docker_registry = '127.0.0.1:5000'
