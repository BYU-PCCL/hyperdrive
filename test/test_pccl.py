import pytest
import hyperdrive
import docker


@pytest.fixture(scope="module")
def client():
    return docker.from_env()

@pytest.fixture(scope="module")
def docker_service():
    import hyperdrive.providers.cluster
    return hyperdrive.providers.cluster.Docker()

def test_initialize():
    pass
