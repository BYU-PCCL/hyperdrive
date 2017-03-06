from setuptools import setup

setup(
    name='hyperdrive',
    version='0.0.1',
    description='Clustering tools for the BYU PCCL',
    url='http://github.com/mwilliammyers/hyperdrive',
    author='BYU-PCCL',
    license='MIT',
    packages=['hyperdrive'],
    install_requires=[
        'ansible',
        'boto'
    ],
    zip_safe=False)
