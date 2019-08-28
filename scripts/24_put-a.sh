#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"
echo TOP=$TOP
DATA_DIR=${TOP}/adc2019_QA

i=0

for f in \
1_A.txt \
2_A.txt \
3_A.txt \
4_A.txt \
5_A.txt \
6_A.txt \
7_A.txt \
8_A.txt \
9_A.txt \
10_A.txt \
11_A.txt \
12_A.txt \
13_A.txt \
14_A.txt \
15_A.txt \
16_A.txt \
17_A.txt \
18_A.txt \
19_A.txt \
20_A.txt \
21_A.txt \
22_A.txt \
23_A.txt \
24_A.txt \
25_A.txt \
26_A.txt \
27_A.txt \
28_A.txt \
29_A.txt \
30_A.txt \
31_A.txt
do
    i=$(( $i + 1 ))
    ${TOP}/client/adccli put-a ${i} ${DATA_DIR}/${f}
done
