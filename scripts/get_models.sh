#!/bin/bash

# eg: SCRIPT_DIR=/home/myhome/workspace/PROJECT/scripts
SCRIPT_DIR="$(cd "$( dirname "$(readlink -f "${BASH_SOURCE[0]}" )")" && pwd)"
# eg: REQUIREMENTS_DIR=/home/myhome/workspace/PROJECT
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_DIR="$(pwd)"

VOSK_EN=vosk-model-small-en-us
VOSK_IT=vosk-model-small-it
VOSK_EN_VER="${VOSK_EN}-0.15"
VOSK_IT_VER="${VOSK_IT}-0.22"

cd "$ROOT_DIR/models"

rm -rf *

wget "https://alphacephei.com/vosk/models/${VOSK_EN_VER}.zip"
unzip "${VOSK_EN_VER}"

wget "https://alphacephei.com/vosk/models/${VOSK_IT_VER}.zip"
unzip "${VOSK_IT_VER}"

mv "${VOSK_EN_VER}" "${VOSK_EN}"
mv "${VOSK_IT_VER}" "${VOSK_IT}"

rm "${VOSK_EN_VER}.zip" "${VOSK_IT_VER}.zip"

cd "$CURRENT_DIR"
