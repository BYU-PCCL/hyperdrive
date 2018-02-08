"""
hyperdrive - run your python projects at lightspeed.
"""
import os

__version__ = '0.1.0.alpha1'
__author__ = 'William Myers'
__licence__ = 'MIT'

default_docker_manager_url = os.environ.get('HYPERDRIVE_DOCKER_MANAGER_URL',
                                            'tcp://monster.cs.byu.edu:2375')

default_docker_base_image = os.environ.get('HYPERDRIVE_DOCKER_BASE_IMAGE',
                                           'ufoym/deepo')

docker_registry = '127.0.0.1:5000'
