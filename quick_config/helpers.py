#!/usr/bin/env python
"""Checks the configuration of various osx options."""



from os.path import expanduser
import re
import time
from subprocess import Popen, PIPE, STDOUT
from warnings import warn
import json
from . import settings
from . import __version__ as VERSION




class CheckResult(object):
    """Each test can have one of three results, informing the next step."""
    explicit_pass = 1
    explicit_fail = 2
    no_pass = 3
    all_skipped = 4

def check_result_to_str(val):
    """Convert enum to string representation"""
    if val == CheckResult.explicit_pass:
        return settings.PASSED_STR
    elif val == CheckResult.explicit_fail:
        return settings.FAILED_STR
    elif val == CheckResult.no_pass:
        return settings.FAILED_STR
    elif val == CheckResult.all_skipped:
        return settings.SKIPPED_STR
    else:
        raise ValueError

class Confidence(object):
    """Likelihood that a configuration will create negative side-effects.

    A lower integer value indicates less likelihood that a configuration will
    cause problems with applications.
    """
    required = 1
    recommended = 2
    experimental = 3

class ConfigCheck(object):
    """Encapsulates configuration to check in operating system."""
    def __init__(self, tests, description, confidence, fix=None, sudo_fix=None,
                 manual_fix=None):
        """
        Args:

            tests (List[dict]): The ordered list of tests to be performed, each
                a `dict` with these attributes including command_pass and/or
                command_fail:
                    * type (str): "exact match" or "regex match"
                    * command (str)
                    * command_pass (Optional[str])
                    * command_fail (Optional[str])
                    * case_sensitive (bool)
            description (str): A human-readable description of the configuration
                being checked.
            confidence (str): "required", "recommended", or "experimental"
            fix (Optional[str]): The command to run if the configuration fails
                the check.
            sudo_fix (Optional[str]): A version of `fix` that requests
                administrative privileges from the operating system. This will
                only be executed if `fix` does not produce the desired config
                change.
            manual_fix (Optional[str]): Instructions to output to the user to
                manually remediate if a config cannot be fixed automatically.
        """
        assert isinstance(tests, list)
        assert tests is not False
        for test in tests:
            assert isinstance(test, dict), "%s" % str(test)
            assert test['type'] in ('exact match', 'regex match')
            assert 'command' in test
            assert 'command_pass' in test or 'command_fail' in test
            test['case_sensitive'] = bool(test['case_sensitive'])
        self.tests = tests

        self.description = description
        if confidence == 'required':
            self.confidence = Confidence.required
        elif confidence == 'recommended':
            self.confidence = Confidence.recommended
        elif confidence == 'experimental':
            self.confidence = Confidence.experimental
        else:
            raise ValueError

        #Optional args
        self.fix = fix #default: None
        self.sudo_fix = sudo_fix #default: None
        self.manual_fix = manual_fix #default: None

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()

def get_output_filename():
    """Get the filename of the file to write results to."""
    return (settings.DEFAULT_OUTPUT_LOCATION + "config-check_" +
            time.strftime("%Y%m%d%H%M%S") + ".txt")

def read_config(config_filename):
    """Read the expected system configuration from the config file."""

    config = None
    with open(config_filename, 'r') as config_file:
        config = json.loads(config_file.read())

    config_checks = []

    for config_check in config:
        if '_comment' in config_check:
            continue

        #Config MUST specify a description of the check
        description = config_check['description']
        write_str("Description: %s" % description, debug=True)

        #Config MUST indicate the confidence of the configuration check
        confidence = config_check['confidence']

        #Config MUST include at least one test obj
        tests = config_check['tests']

        #Config MUST specify a fix object
        assert 'fix' in config_check
        assert isinstance(config_check['fix'], dict)

        #Fix object must specify at least one of these:
        #command, sudo_command, manual
        assert ('command' in config_check['fix'] or
                'sudo_command' in config_check['fix'] or
                'manual' in config_check['fix'])
        fix = None
        sudo_fix = None
        manual_fix = None
        if 'command' in config_check['fix']:
            fix = config_check['fix']['command']
        if 'sudo_command' in config_check['fix']:
            sudo_fix = config_check['fix']['sudo_command']
        if 'manual' in config_check['fix']:
            manual_fix = config_check['fix']['manual']

        config_check_obj = ConfigCheck(
            tests=tests,
            description=description,
            confidence=confidence,
            fix=fix,
            sudo_fix=sudo_fix,
            manual_fix=manual_fix)
        config_checks.append(config_check_obj)

    return config_checks

