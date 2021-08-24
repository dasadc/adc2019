#! /bin/bash
#
#
# 問題データが登録されているか、チェックする


# 全問題のリスト(すべてのユーザー、すべての問題番号)
echo  "get-admin-q-all"
adccli get-admin-q-all

echo "get-q"

adccli get-q
adccli get-q 1
adccli get-q 2
adccli get-q 3

echo "user: test-01"
adccli --alt-user test-01 get-q

echo "user: test-02"
adccli --alt-user test-02 get-q

echo "user: test-03"
adccli --alt-user test-03 get-q

echo "user: test-04"
adccli --alt-user test-04 get-q
