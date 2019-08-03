''' Settings Module Init '''

from ._settings import init
from ._settings import Tallies
from .. import APP_NAME

##
# These can be set from the CLI and
# all need to be initated
##
APP_DIRECTORY = None
CONFIG_FILE = None
LOG = None
LOG_FILE = None
VERBOSITY = None

WARN_FOR_RECOMMENDED = True
WARN_FOR_EXPERIMENTAL = True
FIX_RECOMMENDED_BY_DEFAULT = True
FIX_EXPERIMENTAL_BY_DEFAULT = False
LOG_DEBUG_ALWAYS = True
API_FILENAME = './scripts/api.sh'
COLORS = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKGREEN': '\033[92m',
    'WARNING': '\033[93m',
    'RED': '\033[91m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

PASSED_STR = COLORS['OKGREEN'] + "PASSED!" + COLORS['ENDC']
FAILED_STR = COLORS['FAIL'] + "FAILED!" + COLORS['ENDC']
SKIPPED_STR = COLORS['OKBLUE'] + "SKIPPED!" + COLORS['ENDC']
NO_SUDO_STR = ("%s%s%s" %
               (COLORS['WARNING'],
                ("Insufficient privileges to perform this check. "
                 "Skipping."),
                COLORS['ENDC']))
RECOMMENDED_STR = ("%s%s%s" % (COLORS['BOLD'],
                               'RECOMMENDED',
                               COLORS['ENDC']))
EXPERIMENTAL_STR = ("%s%s%s" % (COLORS['BOLD'],
                                'EXPERIMENTAL',
                                COLORS['ENDC']))

SUDO_STR = ("%s%ssudo%s" %
            (COLORS['BOLD'], COLORS['RED'],
             COLORS['ENDC']))


TALLIES = Tallies()
del Tallies


# cli options
PROMPT = True
APPLY = True
SUDO = True
