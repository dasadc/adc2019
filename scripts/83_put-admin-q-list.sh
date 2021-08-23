#! /bin/bash
#
# test_post-q
#
# 問題データのリストを作成する


adccli timekeeper-state im1  # im1状態へ遷移

# 問題リストを作成する
echo  "put-admin-q-list"
adccli put-admin-q-list
