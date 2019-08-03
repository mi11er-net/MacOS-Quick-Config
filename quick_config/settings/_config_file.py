''' function that support reading the config file '''

import json
import hjson
import yaml
import click
#from .. import APP_NAME

def find_config_file(app_name):
    click.get_app_dir(app_name)

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
