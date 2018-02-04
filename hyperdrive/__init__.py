"""
hyperdrive - run your python projects at lightspeed.
"""
import os

__version__ = '0.0.2'
__author__ = 'William Myers'
__licence__ = 'MIT'

default_docker_manager_url = os.environ.get('HYPERDRIVE_DOCKER_MANAGER_URL',
                                            'tcp://monster.cs.byu.edu:2375')

default_docker_base_image = os.environ.get(
    'HYPERDRIVE_DOCKER_BASE_IMAGE', 'tensorflow/tensorflow:latest-gpu-py3')

docker_registry = '127.0.0.1:5000'
