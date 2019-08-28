#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"

${TOP}/client/adccli test-mode False
${TOP}/client/adccli timekeeper 0 im0

${TOP}/client/adccli delete-admin-q-list
${TOP}/client/adccli delete-admin-q-all
${TOP}/client/adccli delete-admin-a-all

${TOP}/client/adccli timekeeper-state Qup
