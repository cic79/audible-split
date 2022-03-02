#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import os
import sys

import srt
from tqdm import tqdm
from vosk import Model, KaldiRecognizer, SetLogLevel

from utils import compute_file, exec_cmd, is_tool, get_secs, get_elapsed_secs, num_to_str, contains_word, \
    get_cue_time

AUDIO_FILE = '/home/fconte/Downloads/audible/James S.A. Corey - The Expanse 5 - Nemesis Games. L\'esodo.mp3'
base_name_with_path = AUDIO_FILE.rsplit('.', 1)[0]
PERFORMER, TITLE = os.path.basename(base_name_with_path).split(' - ', 1)
WAV_FILE = f'{base_name_with_path}.wav'
OUTPUT_FILE = f'{base_name_with_path}.output'
SRT_FILE = f'{base_name_with_path}.srt'
CUE_FILE = f'{base_name_with_path}.cue'
COVER_FILE = f'{base_name_with_path}.jpg'
OUTPUT_DIR = base_name_with_path
MODEL = 'models/vosk-model-small-it'
SAMPLE_RATE = 16000
WORDS_PER_LINE = 7
VERBOSE = False

# Check existence of paths and programs
if not os.path.exists(MODEL):
    sys.stderr.write(f'ERROR: model path: \'{MODEL}\' doesn\'t exist.\nPlease download the model from '
                     'https://alphacephei.com/vosk/models and unpack as in the MODEL folder.')
    exit(1)
if not os.path.exists(AUDIO_FILE):
    sys.stderr.write(f'ERROR: audio file: \'{AUDIO_FILE}\' doesn\'t exist.')
    exit(1)
if not is_tool('ffmpeg'):
    sys.stderr.write('ERROR: ffmpeg not installed; please run:\nsudo apt install -y ffmpeg')
    exit(1)
if not is_tool('mp3splt'):
    sys.stderr.write('ERROR: mp3splt not installed; please run:\nsudo apt install -y mp3splt')
    exit(1)
compute_audio_file = compute_file(WAV_FILE, 'audio file')
compute_output_file = compute_file(OUTPUT_FILE, 'output file')
compute_srt_file = compute_file(SRT_FILE, 'srt file')
compute_cue_file = compute_file(CUE_FILE, 'cue file')
compute_cover_file = compute_file(COVER_FILE, 'cover file')
if os.path.exists(OUTPUT_DIR):
    sys.stderr.write(f'ERROR: output dir \'{OUTPUT_DIR}\' already exists.')
    exit(1)

# Convert mp3 in wav
if compute_audio_file:
    sys.stdout.write(f'\nGenerating the wav file: \'{WAV_FILE}\'...')
    cmd = f'ffmpeg -y -v error -i "{AUDIO_FILE}" -ar {SAMPLE_RATE} -ac 1 "{WAV_FILE}"'
    exec_cmd(cmd=cmd, verbose=VERBOSE, skip_error=False)
else:
    sys.stdout.write(f'\nReuse the existing file: \'{WAV_FILE}\'...')

# Generate output file with vosk
if compute_output_file:
    sys.stdout.write(f'\nReading \'{WAV_FILE}\' file...\n')
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
    sys.stdout.write(f'\nReuse the existing file: \'{OUTPUT_FILE}\'...')

# Convert output vosk in srt
if compute_srt_file:
    sys.stdout.write(f'\nReading \'{OUTPUT_FILE}\' file...')
    with open(OUTPUT_FILE, 'r') as f:
        results = f.readlines()
    subs = []
    for i, res in enumerate(results):
        jres = json.loads(res)
        if 'result' not in jres:
            continue
        words = jres['result']
        for j in range(0, len(words), WORDS_PER_LINE):
            lines = words[j: j + WORDS_PER_LINE]
            s = srt.Subtitle(index=len(subs), content=' '.join([line['word'] for line in lines]),
                             start=datetime.timedelta(seconds=lines[0]['start']),
                             end=datetime.timedelta(seconds=lines[-1]['end']))
            subs.append(s)
    with open(SRT_FILE, 'w') as f:
        f.write(srt.compose(subs))
    sys.stdout.write(f'\nWrote \'{SRT_FILE}\' file...')
else:
    sys.stdout.write(f'\nReuse the existing file: \'{SRT_FILE}\'...')

# Find chapters
VALUE_KEYWORDS = {
    'prologo': ['prologo'],
    'interludio': ['interludio', 'interlocutorio', 'intermedio', 'intervenuti'],
    'epilogo': ['epilogo']
}
KEYWORDS_REPLACE = {a: k for k, v in VALUE_KEYWORDS.items() for a in v}
KEYWORDS = KEYWORDS_REPLACE.keys()
SILENCE_GAP = 2.5
chapter = 1
chapters = []

