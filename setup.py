from setuptools import setup, find_packages
import hyperdrive

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
        'boto',
        'docker'
    ],
    zip_safe=False)
