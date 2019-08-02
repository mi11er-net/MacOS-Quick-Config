''' Settings module '''
import datetime
import time
import quick_config.settings as settings
from quick_config.helpers import write_str

def init(**kwargs):
    ''' Read config file and intialize all settings '''
    settings.VERBOSITY = kwargs['verbose'] if kwargs['verbose'] is not None else settings.VERBOSITY
    settings.LOG = kwargs['log'] if kwargs['log'] is not None else settings.LOG
    settings.APPLY = kwargs['apply'] if kwargs['apply'] is not None else settings.APPLY
    settings.PROMPT = kwargs['prompt'] if kwargs['prompt'] is not None else settings.PROMPT
    settings.SUDO = kwargs['sudo'] if kwargs['sudo'] is not None else settings.SUDO
    debug()

def debug():
    """Prints current global flags when debug printing is enabled."""
    write_str("VERBOSITY: %s" % str(settings.VERBOSITY),
              debug=True)
    write_str("LOG: %s" % str(settings.LOG),
              debug=True)
    write_str("PROMPT: %s" % str(settings.PROMPT), debug=True)
    write_str("APPLY: %s" % str(settings.APPLY), debug=True)
    write_str("SUDO: %s" % str(settings.SUDO), debug=True)

def get_timestamp():
    """Genereate a current timestamp that won't break a filename."""
    timestamp_format = '%Y-%m-%d_%H-%M-%S'
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime(timestamp_format)
    return timestamp
