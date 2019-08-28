#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"
echo TOP=$TOP
DATA_DIR=${TOP}/adc2019_QA

i=0

for f in \
1_Q.txt \
2_Q.txt \
3_Q.txt \
4_Q.txt \
5_Q.txt \
6_Q.txt \
7_Q.txt \
8_Q.txt \
9_Q.txt \
10_Q.txt \
11_Q.txt \
12_Q.txt \
13_Q.txt \
14_Q.txt \
15_Q.txt \
16_Q.txt \
17_Q.txt \
18_Q.txt \
19_Q.txt \
20_Q.txt \
21_Q.txt \
22_Q.txt \
23_Q.txt \
24_Q.txt \
25_Q.txt \
26_Q.txt \
27_Q.txt \
28_Q.txt \
29_Q.txt \
30_Q.txt \
31_Q.txt
do
    i=$(( $i + 1 ))
    ${TOP}/client/adccli post-user-q ${i} ${DATA_DIR}/${f}
done
