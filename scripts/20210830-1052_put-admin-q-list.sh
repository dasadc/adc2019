#! /bin/bash
#
# round=1の出題リストを作成
#


echo  "put-admin-q-list"
adccli --round 1 put-admin-q-list


# 全問題のリスト(すべてのユーザー、すべての問題番号)
echo  "get-admin-q-list"
adccli --round 1 get-admin-q-list |& tee 20210830-1052_Q-list.txt
