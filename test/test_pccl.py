import pytest
import hyperdrive
import docker


@pytest.fixture(scope="module")
def client():
    return docker.from_env()

@pytest.fixture(scope="module")
def docker_service():
    return hyperdrive.pccl.Pccl()

def test_build():
    pass
