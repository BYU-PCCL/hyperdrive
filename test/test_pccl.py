import hyperdrive.provider
import pytest


@pytest.fixture(scope='module')
def docker_service():
    import os
    pccl = hyperdrive.provider.Pccl(base_url='tcp://reaper.cs.byu.edu:2375')
    pccl.build('python:3-alpine', path=os.path.abspath('./test/fixtures'))
    return pccl


def test_deploy(docker_service):
    assert docker_service.deploy()


def test_status(docker_service):
    assert docker_service.status()


def test_destroy(docker_service):
    assert docker_service.destroy()