sys.stdout.write(f'\nReading \'{SRT_FILE}\' file...')
with open(SRT_FILE, 'r') as f:
    sub_number = f.readline()
    before_sub_to_time = 0.0
    while True:
        sub_from_time_original, sub_to_time = f.readline().split('-->')
        sub_from_time = get_secs(sub_from_time_original)
        sub_to_time = get_secs(sub_to_time)
        sub_text = f.readline().strip().lower()
        empty_line = f.readline()
        sub_number = f.readline()
        elapsed_secs = get_elapsed_secs(before_sub_to_time, sub_from_time)
        if elapsed_secs >= SILENCE_GAP:
            if any(contains_word(sub_text, keyword) for keyword in KEYWORDS):
                for keyword in KEYWORDS:
                    if contains_word(sub_text, keyword):
                        chapters.append((sub_from_time_original, KEYWORDS_REPLACE[keyword].capitalize(), sub_text))
                        break
            elif contains_word(sub_text, num_to_str(chapter)):
                chapters.append((sub_from_time_original, f'Capitolo {chapter}', sub_text))
                chapter += 1
            else:
                # Is it an undetected keyword?
                sys.stdout.write(f'\nDetected the following new keyword: \'{sub_text}\' at {sub_from_time_original}')
        before_sub_to_time = sub_to_time
        if sub_number == '':
            break

# Generate cue file
if compute_cue_file:
    with open(CUE_FILE, 'w') as f:
        track_number = 1
        f.write(f'PERFORMER "{PERFORMER}"\r\n')
        f.write(f'TITLE "{TITLE}"\r\n')
        f.write(f'FILE "{AUDIO_FILE}" MP3\r\n')
        first_chapter_time = chapters[0][0]
        if get_secs(first_chapter_time) > 6:
            f.write(f'  TRACK {track_number:#02} AUDIO\r\n')
            f.write(f'    PERFORMER "{PERFORMER}"\r\n')
            f.write(f'    TITLE "Introduzione"\r\n')
            f.write(f'    INDEX 01 00:00:00\r\n')
            track_number += 1
        for chapter_time, chapter_text, _ in chapters:
            f.write(f'  TRACK {track_number:#02} AUDIO\r\n')
            f.write(f'    PERFORMER "{PERFORMER}"\r\n')
            f.write(f'    TITLE "{chapter_text}"\r\n')
            f.write(f'    INDEX 01 {get_cue_time(chapter_time)}\r\n')
            track_number += 1
    sys.stdout.write(f'\nWrote \'{CUE_FILE}\' file...')
else:
    sys.stdout.write(f'\nReuse the existing file: \'{CUE_FILE}\'...')

# Validate the cue file
sys.stdout.write(f'\nValidating the cue file: \'{CUE_FILE}\'...')
cmd = f'bash cue_validator.sh "{CUE_FILE}"'
result = exec_cmd(cmd=cmd, verbose=VERBOSE, skip_error=False)
if result:
    sys.stderr.write(f'ERROR: cue file \'{CUE_FILE}\' contains some errors:\n{result}')
    exit(1)

# Extract the cover
if compute_cover_file:
    sys.stdout.write('\nExtracting the cover...')
    cmd = f'ffmpeg -y -v error -i "{AUDIO_FILE}" "{COVER_FILE}"'
    exec_cmd(cmd=cmd, verbose=VERBOSE, skip_error=False)
else:
    sys.stdout.write(f'\nReuse the existing file: \'{COVER_FILE}\'...')

# Split the mp3
sys.stdout.write('\nSplitting the mp3...')
cmd = f'mp3splt -f -q -o @n+-+@t -d "{OUTPUT_DIR}" -c "{CUE_FILE}" "{AUDIO_FILE}"'
exec_cmd(cmd=cmd, verbose=VERBOSE, skip_error=False)

# Add the cover to the splitted files
sys.stdout.write('\nAdding the cover to the splitted files...')
for file in os.listdir(os.fsencode(OUTPUT_DIR)):
    filename = os.fsdecode(file)
    if filename.endswith('.mp3'):
        cmd = f'mv -f "{OUTPUT_DIR}/{filename}" /tmp/audio.mp3'
        exec_cmd(cmd=cmd, verbose=VERBOSE, skip_error=False)
        cmd = f'ffmpeg -v error -i "/tmp/audio.mp3" -i "{COVER_FILE}" -map 0:0 -map 1:0 -c copy -id3v2_version 3 ' \
              f'-metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" "{OUTPUT_DIR}/{filename}"'
        exec_cmd(cmd=cmd, verbose=VERBOSE, skip_error=False)

sys.stdout.write('\nEnjoy your new splitted book!')
