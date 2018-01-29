import pytest
import hyperdrive.provider


@pytest.fixture(scope='module')
def docker():
    return hyperdrive.provider.Docker(base_url='tcp://doctor.cs.byu.edu:2375')


def test_build(docker):
    import os
    assert docker.build(path=os.path.abspath('./test/fixtures'), quiet=False)


def test_run_cpu(docker):
    assert docker.run(command=['python', 'test.py', 'Hello', 'world!'])


def test_run_gpu(docker):
    assert docker.run(
        command=['python', 'test.py', 'Hello', 'world!'], runtime='nvidia')
