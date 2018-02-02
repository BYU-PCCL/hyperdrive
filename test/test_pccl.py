import docker
import hyperdrive.provider
import pytest


@pytest.fixture(scope='function')
def docker_service(request):
    import os
    pccl = hyperdrive.provider.Pccl(base_url='tcp://monster.cs.byu.edu:2375')
    pccl.build('python:3-alpine', path=os.path.abspath('./test/fixtures'))
    request.addfinalizer(lambda: pccl.remove())
    return pccl


def test_deploy_cpu(docker_service):
    assert docker_service.deploy()


def test_deploy_gpu(docker_service):
    assert docker_service.deploy(
        resources=docker.types.Resources(generic_reservations=[
            docker.types.DescreteGenericResource(kind='gpu', value=1),
        ]))
