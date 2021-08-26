#! /bin/bash
#
#
# 問題データが登録されているか、チェックする


script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
Q_dir="${top_dir}/samples/Q/"


# 全問題のリスト(すべてのユーザー、すべての問題番号)
echo  "get-admin-q-all"
adccli get-admin-q-all

echo  "get-user-q"

echo "user: ADC-0"
adccli --alt-user ADC-0 get-user-q

echo "user: test-01"
adccli --alt-user test-01 get-user-q

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

diff -u ${Q_dir}/sample_1_Q.txt Q1.test-04.txt
diff -u ${Q_dir}/sample_2_Q.txt Q2.test-04.txt
diff -u ${Q_dir}/sample_3_Q.txt Q3.test-04.txt
