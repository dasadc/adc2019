#! /bin/bash
#
# 回答データの補足情報を登録する、取得する


adccli --alt-user test-01 put-a-info 1 12.345 2048 hello
adccli --alt-user test-01 put-a-info 2 23.456 4096 world

adccli --alt-user test-01 get-a-info 1
adccli --alt-user test-01 get-a-info 2
