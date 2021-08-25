#! /bin/bash
#
# test_put-a
#
# 回答データを登録する


script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
A_dir="${top_dir}/samples/A"


# 81_test_post-q.shにて、問題Qが3種類だけなので、全部同じ回答Aをputすれば、確率33.333%で正解するはず

#adccli put-a 1 ${A_dir}/sample_1_A.txt replace-A-number
#adccli put-a 2 ${A_dir}/sample_1_A.txt replace-A-number
#adccli put-a 3 ${A_dir}/sample_1_A.txt replace-A-number
#adccli put-a 4 ${A_dir}/sample_1_A.txt replace-A-number
#adccli put-a 5 ${A_dir}/sample_1_A.txt replace-A-number



# test-01  すべてA1をput
a=1
while [ $a -le 24 ]; do
    adccli --alt-user test-01 put-a ${a} ${A_dir}/sample_1_A.txt replace-A-number
    a=$((a+1))
done


# test-02  すべてA2をput
a=1
while [ $a -le 24 ]; do
    adccli --alt-user test-02 put-a ${a} ${A_dir}/sample_2_A.txt replace-A-number
    a=$((a+1))
done


# test-03  すべてA3をput
a=1
while [ $a -le 24 ]; do
    adccli --alt-user test-03 put-a ${a} ${A_dir}/sample_3_A.txt replace-A-number
    a=$((a+1))
done


# test-04  すべてA3をput
a=1
while [ $a -le 24 ]; do
    adccli --alt-user test-04 put-a ${a} ${A_dir}/sample_3_A.txt replace-A-number
    a=$((a+1))
done



# 全問題のリスト(すべてのユーザー、すべての問題番号)
echo  "get-admin-a-all"
adccli get-admin-a-all
