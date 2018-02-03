from __future__ import print_function
import sys
import os
import shutil
import glob
from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand
import hyperdrive


class PyTest(TestCommand):
    description = 'run unit tests'

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--verbose', '--capture=no']
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


class Clean(Command):
    description = 'remove build files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        def respect_dry_run(path, fn):
            if self.dry_run:
                print('would remove {}...'.format(path))
            else:
                if self.verbose > 1:
                    print('removing {}...'.format(path))
                fn(path)

        for d in [
                './dist/', './build/', './__pycache__/',
                './hyperdrive.egg-info/', './test/__pycache__'
        ]:
            if os.path.isdir(d):
                respect_dry_run(d, shutil.rmtree)

        for f in glob.glob('*.pyc'):
            respect_dry_run(f, os.remove)


class Tag(Command):
    description = 'tag the release with git'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("git tag {}".format(hyperdrive.__version__))
        os.system("git push --tags")


setup(
    name='hyperdrive',
    version=hyperdrive.__version__,
    url='http://github.com/BYU-PCCL/hyperdrive',
    license=hyperdrive.__licence__,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['hyperdrive = hyperdrive.__main__:main'],
    },
    install_requires=['docker>=3.0.0'],
    tests_require=['pytest'],
    dependency_links=[
        "https://github.com/BYU-PCCL/docker-py/tarball/master#egg=docker-3.0.1"
    ],
    cmdclass={
        'test': PyTest,
        'clean': Clean,
        'tag': Tag,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
    zip_safe=False)
