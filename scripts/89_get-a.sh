#! /bin/bash
#
# 回答データ


# ユーザーごとの全回答のリスト
echo  "get-a"
adccli get-a

echo "user: test-01"
adccli --alt-user test-01 get-a

echo "user: test-02"
adccli --alt-user test-02 get-a

echo "user: test-03"
adccli --alt-user test-03 get-a

echo "user: test-04"
adccli --alt-user test-04 get-a
