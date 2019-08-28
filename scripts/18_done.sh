#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"


${TOP}/client/adccli timekeeper-state im1

${TOP}/client/adccli put-admin-q-list
