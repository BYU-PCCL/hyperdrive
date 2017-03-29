import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import hyperdrive


class PyTest(TestCommand):
    # `$ python setup.py test' simply installs minimal requirements
    # and runs the tests with no fancy stuff like parallel execution.
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--doctest-modules', '--verbose', './hyperdrive', './test'
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


setup(
    name='hyperdrive',
    version=hyperdrive.__version__,
    url='http://github.com/mwilliammyers/hyperdrive',
    license=hyperdrive.__licence__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hyperdrive = hyperdrive.__main__:main',
        ],
    },
    install_requires=[
        'docker'
    ],
    tests_require=[
        'pytest'
    ],
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
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
