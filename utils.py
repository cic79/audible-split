#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import time
import shlex
from shutil import which


def str_time(secs):
    # Ritorna una stringa formattata.
    if secs > 1:
        if secs > 60:
            mins = secs // 60
            secs %= 60
            if mins > 60:
                hours = mins // 60
                mins %= 60
                if hours > 24:
                    days = hours // 24
                    hours %= 24
                    return '%s days %s hours' % (int(days), int(hours))
                else:
                    return '%s hours %s mins' % (int(hours), int(mins))
            else:
                return '%s mins %s secs' % (int(mins), int(secs))
        else:
            return '%s secs' % int(secs)
    else:
        return '%s millisecs' % int(secs * 1000.0)


def str_elapsed_time(start):
    # Ritorna una stringa che contiene quanto tempo è passato da start.
    secs = time.time() - start
    return str_time(secs)


def is_tool(name):
    # Controlla se esiste il programma name
    return which(name) is not None


def query_yes_no(question, default='yes'):
    """
    Ask a yes/no question via raw_input() and return their answer.
    'question' is a string that is presented to the user.
    'default' is the presumed answer if the user just hits <Enter>.
            It must be 'yes' (the default), 'no' or None (meaning
            an answer is required of the user).
    The 'answer' return value is True for 'yes' or False for 'no'.
    """
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('invalid default answer: \'%s\'' % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write('Please respond with \'yes\' or \'no\' (or \'y\' or \'n\').\n')


def exec_cmd(cmd, verbose=True, skip_error=False):
    # Esegue il comando cmd
    start = time.time()
    if verbose:
        sys.stdout.write('\nRunning command: %s ...' % cmd)
    try:
        output = subprocess.check_output(shlex.split(cmd)).decode('utf-8')
    except subprocess.CalledProcessError as e:
        if skip_error:
            return False
        raise e
    if verbose:
        sys.stdout.write('\nOutput command: %s\n%s' % (cmd, output))
        sys.stdout.write('\nExecution time: %s\n' % str_elapsed_time(start))
    return output


def get_cmd_output(cmd):
    sys.stdout.write('\nRunning command: %s ...' % cmd)
    return subprocess.Popen(shlex.split(cmd, posix=False), stdout=subprocess.PIPE)
