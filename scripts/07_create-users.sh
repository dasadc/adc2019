#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"
echo TOP=$TOP

${TOP}/client/adccli create-users ${TOP}/server/adcusers_in.py
