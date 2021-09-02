#! /bin/bash
#
# round=2のQデータを登録
#


[ -z "${Q_DIR}" ] && Q_DIR="./qa_2021"

qnum=1

for i in \
hiromoto_1_Q.txt \
hiromoto_2_Q.txt \
hiromoto_3_Q.txt \
hiromoto_4_Q.txt \
hiromoto_5_Q.txt \
hiromoto_6_Q.txt \
kn_Q114.txt \
ss_1_Q.txt \
ss_2_Q.txt \
taki1_Q.txt \
taki2_Q.txt \
taki3_Q.txt \
test1_10x60_100_100_Q.txt \
test1_10x60_100_50_Q.txt \
test1_20x60_200_200_Q.txt \
test1_22x22_100_100_Q.txt \
test1_25x25_100_100_Q.txt \
test1_25x25_70_100_Q.txt \
test1_40x40_200_300_Q.txt \
test1_60x30_200_100_Q.txt
do
    #echo ${Q_DIR}/${i}
    adccli --round 2 --alt-user ADC-0 post-user-q ${qnum} ${Q_DIR}/${i}
    qnum=$(( $qnum + 1 ))
done

adccli --round 2 get-admin-q-all
