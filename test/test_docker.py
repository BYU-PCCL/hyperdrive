import hyperdrive.provider
import pytest


@pytest.fixture(scope='function')
def docker(request):
    d = hyperdrive.provider.Docker(base_url='tcp://monster.cs.byu.edu:2375')
    request.addfinalizer(lambda: d.remove())
    return d


def test_build(docker):
    import os
    assert docker.build(
        'python:3-alpine', path=os.path.abspath('./test/fixtures'))


def test_run_cpu(docker):
    assert docker.run(command=['python3', 'test.py', 'Hello', 'world!'])


def test_run_gpu(docker):
    assert docker.run(
        command=['python3', 'test.py', 'Hello', 'world!'], runtime='nvidia')
