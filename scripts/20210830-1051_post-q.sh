#! /bin/bash
#
# round=1のQデータを登録
#


[ -z "${Q_DIR}" ] && Q_DIR="./qa_2021_pre"


adccli --round 1 --alt-user ADC-0 post-user-q 1 ${Q_DIR}/kn_Q111.txt
adccli --round 1 --alt-user ADC-0 post-user-q 2 ${Q_DIR}/kn_Q118.txt
adccli --round 1 --alt-user ADC-0 post-user-q 3 ${Q_DIR}/shimamura_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 4 ${Q_DIR}/test1_20x60_200_100_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 5 ${Q_DIR}/test1_40x40_300_300_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 6 ${Q_DIR}/test1_60x30_200_350_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 7 ${Q_DIR}/test1_60x60_500_800_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 8 ${Q_DIR}/test1_60x60_700_100_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 9 ${Q_DIR}/test1_60x60_750_750_Q.txt
adccli --round 1 --alt-user ADC-0 post-user-q 10 ${Q_DIR}/test1_72x72_1000_1000_Q.txt

adccli --round 1 get-admin-q-all
