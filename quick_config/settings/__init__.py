''' Settings Module Init '''
from ._settings import init
from ._settings import get_timestamp
from ._settings import Tallies

DEFAULT_OUTPUT_LOCATION = "~/Documents/"
DEFAULT_CONFIG_FILE = "osx-config.json"
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

LOG_FILE_NAME = 'osx-config-check_%s.log' % get_timestamp()
del get_timestamp

LOG_FILE_LOC = DEFAULT_OUTPUT_LOCATION + LOG_FILE_NAME

TALLIES = Tallies()
del Tallies


# cli options
VERBOSITY = 0
LOG = True
PROMPT = True
APPLY = True
SUDO = True
