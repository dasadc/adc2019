#! /bin/bash
#
#
# 問題データが登録されているか、チェックする



echo  "get-user-q"

echo "user: ADC-0"
adccli --alt-user ADC-0 get-user-q

echo "user: test-02"
adccli --alt-user test-02 get-user-q

echo "user: test-03"
adccli --alt-user test-03 get-user-q

echo "user: test-04"
adccli --alt-user test-04 get-user-q

echo "user: test-04, get-user-q"
adccli --alt-user test-04 get-user-q 1
adccli --alt-user test-04 get-user-q 2
adccli --alt-user test-04 get-user-q 3
