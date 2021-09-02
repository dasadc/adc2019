#! /bin/bash
#
#
# 1. state im1
# 2. put-admin-q-list

adccli timekeeper-state im1
sleep 5
adccli put-admin-q-list
sleep 5
adccli get-admin-q-list |& tee 20210902-1310_Q-list.txt
sleep 5
adccli dump-data dump-20210902_1310.pickle
