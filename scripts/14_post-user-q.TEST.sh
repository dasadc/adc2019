#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TOP="$( cd ${DIR}/../ >/dev/null 2>&1 && pwd )"
#echo TOP=$TOP
DATA_DIR=${TOP}/sample_hiromoto_1-12_mod

#adc2019_QA

i=0
for f in \
sample_hiromoto_1_Q.txt \
sample_hiromoto_2_Q.txt \
sample_hiromoto_3_Q.txt \
sample_hiromoto_4_Q.txt \
sample_hiromoto_5_Q.txt \
sample_hiromoto_6_Q.txt \
sample_hiromoto_7_Q.txt \
sample_hiromoto_8_Q.txt \
sample_hiromoto_9_Q.txt \
sample_hiromoto_10_Q.txt \
sample_hiromoto_11_Q.txt \
sample_hiromoto_12_Q.txt
do
    i=$(( $i + 1 ))
    ${TOP}/client/adccli post-user-q ${i} ${DATA_DIR}/${f}
done


i=0
for f in \
sample_hiromoto_1_Q.txt \
sample_hiromoto_2_Q.txt \
sample_hiromoto_3_Q.txt
do
    i=$(( $i + 1 ))
    ${TOP}/client/adccli --alt-user test-01 post-user-q ${i} ${DATA_DIR}/${f}
    ${TOP}/client/adccli --alt-user test-02 post-user-q ${i} ${DATA_DIR}/${f}
    ${TOP}/client/adccli --alt-user test-03 post-user-q ${i} ${DATA_DIR}/${f}
    ${TOP}/client/adccli --alt-user test-04 post-user-q ${i} ${DATA_DIR}/${f}
done
