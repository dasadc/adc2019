#! /bin/bash
#
#
# Qup

adccli test-mode false
sleep 5
adccli view-score-mode false
sleep 5
adccli log-to-datastore false
sleep 5

adccli timekeeper-state Qup
