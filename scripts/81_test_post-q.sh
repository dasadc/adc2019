#! /bin/bash
#
# test_post-q
#
# 動作確認用の問題データを登録する


script=$(readlink -f "$0")
top_dir=$(cd $(dirname "$script")/../; pwd)
Q_dir="${top_dir}/samples/Q/"

adccli timekeeper-state Qup  # Qup状態へ遷移

adccli post-user-q 1 ${Q_dir}/sample_1_Q.txt
adccli post-user-q 2 ${Q_dir}/sample_2_Q.txt
adccli post-user-q 3 ${Q_dir}/sample_3_Q.txt
adccli post-user-q 4 ${Q_dir}/sample_1_Q.txt
adccli post-user-q 5 ${Q_dir}/sample_2_Q.txt
adccli post-user-q 6 ${Q_dir}/sample_3_Q.txt
adccli post-user-q 7 ${Q_dir}/sample_1_Q.txt
adccli post-user-q 8 ${Q_dir}/sample_2_Q.txt
adccli post-user-q 9 ${Q_dir}/sample_3_Q.txt
adccli post-user-q 10 ${Q_dir}/sample_1_Q.txt
adccli post-user-q 11 ${Q_dir}/sample_2_Q.txt
adccli post-user-q 12 ${Q_dir}/sample_3_Q.txt

adccli --alt-user test-01 post-user-q 1 ${Q_dir}/sample_1_Q.txt
adccli --alt-user test-01 post-user-q 2 ${Q_dir}/sample_2_Q.txt
adccli --alt-user test-01 post-user-q 3 ${Q_dir}/sample_3_Q.txt

adccli --alt-user test-02 post-user-q 1 ${Q_dir}/sample_1_Q.txt
adccli --alt-user test-02 post-user-q 2 ${Q_dir}/sample_2_Q.txt
adccli --alt-user test-02 post-user-q 3 ${Q_dir}/sample_3_Q.txt

adccli --alt-user test-03 post-user-q 1 ${Q_dir}/sample_1_Q.txt
adccli --alt-user test-03 post-user-q 2 ${Q_dir}/sample_2_Q.txt
adccli --alt-user test-03 post-user-q 3 ${Q_dir}/sample_3_Q.txt

adccli --alt-user test-04 post-user-q 1 ${Q_dir}/sample_1_Q.txt
adccli --alt-user test-04 post-user-q 2 ${Q_dir}/sample_2_Q.txt
adccli --alt-user test-04 post-user-q 3 ${Q_dir}/sample_3_Q.txt

# 全問題のリスト(すべてのユーザー、すべての問題番号)
echo "get-admin-q-all"
adccli get-admin-q-all
