#! /bin/bash
#
# いろいろな初期化処理
#
# 変更しない情報
# - ユーザーアカウント情報
# - roundカウンタ
#
# 変更する情報
# - 状態変数やモードなどを初期化
# - 問題データ、問題リスト、回答データ、すべて削除


# roundカウンタ値は、ここでは変更しない。事前に設定しておく。
# adccli timekeeper-round round 999 # roundカウンタ値の設定
adccli timekeeper-round  # roundカウンタ値の確認

# 状態変数を初期化
adccli timekeeper-state init  # init状態へ遷移
adccli timekeeper-enabled 0   # timekeeper無効


# モード設定
adccli test-mode True
adccli view-score-mode True
adccli log-to-datastore False

adccli timekeeper-state im0  # im0状態へ遷移

# 出題番号を消去する
adccli delete-admin-q-list

# 問題データをすべて消去する
adccli delete-admin-q-all

# 回答データをすべて消去する
adccli delete-admin-a-all

echo "sleep 5"
sleep 5

# データの一覧リストを出力して、データが消去済みであることを確認する
echo  "get-admin-q-all"
adccli get-admin-q-all

echo  "get-admin-a-all"
adccli get-admin-a-all

echo ""
adccli get-user-list
