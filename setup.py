""" App Setup"""

from setuptools import setup
from quick_config.__init__ import __version__ as version

setup(
    name='quick-config',
    version=version,
    packages=['quick_config'],
    install_requires=[
        'Click',
        'pyfiglet',
        'docopt'

    ],
    entry_points='''
      [console_scripts]
      quick-config=quick_config.__main__:cli
    ''',
)
