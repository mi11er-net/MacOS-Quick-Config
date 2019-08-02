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
    _debug()

def _debug():
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
class Tallies:
    ''' Manage Tallies '''
    check_num = 1

    #counters
    pass_no_fix = 0,
    pass_after_fix = 0
    fail_fix_fail = 0
    fail_fix_skipped = 0
    fail_fix_declined = 0
    check_skipped = 0
    fix_skipped_no_sudoer = 0

    def print(self):
        """Prints totals of the various possible outcomes of config checks."""
        total_checks = self.check_num - 1
        total_passed = self.pass_no_fix + self.pass_after_fix
        total_failed = (self.fail_fix_fail + self.fail_fix_skipped +
                        self.fail_fix_declined + self.check_skipped)

        out = _trim_block('''
        Configurations passed total:                          %s
        Configurations failed or skipped total:               %s
        Configurations passed without applying fix:           %s
        Configurations passed after applying fix:             %s
        Configurations failed and fix failed:                 %s
        Configurations failed and fix skipped:                %s
        Configurations failed and fix declined:               %s
        Configurations failed and fix failed for non-sudoer:  %s
        Configuration checks skipped:                         %s
        ''' % (_number_and_pct(total_passed, total_checks, 'pass'),
               _number_and_pct(total_failed, total_checks, 'fail'),
               _number_and_pct(self.pass_no_fix, total_checks, 'pass'),
               _number_and_pct(self.pass_after_fix, total_checks, 'pass'),
               _number_and_pct(self.fail_fix_fail, total_checks, 'fail'),
               _number_and_pct(self.fail_fix_skipped, total_checks, 'fail'),
               _number_and_pct(self.fail_fix_declined, total_checks, 'fail'),
               _number_and_pct(self.fix_skipped_no_sudoer, total_checks, 'fail'),
               _number_and_pct(self.check_skipped, total_checks, 'skip')))

        write_str(out)

def _number_and_pct(num, total, result):
    assert result in ('pass', 'fail', 'skip')
    if result == 'pass':
        color = settings.COLORS['OKGREEN']
    elif result == 'fail':
        color = settings.COLORS['FAIL']
    elif result == 'skip':
        color = settings.COLORS['OKBLUE']
    end_color = '' if color == '' else settings.COLORS['ENDC']
    return "%s%d (%s)%s" % (color, num, _pct(num, total), end_color)

def _trim_block(multiline_str):
    """Remove empty lines and leading whitespace"""
    result = ""
    for line in multiline_str.split("\n"):
        line = line.lstrip()
        if line != '':
            result += "%s\n" % line
    return result.rstrip() #remove trailing newline

def _pct(num, total):
    return "{0:.2f}".format(100.0 * num / total) + '%'
