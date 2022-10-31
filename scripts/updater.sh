#!/bin/bash

# eg: SCRIPT_DIR=/home/myhome/workspace/PROJECT/scripts
SCRIPT_DIR="$(cd "$( dirname "$(readlink -f "${BASH_SOURCE[0]}" )")" && pwd)"
# eg: REQUIREMENTS_DIR=/home/myhome/workspace/PROJECT
REQUIREMENTS_DIR="$(dirname "$SCRIPT_DIR")"
CURRENT_DIR="$(pwd)"

if ! pur --help > /dev/null;
then
  # command not found
  pip install pur
fi

if ! pip-sync --help > /dev/null;
then
  # command not found
  pip install pip-tools
fi

cd "${REQUIREMENTS_DIR}"

# uncomment pur and pip-tools requirements
sed -i '/pur=/s/^# //g' requirements.txt
sed -i '/pip-tools/s/^# //g' requirements.txt

PUR_COMMAND="$(sed '/pur/s/^# //g' requirements.txt | sed -n '2p')"
$PUR_COMMAND

pip-sync

# comment pur and pip-tools requirements
sed -i '/pur=/s/^/# /g' requirements.txt
sed -i '/pip-tools/s/^/# /g' requirements.txt

cd "$CURRENT_DIR"
