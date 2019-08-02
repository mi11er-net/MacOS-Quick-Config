"""MacOS Quick Config"""

import click
from . import settings
from . import __version__
from . import helpers
from . import prompt

@click.group()
@click.option('--apply/--no-apply', default=None,
              help='Should fixes be applied. [Default: apply]')
@click.option('--log/--no-log', default=None,
              help='Should output be written to a log. [Default: log]')
@click.option('--sudo/--no-sudo', 'sudo', default=None,
              help='Should sudo checks be performed. [Default: sudo]')
@click.option('--prompt/--no-prompt', default=None,
              help='Should user be promted before apply every fix. [Default: prompt] ')
@click.option('-v', '--verbose', count=True,
              help='Enables verbose output for debugging.')
@click.version_option()
@click.help_option('--help', '-h')
def cli(**kwargs):
    """
        Run checks aginst the MacOS configuration and apply fixes if necessary.

        Setting options on the command line will override their defaults
        and what is set in the config file.
    """

    settings.init(**kwargs)
    helpers.print_banner()

    config_checks = helpers.read_config(settings.DEFAULT_CONFIG_FILE)
    completely_failed_tests = []
    for config_check in config_checks:
        check_result = helpers.run_check(settings.TALLIES, config_check)
        if check_result in (helpers.CheckResult.explicit_fail, helpers.CheckResult.no_pass):
            if not settings.APPLY:
                #report-only mode
                settings.TALLIES.fail_fix_skipped += 1
                settings.TALLIES.check_num += 1
                continue

            if config_check.fix is None and config_check.sudo_fix is None:
                #no automatic fix available
                if config_check.manual_fix is not None:
                    completely_failed_tests.append(settings.TALLIES.check_num)
                else:
                    helpers.write_str(("Could not satisfy test #%d but no manual fix "
                                       "specified.") % settings.TALLIES.check_num, debug=True)
            else:
                #attempt fix, but prompt user first if appropriate
                if settings.PROMPT:
                    prompt_default = True
                    descriptor = ''
                    if config_check.confidence == helpers.Confidence.recommended:
                        prompt_default = settings.FIX_RECOMMENDED_BY_DEFAULT
                        descriptor = settings.RECOMMENDED_STR + ' '
                    elif config_check.confidence == helpers.Confidence.experimental:
                        prompt_default = settings.FIX_EXPERIMENTAL_BY_DEFAULT
                        descriptor = settings.EXPERIMENTAL_STR + ' '

                    next_fix_command = config_check.fix
                    if next_fix_command is None:
                        next_fix_command = config_check.sudo_fix

                    question = (("\tApply the following %s fix? This will "
                                 "execute  this command:\n\t\t'%s'") %
                                (descriptor, next_fix_command))
                    if prompt.query_yes_no(question=question,
                                           default=helpers.bool_to_yes_no(prompt_default)):
                        fixed = helpers.do_fix_and_test(settings.TALLIES, config_check)
                        helpers.write_str("Value of fixed is: %s" % str(fixed),
                                          debug=True)
                        if fixed:
                            settings.TALLIES.pass_after_fix += 1
                        else:
                            settings.TALLIES.fail_fix_fail += 1
                            if config_check.manual_fix is not None:
                                completely_failed_tests.append(settings.TALLIES.check_num)
                            else:
                                helpers.write_str(("Could not satisfy test #%d but no "
                                                   "manual fix specified.") %
                                                  settings.TALLIES.check_num, debug=True)
                    else:
                        #user declined fix
                        settings.TALLIES.fail_fix_declined += 1
                else:
                    fixed = helpers.do_fix_and_test(settings.TALLIES, config_check)
                    helpers.write_str("Value of fixed is: %s" % str(fixed), debug=True)
                    if fixed:
                        settings.TALLIES.pass_after_fix += 1
                    else:
                        settings.TALLIES.fail_fix_fail += 1
                        if config_check.manual_fix is not None:
                            completely_failed_tests.append(settings.TALLIES.check_num)
                        else:
                            helpers. write_str(("Could not satisfy test #%d but no "
                                                "manual fix specified.") %
                                               settings.TALLIES.check_num, debug=True)

        elif check_result == helpers.CheckResult.explicit_pass:
            settings.TALLIES.pass_no_fix += 1
        elif check_result == helpers.CheckResult.all_skipped:
            settings.TALLIES.check_skipped += 1

        settings.TALLIES.check_num += 1

    settings.TALLIES.print()

    if not completely_failed_tests:
        helpers.write_str("==========================")
        helpers.write_str(("%s%d tests could not be automatically fixed, but manual "
                           "instructions are available. Please manually remediate these"
                           " problems and re-run the tool:%s") %
                          (settings.COLORS['BOLD'], len(completely_failed_tests),
                           settings.COLORS['ENDC']))
        for test_num in completely_failed_tests:
            description = config_checks[test_num - 1].description
            instructions = config_checks[test_num - 1].manual_fix
            helpers.write_str("TEST #%d: %s" % (test_num, description))
            helpers.write_str("%s" % helpers.underline_hyperlink(instructions))
            helpers.write_str("==========================")
    else:
        helpers.write_str("List of completely failed tests is empty.", debug=True)

    if settings.LOG:
        print("Wrote results to %s'%s'%s. Please review the contents before "
              "submitting them to third parties, as they may contain sensitive "
              "information about your system." %
              (settings.COLORS['BOLD'], settings.LOG_FILE_LOC, settings.COLORS['ENDC']))

#@cli.command('show-config')
#def show_config:
#    pass

if __name__ == "__main__":
    cli()