def run_check(tallies, config_check, last_attempt=False, quiet_fail=False):
    """Perform the specified configuration check against the OS.

    Each config check may specify multiple test cases with early-succeed and/or
    early-fail parameters.

    These are the possible conditions resulting from run_check:
    1. One of the tests explicitly passed.
    2. One of the tests explicitly failed.
    3. All of the tests were run and none of them passed or failed. (This
        should be considered a fail.)
    4. All of the tests were skipped because we're skipping sudo checks and
        the only tests available require sudo privs.

    Args:
        config_check (`ConfigCheck`): The check to perform. May contain multiple
            commands to test.
        last_attempt (bool): Is this the last time the script checks this
            configuration, or will we check again during this run?
        quiet_fail (bool): Suppress print failed results to stdout?
            Default: False.

    Returns: `CheckResult`: The check explicitly passed, explicitly
        failed, never passed, or all checks were skipped.

    Raises: ValueError if result of _execute_check is not valid.
    """
    assert isinstance(config_check, ConfigCheck)

    #Assume all tests have been skipped until demonstrated otherwise.
    result = CheckResult.all_skipped
    for test in config_check.tests:
        #alert user if he might get prompted for admin privs due to sudo use
        if 'sudo ' in test['command']:
            if not settings.SUDO:
                write_str("Skipping test because app skipping sudo tests.",
                          debug=True)
            else:
                fancy_sudo_command = re.sub(
                    "sudo", settings.SUDO_STR, test['command'])
                write_str(("The next configuration check requires elevated "
                           "privileges; %syou may be prompted for your current "
                           "OS X user's password  below%s. The command to be "
                           "executed is: '%s'") %
                          (settings.COLORS['BOLD'], settings.COLORS['ENDC'],
                           fancy_sudo_command))

        if 'sudo ' not in test['command'] or settings.SUDO:
            command_pass = None
            if 'command_pass' in test:
                command_pass = str(test['command_pass'])
            command_fail = None
            if 'command_fail' in test:
                command_fail = str(test['command_fail'])
            result = _execute_check(command=test['command'],
                                    comparison_type=test['type'],
                                    case_sensitive=test['case_sensitive'],
                                    command_pass=command_pass,
                                    command_fail=command_fail)
            if result == CheckResult.explicit_pass:
                write_str("Test passed exlicitly for '%s'" % test['command'],
                          debug=True)
                break
            elif result == CheckResult.explicit_fail:
                write_str("Test failed exlicitly for '%s'" % test['command'],
                          debug=True)
                break
            elif result == CheckResult.no_pass:
                write_str("Test did not pass for '%s'" % test['command'],
                          debug=True)
                continue
            else:
                raise ValueError("Invalid return value from _execute_check.")

    if result == CheckResult.explicit_pass or not quiet_fail:
        write_str("\nCHECK #%d: %s... %s" % (tallies.check_num,
                                             config_check.description,
                                             check_result_to_str(result)))

    if (result not in (CheckResult.explicit_pass, CheckResult.all_skipped) and
            last_attempt and do_warn(config_check)):
        warn("Attempted fix %s" % settings.FAILED_STR)

    return result

def log_to_file(string):
    """Append string, followed by newline character, to log file.

    Color codes will be stripped out of the string non-destructively before
    writing.
    """
    string = re.sub(r"\033\[\d{1,2}m", "", string)
    log_file_loc = settings.LOG_FILE_LOC
    if log_file_loc.startswith('~'):
        log_file_loc = expanduser(log_file_loc)
    with open(log_file_loc, 'a+') as log_file:
        log_file.write("%s\n" % string)

