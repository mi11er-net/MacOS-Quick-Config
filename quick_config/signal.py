"""
    Signal Handling
"""

import sys
import signal

def setup():
    """ Setup signal handeling """
    signal.signal(signal.SIGINT, _graceful_sig_exit)
    signal.signal(signal.SIGTERM, _graceful_sig_exit)

def _graceful_sig_exit(*_):
    """ exit garcefully """
    print('Exiting')
    sys.exit()

# TODO: ref for looping
# https://github.com/kysely/atomicloop/blob/master/atomicloop/__init__.py
