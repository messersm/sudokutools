from setuptools import setup

import sudokutools

version = sudokutools.__version__
description = sudokutools.__doc__.split('\n')[0]
long_description = sudokutools.__doc__

setup(
    name = 'sudokutools',
    packages = ['sudokutools', 'sudokutools.tests'],
    entry_points={
        'console_scripts': [
            'sudokutools = sudokutools.__main__:main',
        ],
    },
    version = version,
    description = description,
    long_description=long_description,
    author = sudokutools.__author__,
    author_email = sudokutools.__email__,
    license = sudokutools.__license__,
    url = 'https://github.com/messersm/sudokutools',
    download_url = 'https://github.com/messersm/sudokutools/tarball/%s' % version,
    keywords = ['sudokutools'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
