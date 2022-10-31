#!/bin/bash

# eg: SCRIPT_DIR=/home/myhome/workspace/PROJECT/scripts
SCRIPT_DIR="$(cd "$( dirname "$(readlink -f "${BASH_SOURCE[0]}" )")" && pwd)"
# eg: REQUIREMENTS_DIR=/home/myhome/workspace/PROJECT
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_DIR="$(pwd)"

EN_VER=0.15
IT_VER=0.22

cd "$ROOT_DIR/models"
wget "https://alphacephei.com/vosk/models/vosk-model-small-en-us-${EN_VER}.zip"
wget "https://alphacephei.com/vosk/models/vosk-model-small-it-${IT_VER}.zip"
tar zxvf vosk-model*.zip

cd "$CURRENT_DIR"
