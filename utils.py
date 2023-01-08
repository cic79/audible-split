#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
import sys
import time
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


def get_secs(time_str):
    # Converte la stringa HH:MM:SS,SSS in secondi
    h, m, s = time_str.strip().split(':')
    return int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))


def get_elapsed_secs(from_time, to_time):
    # Ritorna i secondi che intercorrono tra i due tempi.
    # Il risultato viene convertito nell'intero più vicino.
    return round(to_time - from_time)


def get_cue_time(time_str):
    # Converte la stringa HH:MM:SS,SSS in formato CUE MM:SS:FF
    # FF sono i frame e ci sono 75 frame per secondo.
    h, m, s = time_str.strip().split(':')
    s, ms = s.split(',')
    return f'{int(h)*60+int(m):#02}:{int(s):#02}:{int(0.075*int(ms)):#02}'


def num_to_str(number):
    # Trasforma un numero in stringa o lista di stringhe; eg: 1 -> uno
    from num2words import num2words
    if number == 1:
        return [num2words(number, lang='it'), 'una']
    if number == 21:
        return [num2words(number, lang='it'), 'ventuno']
    if number == 29:
        return [num2words(number, lang='it'), 'venti love']
    return num2words(number, lang='it')


def contains_word(text, word):
    # Ritorna True se word è contenuta in text
    # word può essere una stringa o una lista di stringhe
    words = word
    if not isinstance(word, list):
        words = [word]
    return any(f' {word} ' in f' {text} ' for word in words)


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


def compute_file(file, label):
    file_exists = os.path.exists(file)
    overwrite_file = False
    if file_exists:
        sys.stdout.write(f'{label.capitalize()} \'{file}\' already exists.\n')
        reuse_file = query_yes_no('Do you wanna continue and reuse the existing file?')
        if not reuse_file:
            overwrite_file = query_yes_no('Do you wanna continue and overwrite the existing file?')
            if not overwrite_file:
                sys.stderr.write(f'ERROR: {label.lower()} \'{file}\' already exists.')
                exit(1)
    return not file_exists or overwrite_file


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
