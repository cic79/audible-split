#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import os
import sys

import srt
from tqdm import tqdm
from vosk import Model, KaldiRecognizer, SetLogLevel

from utils import exec_cmd, is_tool, query_yes_no

AUDIO_FILE = '/home/fconte/Downloads/audible/James S.A. Corey - The Expanse 2 - Caliban. La guerra.mp3'
WAV_FILE = '%s.wav' % AUDIO_FILE.rsplit('.', 1)[0]
OUTPUT_FILE = '%s.output' % AUDIO_FILE.rsplit('.', 1)[0]
SRT_FILE = '%s.srt' % AUDIO_FILE.rsplit('.', 1)[0]
MODEL = 'models/vosk-model-small-it'
SAMPLE_RATE = 16000
WORDS_PER_LINE = 7


# Check existence of paths and programs
if not os.path.exists(MODEL):
    sys.stderr.write('ERROR: model path: \'%s\' doesn\'t exist.\nPlease download the model from '
                     'https://alphacephei.com/vosk/models and unpack as in the MODEL folder.' % MODEL)
    exit(1)
if not os.path.exists(AUDIO_FILE):
    sys.stderr.write('ERROR: audio file: \'%s\' doesn\'t exist.' % AUDIO_FILE)
    exit(1)
if not is_tool('ffmpeg'):
    sys.stderr.write('ERROR: ffmpeg not installed; please run:\nsudo apt install -y ffmpeg')
    exit(1)
audio_file_exists = os.path.exists(WAV_FILE)
overwrite_audio_file = False
if audio_file_exists:
    sys.stdout.write('Audio file \'%s\' already exists.\n' % WAV_FILE)
    reuse_file = query_yes_no('Do you wanna continue and reuse the existing file?')
    if not reuse_file:
        overwrite_audio_file = query_yes_no('Do you wanna continue and overwrite the existing file?')
        if not overwrite_audio_file:
            sys.stderr.write('ERROR: audio file \'%s\' already exists.' % WAV_FILE)
            exit(1)
output_file_exists = os.path.exists(OUTPUT_FILE)
overwrite_output_file = False
if output_file_exists:
    sys.stdout.write('Output file \'%s\' already exists.\n' % OUTPUT_FILE)
    reuse_file = query_yes_no('Do you wanna continue and reuse the existing file?')
    if not reuse_file:
        overwrite_output_file = query_yes_no('Do you wanna continue and overwrite the existing file?')
        if not overwrite_output_file:
            sys.stderr.write('ERROR: output file \'%s\' already exists.' % OUTPUT_FILE)
            exit(1)
srt_file_exists = os.path.exists(SRT_FILE)
overwrite_srt_file = False
if srt_file_exists:
    sys.stdout.write('Srt file \'%s\' already exists.\n' % SRT_FILE)
    reuse_file = query_yes_no('Do you wanna continue and reuse the existing file?')
    if not reuse_file:
        overwrite_srt_file = query_yes_no('Do you wanna continue and overwrite the existing file?')
        if not overwrite_srt_file:
            sys.stderr.write('ERROR: srt file \'%s\' already exists.' % SRT_FILE)
            exit(1)

if not audio_file_exists or overwrite_audio_file:
    cmd = 'ffmpeg -y -i "%s" -ar %s -ac 1 "%s"' % (AUDIO_FILE, SAMPLE_RATE, WAV_FILE)
    result = exec_cmd(cmd=cmd, verbose=True, skip_error=False)
else:
    sys.stdout.write('Reuse the existing file: \'%s\'...' % WAV_FILE)

if not output_file_exists or overwrite_output_file:
    sys.stdout.write('\nReading \'%s\' file...\n' % WAV_FILE)
    with open(OUTPUT_FILE, 'w') as output:
        SetLogLevel(-1)
        model = Model(MODEL)
        rec = KaldiRecognizer(model, SAMPLE_RATE)
        rec.SetWords(True)
        with tqdm(total=os.path.getsize(WAV_FILE)) as progress_bar:
            with open(WAV_FILE, 'br') as f:
                while True:
                    data = f.read(4000)
                    progress_bar.update(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        output.write(rec.Result().replace('\n', '') + '\n')
        output.write(rec.FinalResult().replace('\n', ''))
else:
    sys.stdout.write('Reuse the existing file: \'%s\'...' % OUTPUT_FILE)

sys.stdout.write('\nReading \'%s\' file...\n' % OUTPUT_FILE)
with open(OUTPUT_FILE, 'r') as f:
    results = f.readlines()
subs = []
for i, res in enumerate(results):
    jres = json.loads(res)
    if 'result' not in jres:
        continue
    words = jres['result']
    for j in range(0, len(words), WORDS_PER_LINE):
        line = words[j: j + WORDS_PER_LINE]
        s = srt.Subtitle(index=len(subs),
                         content=' '.join([l['word'] for l in line]),
                         start=datetime.timedelta(seconds=line[0]['start']),
                         end=datetime.timedelta(seconds=line[-1]['end']))
        subs.append(s)

with open(SRT_FILE, 'w') as f:
    f.write(srt.compose(subs))
sys.stdout.write('\nWrote \'%s\' file...\n' % SRT_FILE)
