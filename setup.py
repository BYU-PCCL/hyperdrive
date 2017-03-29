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
