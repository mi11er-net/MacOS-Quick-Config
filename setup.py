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
    extras_require={
        'dev': [
            'pyinstaller',
            'pylint',
            'mamba',
            'expects'
        ]
    },
    entry_points='''
      [console_scripts]
      quick-config=quick_config.cli:run
    ''',
)
