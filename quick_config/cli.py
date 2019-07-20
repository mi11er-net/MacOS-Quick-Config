"""MacOS Quick Config

    Usage:
        quick-config [options]

    Options:
        -s TEXT, --set TEXT
        -h --help              Show this screen.
        --version              Show version.

"""

from docopt import docopt
from . import __version__
from .helpers import *

#import quick_config.helpers as helpers

def run():
    """Main function."""
    arguments = docopt(__doc__, version=__version__)
    #print(arguments)

    global glob_check_num, glob_fail_fix_declined, glob_pass_after_fix, \
           glob_fail_fix_fail, glob_fail_fix_skipped, glob_pass_no_fix, \
           glob_check_skipped

    args = get_sys_args()
    const.ENABLE_DEBUG_PRINT = args['debug-print']
    const.WRITE_TO_LOG_FILE = args['write-to-log-file']
    const.PROMPT_FOR_FIXES = not args['no-prompt']
    const.ATTEMPT_FIXES = not args['report-only']
    const.SKIP_SUDO_TESTS = args['skip-sudo-checks']

    dprint_settings()

    _print_banner()

    config_checks = read_config(const.DEFAULT_CONFIG_FILE)
    completely_failed_tests = []
    for config_check in config_checks:
        check_result = run_check(config_check)
        if check_result in (CheckResult.explicit_fail, CheckResult.no_pass):
            if not const.ATTEMPT_FIXES:
                #report-only mode
                glob_fail_fix_skipped += 1
                glob_check_num += 1
                continue

            if config_check.fix is None and config_check.sudo_fix is None:
                #no automatic fix available
                if config_check.manual_fix is not None:
                    completely_failed_tests.append(glob_check_num)
                else:
                    write_str(("Could not satisfy test #%d but no manual fix "
                               "specified.") % glob_check_num, debug=True)
            else:
                #attempt fix, but prompt user first if appropriate
                if const.PROMPT_FOR_FIXES:
                    prompt_default = True
                    descriptor = ''
                    if config_check.confidence == Confidence.recommended:
                        prompt_default = const.FIX_RECOMMENDED_BY_DEFAULT
                        descriptor = const.RECOMMENDED_STR + ' '
                    elif config_check.confidence == Confidence.experimental:
                        prompt_default = const.FIX_EXPERIMENTAL_BY_DEFAULT
                        descriptor = const.EXPERIMENTAL_STR + ' '

                    next_fix_command = config_check.fix
                    if next_fix_command is None:
                        next_fix_command = config_check.sudo_fix

                    question = (("\tApply the following %s fix? This will "
                                 "execute  this command:\n\t\t'%s'") %
                                (descriptor, next_fix_command))
                    if prompt.query_yes_no(question=question,
                                           default=_bool_to_yes_no(prompt_default)):
                        fixed = do_fix_and_test(config_check)
                        write_str("Value of fixed is: %s" % str(fixed),
                                  debug=True)
                        if fixed:
                            glob_pass_after_fix += 1
                        else:
                            glob_fail_fix_fail += 1
                            if config_check.manual_fix is not None:
                                completely_failed_tests.append(glob_check_num)
                            else:
                                write_str(("Could not satisfy test #%d but no "
                                           "manual fix specified.") %
                                          glob_check_num, debug=True)
                    else:
                        #user declined fix
                        glob_fail_fix_declined += 1
                else:
                    fixed = do_fix_and_test(config_check)
                    write_str("Value of fixed is: %s" % str(fixed), debug=True)
                    if fixed:
                        glob_pass_after_fix += 1
                    else:
                        glob_fail_fix_fail += 1
                        if config_check.manual_fix is not None:
                            completely_failed_tests.append(glob_check_num)
                        else:
                            write_str(("Could not satisfy test #%d but no "
                                       "manual fix specified.") %
                                      glob_check_num, debug=True)

        elif check_result == CheckResult.explicit_pass:
            glob_pass_no_fix += 1
        elif check_result == CheckResult.all_skipped:
            glob_check_skipped += 1

        glob_check_num += 1

    print_tallies()

    if len(completely_failed_tests) > 0:
        write_str("==========================")
        write_str(("%s%d tests could not be automatically fixed, but manual "
                   "instructions are available. Please manually remediate these"
                   " problems and re-run the tool:%s") %
                  (const.COLORS['BOLD'], len(completely_failed_tests),
                   const.COLORS['ENDC']))
        for test_num in completely_failed_tests:
            description = config_checks[test_num - 1].description
            instructions = config_checks[test_num - 1].manual_fix
            write_str("TEST #%d: %s" % (test_num, description))
            write_str("%s" % _underline_hyperlink(instructions))
            write_str("==========================")
    else:
        write_str("List of completely failed tests is empty.", debug=True)

    if const.WRITE_TO_LOG_FILE:
        print("Wrote results to %s'%s'%s. Please review the contents before "
              "submitting them to third parties, as they may contain sensitive "
              "information about your system." %
              (const.COLORS['BOLD'], const.LOG_FILE_LOC, const.COLORS['ENDC']))


if __name__ == "__main__":
    main()
