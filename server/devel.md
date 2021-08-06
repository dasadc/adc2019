adc2019 API server for ADC2021
==============================

**(注意)** このドキュメントは、まだ、アルゴリズムデザインコンテスト2021年向けの更新漏れがあり、古い情報が書かれている可能性がある。

「API server」とは、アルゴリズムデザインコンテストの自動運営システムにおいて、バックエンドで実行されるREST API serverのことである。
[ウェブアプリ(client-app)](../client-app/README.md)と、コマンラインツール[adcclient](../client/README.md)は、このAPI serverにアクセスして、さまざまな機能を実行している。

以下で説明する手順をスキップして、[Dockerコンテナでかんたんに動かすこともできる](../docker/README.md)。


開発・実行のための環境構築
--------------------------

conda-forgeの「Miniforge」の利用を推奨する。[>> How?](../devel.md#miniforge)


API server 設定ファイル`adcconfig.py`
-------------------------------------

`adcconfig.py`は、API server起動時に読み込まれる設定ファイルである。

1. `YEAR`を、今年の西暦年(e.g. 2021)にする。この値は、[ウェブアプリ(client-app)](../client-app/README.md)での画面表示にも反映される
2. `SECRET_KEY`を、設定する。これは他者には秘密にする情報である
3. `SALT`を、設定する。これも秘密にする情報である
4. `TEST_MODE`と`VIEW_SCORE_MODE`は、API serverのデフォルト値として使われるものであり、[client-app](../client-app/README.md)のAdminメニューでいつでも変更可能である


ユーザーアカウント登録
----------------------

API serverにアクセスできるユーザーアカウントは、2箇所で管理されている。

1. ファイル(`adcusers.py`)
    - ここでは、管理者ユーザー(administrator, uid=0, gid=0)のみを登録する
	- この`adcusers.py`は、`adcusers_in.yaml`から生成する
2. データストア (Google Cloud Datastoreのこと)
    - ここでは、すべてのユーザーを登録する。1と同じ管理者ユーザーも登録されている

### ユーザーアカウント登録用ファイルについて

(2020年変更) 以前は、Python形式のファイル`adcusers_in.py`を使っていたが、YAML形式に変更した。

- ウェブアプリ([client-app](../client-app/README.md))では、管理者がYAML形式のファイルをアップロードすることで、ユーザー登録が可能である
- 以前の方式(コマンド`adccli create-users ${top_dir}/server/adcusers_in.py`)でも、ユーザー登録が可能である

ウェブアプリを使ったユーザーアカウント登録手順については、[client-app/README.md](../client-app/README.md)を参照してほしい。



ローカル環境でAPI serverを実行する
---------------------------------

2019年、Google Cloud PlatformにてPython 3がサポートされるようになって以降、`dev_appserver.py`の利用は非推奨となった。

- ADC2021では、使っていない
- ADC2020では、もう使うのをあきらめた（いろいろ、メンドクサすぎる…）
- ADC2019では、まだ使っていた

`dev_appserver.py`の代わりに、Datastore emulatorを利用する。

Datastore emulatorを実行したあとに、API serverを実行する。


## Datastore emulatorを実行する

(参考) [Datastore emulator起動シェルスクリプト](../scripts/00_datastore.sh)で実行可能

``` bash
# datastoreのデータ保存場所を`../work/datastore/`とした場合
datastore_dir="../work/datastore/"

# 環境変数を設定する
$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)

# datastore emulatorを実行する
gcloud beta emulators datastore --data-dir "${datastore_dir}" start
```


## API serverを実行する

(参考) [API server実行シェルスクリプト](../scripts/04_server.sh)で実行可能

```
# datastoreのデータ保存場所を`../work/datastore/`とした場合
datastore_dir="../work/datastore/"

# 環境変数を設定する
$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)

# API serverを実行する
python main.py
    # または
gunicorn -b :4280 main:app
    # アクセスログが見たいときは
gunicorn -b :4280 --access-logfile '-' main:app
```
    
このAPIサーバは、`http://127.0.0.1:4280/` で動いている。




curlを使って、API serverの動作確認を行う
---------------------------------------

以下ではport番号4280を指定しているが、実際にAPI serverが使用しているポート番号に変更すること。

実行するコマンド

``` bash
curl -v http://127.0.0.1:4280/api/test_get
```

実行例

```
$ curl -v http://127.0.0.1:4280/api/test_get
*   Trying 127.0.0.1:4280...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 4280 (#0)
> GET /api/test_get HTTP/1.1
> Host: 127.0.0.1:4280
> User-Agent: curl/7.68.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Server: gunicorn
< Date: Wed, 04 Aug 2021 03:07:44 GMT
< Connection: close
< Content-Type: application/json
< Content-Length: 82
< 
{"msg":"こんにちは世界","my_url":"/api/test_get","test":"ok","value":9876}
* Closing connection 0
```


curlを使って、ファイル・チェックを行う
--------------------------------------

コマンドの書式

``` bash
curl -X POST --form Qfile=@FILE1 --form Afile=@FILE2 http://127.0.0.1:4280/api/check_file
```

- curlでJSON形式のデータを作るのは面倒だったので、特例として、フォームでファイルをアップロードするときの形式で、API `/api/check_file`を呼べるようにした
- FILE1は、Qデータのファイル
- FILE2は、Aデータのファイル
- `http://127.0.0.1:4280`は、API serverのアドレスとポート
- 結果はJSON形式で返ってくる(`Content-Type: application/json`)


### 正しいデータの実行例

``` bash
curl -X POST --form Qfile=@../samples/sampleQ0.txt --form Afile=@../samples/sampleA0.txt http://127.0.0.1:4280/api/check_file
```

実行例

```
$ curl -X POST --form Qfile=@../samples/sampleQ0.txt --form Afile=@../samples/sampleA0.txt http://127.0.0.1:4280/api/check_file
{"area":72,"ban_data_F":"[[ 0  1  1  1  1  2  2  2  2]\n [ 0 -1  0  0  4 -1  0  0  2]\n [ 0  8  8  8  4  4  4  4  2]\n [ 0  7  7  6 -1 -1 -1  4  2]\n [10 10 10  6 -1  2 -1  4  2]\n [-1  9  5  5 11  2  2  2  2]\n [ 3  9  0  0 11 -1 -1  0  0]\n [ 3  3  3  3  3  3  3  0  0]]","check_file":"ok","corner":"[[0 0 0 0 0 0 0 0 1]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 1 0 0 1 0]\n [0 0 0 0 1 0 1 0 0]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 0 1 0 0 1]\n [0 0 0 0 0 0 0 0 0]\n [1 0 0 0 0 0 0 0 0]]","count":"[[0 1 2 2 1 1 2 2 2]\n [0 0 0 0 1 0 0 0 2]\n [0 1 2 1 2 2 2 2 2]\n [0 1 1 1 2 2 2 2 2]\n [1 2 1 1 1 1 1 1 2]\n [0 1 1 1 1 2 2 2 2]\n [1 1 0 0 1 1 1 0 0]\n [2 2 2 2 2 2 1 0 0]]","dim":[0,0,9,8],"line_corner":"[0 0 3 1 2 0 0 0 0 0 0 0]","line_length":"[ 0  4 13  8  7  2  2  2  3  2  3  2]","terminal":[[],[{"block":1,"xy":[1,0]},{"block":4,"xy":[4,0]}],[{"block":4,"xy":[5,0]},{"block":6,"xy":[5,4]}],[{"block":3,"xy":[0,6]},{"block":5,"xy":[6,7]}],[{"block":4,"xy":[4,1]},{"block":8,"xy":[7,4]}],[{"block":6,"xy":[3,5]},{"block":7,"xy":[2,5]}],[{"block":2,"xy":[3,3]},{"block":7,"xy":[3,4]}],[{"block":1,"xy":[1,3]},{"block":2,"xy":[2,3]}],[{"block":1,"xy":[1,2]},{"block":2,"xy":[3,2]}],[{"block":3,"xy":[1,6]},{"block":7,"xy":[1,5]}],[{"block":3,"xy":[0,4]},{"block":7,"xy":[2,4]}],[{"block":5,"xy":[4,6]},{"block":6,"xy":[4,5]}]]}
```


### 正しくないデータの実行例


``` bash
curl -X POST --form Qfile=@../samples/sampleQ0.txt --form Afile=@../samples/sampleA0.e.txt http://127.0.0.1:4280/api/check_file
```

実行例

```
$ curl -X POST --form Qfile=@../samples/sampleQ0.txt --form Afile=@../samples/sampleA0.e.txt http://127.0.0.1:4280/api/check_file
{"error":["ADC2020 rule violation","check-QA2: inconsistent numbers on block","1","(1, 0)","[[ 1]\n [-1]\n [ 8]\n [ 7]]","[[1]\n [0]\n [8]\n [7]]"],"stack_trace":"Traceback (most recent call last):\n  File \"/home/USER/adc2019/server/main.py\", line 249, in check_file\n    info = adc2019.check_data(Q, A)\n  File \"/home/USER/adc2019/server/adc2019.py\", line 713, in check_data\n    raise RuntimeError('check-QA2: inconsistent numbers on block', b, (x, y), block_data_Q[b], block_ban_masked)\nRuntimeError: ('check-QA2: inconsistent numbers on block', 1, (1, 0), array([[ 1],\n       [-1],\n       [ 8],\n       [ 7]]), array([[1],\n       [0],\n       [8],\n       [7]]))\n"}
```



動作テスト用問題データのアップロード
--------------------------------

ローカルのテスト用サイトでの実行例

``` bash
    # adccliを使うための設定
source ../client/env.sh

    # admministratorでログインする
adccli --URL http://127.0.0.1:4280/ --username administrator login

    # admministratorでログインしていることを確認する
adccli --URL http://127.0.0.1:4280/ --username administrator whoami

    # アップロードする
cd ../samples/Q/

adccli post-user-q 1 sample_1_Q.txt
adccli post-user-q 2 sample_2_Q.txt
adccli post-user-q 3 sample_3_Q.txt
adccli post-user-q 4 sample_1_Q.txt
adccli post-user-q 5 sample_2_Q.txt
adccli post-user-q 6 sample_3_Q.txt
adccli post-user-q 7 sample_1_Q.txt
adccli post-user-q 8 sample_2_Q.txt
adccli post-user-q 9 sample_3_Q.txt
adccli post-user-q 10 sample_1_Q.txt
adccli post-user-q 11 sample_2_Q.txt
adccli post-user-q 12 sample_3_Q.txt

adccli --alt-user test-01 post-user-q 1 sample_1_Q.txt
adccli --alt-user test-01 post-user-q 2 sample_2_Q.txt
adccli --alt-user test-01 post-user-q 3 sample_3_Q.txt

adccli --alt-user test-02 post-user-q 1 sample_1_Q.txt
adccli --alt-user test-02 post-user-q 2 sample_2_Q.txt
adccli --alt-user test-02 post-user-q 3 sample_3_Q.txt

adccli --alt-user test-03 post-user-q 1 sample_1_Q.txt
adccli --alt-user test-03 post-user-q 2 sample_2_Q.txt
adccli --alt-user test-03 post-user-q 3 sample_3_Q.txt

adccli --alt-user test-04 post-user-q 1 sample_1_Q.txt
adccli --alt-user test-04 post-user-q 2 sample_2_Q.txt
adccli --alt-user test-04 post-user-q 3 sample_3_Q.txt
```


動作テスト用問題データが登録されていることを確認する
--------------------------------

ローカルのテスト用サイトでの実行例

```　bash
    # admministratorでログインしていることを確認する
adccli --URL http://127.0.0.1:4280/ --username administrator whoami

    # 確認する
adccli get-admin-q-all
```


動作テスト用問題データをすべて一括削除する
------------------------------------

ローカルのテスト用サイトでの実行例

``` bash
    # admministratorでログインしていることを確認する
adccli --URL http://127.0.0.1:4280/ --username administrator whoami

    # 削除する
adccli delete-admin-q-all

    # 確認する (削除されるまで、やや時間がかかる場合もある)
adccli get-admin-q-all
```



動作テスト用に出題番号を決める
----------------------------

``` bash
    # 出題番号を消去する
adccli delete-admin-q-list

    # 出題番号を決める（シャフルする）
adccli put-admin-q-list

    # 出題番号、作者、問題番号の対応関係を確認する
adccli get-admin-q-list
```



動作テスト用に回答データをアップロードする
----------------------------------------

本当は、`adccli get-admin-q-list` で、問題データがどれなのかを確認したあと、それと対応する回答データをアップロードすべきだが、まあ、確率33.333%で正解するはずである。


``` bash
cd ../../samples/A/

adccli put-a 1 sample_1_A.txt replace-A-number
adccli put-a 2 sample_1_A.txt replace-A-number
adccli put-a 3 sample_1_A.txt replace-A-number
adccli put-a 4 sample_1_A.txt replace-A-number
adccli put-a 5 sample_1_A.txt replace-A-number
adccli put-a 6 sample_1_A.txt replace-A-number
adccli put-a 7 sample_1_A.txt replace-A-number
adccli put-a 8 sample_1_A.txt replace-A-number
adccli put-a 9 sample_1_A.txt replace-A-number
adccli put-a 10 sample_1_A.txt replace-A-number
adccli put-a 11 sample_1_A.txt replace-A-number
adccli put-a 12 sample_1_A.txt replace-A-number
adccli put-a 13 sample_1_A.txt replace-A-number
adccli put-a 14 sample_1_A.txt replace-A-number
adccli put-a 15 sample_1_A.txt replace-A-number
adccli put-a 16 sample_1_A.txt replace-A-number
adccli put-a 17 sample_1_A.txt replace-A-number
adccli put-a 18 sample_1_A.txt replace-A-number
adccli put-a 19 sample_1_A.txt replace-A-number
adccli put-a 20 sample_1_A.txt replace-A-number

adccli --alt-username test-01 put-a 3 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 4 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 5 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 6 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 7 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 8 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 9 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 10 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 11 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 12 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 13 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 14 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 15 sample_2_A.txt replace-A-number
adccli --alt-username test-01 put-a 16 sample_2_A.txt replace-A-number

adccli --alt-username test-02 put-a 2 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 3 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 4 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 5 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 6 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 7 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 8 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 9 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 10 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 11 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 12 sample_3_A.txt replace-A-number
adccli --alt-username test-02 put-a 13 sample_3_A.txt replace-A-number

adccli --alt-username test-03 put-a 8 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 9 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 10 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 11 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 12 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 13 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 14 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 15 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 16 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 17 sample_1_A.txt replace-A-number
adccli --alt-username test-03 put-a 18 sample_1_A.txt replace-A-number

adccli --alt-username test-04 put-a 2 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 3 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 4 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 5 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 6 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 7 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 8 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 9 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 10 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 11 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 12 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 13 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 14 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 15 sample_2_A.txt replace-A-number
adccli --alt-username test-04 put-a 16 sample_2_A.txt replace-A-number
```

動作テスト用にアップロードした回答データを確認する、削除する
---------------------------------------------------------

```
    # 確認する
adccli get-admin-a-all

    # 削除する
adccli delete-admin-a-all
```





adc2019 API server on Google App Engine
=======================================

Google App Engineへ、deployする。

テスト用プロジェクト

``` bash
gcloud app deploy
    # プロジェクト名を指定する場合
gcloud app deploy --project=trusty-obelisk-631
```

本番用プロジェクト

``` bash
gcloud app deploy --project=das-adc
```


### APIの疎通確認

```
curl -v https://trusty-obelisk-631.appspot.com/api/test_get
    # または
curl -v https://das-adc.appspot.com/api/test_get
```


datastoreのインデックス更新
---------------------------

App Engineにdeployしたあと、Loggingにて、"no matching index found. recommended index is:" 〜〜〜 というエラーログがでるときは、index.yamlを更新する。

```
gcloud datastore indexes create index.yaml --project=das-adc
```

確認方法

Google Cloud Platform >> Datastore >> インデックス

`https://console.cloud.google.com/datastore/indexes?hl=ja&project=das-adc`

また、`dev_appserver.py`が自動作成した`index.yaml`が以下にある。これをコピペして使うのが正解かもしれない。ただし、コードのバグのせいで、実際には使われないインデックスが含まれていることがある（nameをtypoしてたりする）。

`$HOME/.config/gcloud/emulators/datastore/WEB-INF/index.yaml`