def _execute_check(command, comparison_type, case_sensitive, command_pass=None,
                   command_fail=None):
    """Helper function for `run_check` -- executes command and checks result.

    This check can result in three conditions:
    1. The check explicitly passed, and no subsequent tests need to be performed
        for this check. Returns True.
    2. The check explicitly failed, and no subsequent tests need to be performed
        for this check. Raises ConfigCheckFailedExplicitly.
    3. The check produced another result, and if there is another test
        available, it

    Args:
        command (str): The command to execute to perform the check.
        comparison_type (str): 'exact match' or 'regex match'
        case_sensitive (bool): Whether the comparison to output is case
            sensitive.
        command_pass (str or None): The output of the command which constitutes
            an explicit pass for the test, either as an exact string or regex
            depending on `comparison_type`.
        command_fail (str or None): The output of the command which constitutes
            an explicit fail for the test, either as an exact string or regex
            depending on `comparison_type`.

    Returns:
       `CheckResult`: explicit pass, explicit failure, or lacking of passing for
            this test only.

    Raises:
        ValueError if `comparison_type` is not an expected value
    """
    #http://stackoverflow.com/questions/7129107/python-how-to-suppress-the-output-of-os-system
    command = "source %s ; %s" % (settings.API_FILENAME, command)
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    stdout, _ = process.communicate()

    stdout = stdout.strip().decode(encoding='UTF-8')

    write_str("Command executed to check config: '%s'" % str(command),
              debug=True)
    write_str("Result of command: '%s'" % str(stdout), debug=True)
    write_str("Explicit pass condition for command: '%s'" % str(command_pass),
              debug=True)
    write_str("Explicit fail condition for command: '%s'" % str(command_fail),
              debug=True)

    if comparison_type == 'exact match':
        if case_sensitive:
            if command_fail is not None and stdout == command_fail:
                return CheckResult.explicit_fail
            if command_pass is not None and stdout == command_pass:
                return CheckResult.explicit_pass
            else:
                return CheckResult.no_pass
        else:
            if (command_fail is not None and
                    stdout.lower() == str(command_fail.lower())):
                return CheckResult.explicit_fail
            if (command_pass is not None and
                    stdout.lower() == str(command_pass).lower()):
                return CheckResult.explicit_pass
            else:
                return CheckResult.no_pass
    elif comparison_type == 'regex match':
        ignore_case = not case_sensitive
        if (command_fail is not None and
                is_match(command_fail, stdout, ignore_case=ignore_case)):
            return CheckResult.explicit_fail
        if (command_pass is not None and
                is_match(command_pass, stdout, ignore_case=ignore_case)):
            return CheckResult.explicit_pass
        else:
            return CheckResult.no_pass
    else:
        raise ValueError

def do_warn(config_check):
    """Determines whether the config failure merits warning."""
    if config_check.confidence == Confidence.required:
        return True
    if (config_check.confidence == Confidence.recommended and
            settings.WARN_FOR_RECOMMENDED):
        return True
    if (config_check.confidence == Confidence.experimental and
            settings.WARN_FOR_EXPERIMENTAL):
        return True
    return False

def run_quick_command(command):
    """Runs a quick shell command and returns stdout."""
    command = "source %s ; %s" % (settings.API_FILENAME, command)
    process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    stdoutdata, stderrdata = process.communicate()

    write_str("Quick command executed: '%s'" % str(command), debug=True)
    write_str("Command STDOUT: '%s'" % str(stdoutdata), debug=True)
    write_str("Command STDERR: '%s'" % str(stderrdata), debug=True)

    return stdoutdata

