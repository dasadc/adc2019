#! /bin/bash
#
# log


echo  "get-log"
adccli get-log 30


echo  "get-user-log"

echo "user: test-01"
adccli --alt-user test-01 get-user-log 10

echo "user: test-02"
adccli --alt-user test-02 get-user-log 10

echo "user: test-03"
adccli --alt-user test-03 get-user-log 10

echo "user: test-04"
adccli --alt-user test-04 get-user-log 10
