#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"



echo Except test_mode  False
${TOP}/client/adccli test-mode


echo Expect enabled is 0,  state is Qup
${TOP}/client/adccli timekeeper


echo Expect 0
${TOP}/client/adccli get-admin-q-all

echo Expect 0
${TOP}/client/adccli get-admin-a-all

echo Expect Not found.
${TOP}/client/adccli get-admin-q-list