def _try_fix(tallies, config_check, use_sudo=False):
    """Attempt to fix a misconfiguration.

    Args:
        config_check (`ConfigCheck`): The check to perform.
        use_sudo (bool): Whether to use the sudo version of this command. If
            no sudo version of this command has been specified in the config
            file, this will simply return without executing anything.
    """
    command = config_check.sudo_fix if use_sudo else config_check.fix
    if use_sudo:
        write_str(("\tAttempting configuration fix with elevated privileges; %s"
                   "you may be prompted for your OS X login password%s...") %
                  (settings.COLORS['BOLD'], settings.COLORS['ENDC']))
    stdoutdata = ""
    stderrdata = ""
    if command is not None:

        if use_sudo and run_quick_command("is_sudoer").strip() == "0":
            write_str(("User is not in sudoers, and therefore need not attempt "
                       "this fix: '%s'") % command)
            tallies.fix_skipped_no_sudoer += 1
            return

        command = "source %s ; %s" % (settings.API_FILENAME, command)
        process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
        stdoutdata, stderrdata = process.communicate()

        write_str("Command executed: '%s'" % str(command), debug=True)
        write_str("Command STDOUT: '%s'" % str(stdoutdata), debug=True)
        write_str("Command STDERR: '%s'" % str(stderrdata), debug=True)

def do_fix_and_test(tallies, config_check):
    """Attempt to fix misconfiguration, returning the result.

    If a non-sudo fix is specified, this will be attempted first.
    If a non-sudo fix fails or there is none specified and a sudo fix is
    specified, this will be attempted next.
    If all previous attempts have failed or none have been specified and
    instructions for manually fixing the configuration have been specified,
    these will be printed out at the end of execution by another function.

    Args:
        config_check (`ConfigCheck`): The check to perform.

    Returns:
        bool: Whether an attempted fix was successful.
    """
    write_str("Entered do_fix_and_test()", debug=True)

    if config_check.fix is not None:
        _try_fix(tallies, config_check, use_sudo=False)
        check_result = run_check(
            tallies,
            config_check, last_attempt=False, quiet_fail=True)
        if check_result == CheckResult.explicit_pass:
            return True

    if config_check.sudo_fix is not None:
        _try_fix(tallies, config_check, use_sudo=True)
        check_result = run_check(
            tallies,
            config_check, last_attempt=True, quiet_fail=False)
        return bool(check_result == CheckResult.explicit_pass)
    else:
        return False



def underline_hyperlink(string):
    """Insert underlines into hyperlinks"""
    return re.sub(
        r"(https?://[^ ]+)",
        (r"%s\1%s" % (settings.COLORS['UNDERLINE'], settings.COLORS['ENDC'])),
        string,
        flags=re.IGNORECASE)

def bool_to_yes_no(boolean):
    ''' Convert boolean to yes or no '''
    return 'yes' if boolean else 'no'


def write_str(msg, debug=False):
    """Print and logs the specified message unless prohibited by settings.

    Args:
        msg (str): The message to be written.
        debug (bool): Whether the message is normal or debug-only info.
            Default: False
    """
    if debug:
        dprint(msg)
        if ((settings.VERBOSITY > 0 or settings.LOG_DEBUG_ALWAYS) and
                settings.LOG):
            log_to_file("DEBUG: %s" % msg)
    else:
        print("%s" % msg)
        if settings.LOG:
            log_to_file(msg)

def dprint(msg):
    """Print debug statements."""
    if settings.VERBOSITY > 0:
        print("DEBUG: %s" % msg)

def is_match(regex, string, ignore_case=False):
    """Check if regex matches string."""
    regex_flags = re.DOTALL
    if ignore_case:
        regex_flags = re.DOTALL | re.IGNORECASE

    return re.match(regex, string, regex_flags) is not None

def print_banner():
    ''' Print Banner '''
    banner = (("---------------------------------------------------------------"
               "---------------------------\n"
               "%s%sosx-config-check%s %s\n"
               "Download the latest copy of this tool at: "
               "https://github.com/kristovatlas/osx-config-check \n"
               "Report bugs/issues:\n"
               "\t* GitHub: "
               "https://github.com/kristovatlas/osx-config-check/issues \n"
               "\t* Twitter: https://twitter.com/kristovatlas \n"
               "---------------------------------------------------------------"
               "---------------------------\n") %
              (settings.COLORS['BOLD'], settings.COLORS['OKBLUE'],
               settings.COLORS['ENDC'], VERSION))
    write_str(underline_hyperlink(banner))
