import logging

from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

# SHELL CMD


def shell_cmd(command):
    log.debug('')
    log.debug('Issuing system command: ({})'.format(command))
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output, errors = process.communicate()
    log.debug('Output: ({}), Errors: ({})'.format(output, errors))
    return  str(output).rstrip('\n'), str(errors).rstrip('\n'), process.returncode
