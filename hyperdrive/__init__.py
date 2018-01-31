"""
hyperdrive - run your python projects at lightspeed.
"""
import os

__version__ = '0.0.1'
__author__ = 'William Myers'
__licence__ = 'MIT'

default_docker_manager_url = os.environ.get('HYPERDRIVE_DOCKER_MANAGER_URL',
                                            'tcp://reaper.cs.byu.edu:2375')

default_docker_builder_url = os.environ.get('HYPERDRIVE_DOCKER_BUILDER_URL',
                                            'unix://var/run/docker.sock')

default_docker_base_image = os.environ.get(
    'HYPERDRIVE_DOCKER_BASE_IMAGE', 'tensorflow/tensorflow:latest-gpu-py3')

docker_registry = 'localhost:5000'
