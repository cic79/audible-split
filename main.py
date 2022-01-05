#!/usr/bin/env python3

import datetime
import json
import os
import subprocess

import srt
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

AUDIO_FILE = '/home/fconte/Downloads/audible/James S.A. Corey - The Expanse 2 - Caliban. La guerra.mp3'
MODEL = 'models/vosk-model-small-it'
SAMPLE_RATE = 16000
WORDS_PER_LINE = 7


def transcribe():
    results = []
    subs = []
    model = Model(MODEL)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)
    while True:
        data = process.stdout.read(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(rec.Result())
    results.append(rec.FinalResult())

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
    return subs


if not os.path.exists(MODEL):
    print('Please download the model from https://alphacephei.com/vosk/models and unpack as in the MODEL folder.')
    exit(1)

wav_file = '%s.wav' % AUDIO_FILE.rsplit('.', 1)[0]
result = subprocess.run(['ffmpeg', '-i', AUDIO_FILE, '-ar', str(SAMPLE_RATE), '-ac', '1', wav_file])
if result.returncode is not 0:
    print(result)
    exit(result.returncode)
print('WAV READY...')

process = subprocess.Popen(
    ['ffmpeg', '-loglevel', 'quiet', '-i', wav_file, '-ar', str(SAMPLE_RATE), '-ac', '1', '-f', 's16le', '-'],
    stdout=subprocess.PIPE)
print('WAV OPENED...')

print(srt.compose(transcribe()))

print('COMPLETED!')
