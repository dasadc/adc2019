#! /bin/bash
#
# 回答データの補足情報を登録する、取得する


adccli put-a-info 1 12.345 2048 hello
adccli put-a-info 2 23.456 4096 world

adccli get-a-info 1
adccli get-a-info 2
