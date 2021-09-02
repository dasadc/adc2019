#! /bin/bash
#
#
# Round1終了、Round2へ移行


adccli timekeeper-state im2
sleep 5
adccli score-dump |& tee score-dump-20210930.txt
sleep 5
adccli timekeeper-round 2
sleep 5
adccli timekeeper-state im0

adccli test-mode false
adccli view-score-mode false
adccli log-to-datastore false
