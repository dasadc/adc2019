#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"
echo TOP=$TOP

${TOP}/client/adccli --URL='http://127.0.0.1:8888/' --username='administrator' --password='XYZ!123456789o' login
