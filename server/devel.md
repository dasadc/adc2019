adc2019 API server version 20210714
===================================

(注意) ドキュメントを更新していないため、古い情報が書かれているところがあります。

以下で説明する手順をスキップして、[Dockerコンテナでかんたんに動かすこともできます](../docker/README.md)。


開発・実行のための環境構築
--------------------------

conda-forgeの「Miniforge」の利用を推奨する。[>> How?](../devel.md#miniforge)


サーバー設定ファイル`adcconfig.py`
-------------------------------------

`adcconfig.py`は、サーバー起動時に読み込まれる設定ファイルである。

1. `YEAR`を、今年の西暦年(e.g. 2021)にする。この値は、[ウェブアプリ(client-app)](../client-app/README.md)での画面表示にも反映される
2. `SECRET_KEY`を、設定する。これは他者には秘密にする情報である
3. `SALT`を、設定する。これも秘密にする情報である
4. `TEST_MODE`と`VIEW_SCORE_MODE`は、サーバーのデフォルト値として使われるものであり、[client-app](../client-app/README.md)のAdminメニューでいつでも変更可能である


ユーザーアカウント登録
----------------------

サーバーにアクセスできるユーザーアカウントは、2箇所で管理されている。

1. ファイル(`adcusers.py`)
    - ここでは、管理者ユーザー(administrator, uid=0, gid=0)のみを登録する
	- この`adcusers.py`は、`adcusers_in.yaml`から生成する
2. データストア
    - ここでは、すべてのユーザーを登録する。1と同じ管理者ユーザーも登録されている

### ユーザーアカウント登録について

(2020年変更) 以前は、Python形式のファイル`adcusers_in.py`を使っていたが、YAML形式に変更した。

- ウェブアプリ([client-app](../client-app/README.md))では、管理者がYAML形式のファイルをアップロードすることで、ユーザー登録が可能である
- 以前の方式(コマンド`adccli create-users ${top_dir}/server/adcusers_in.py`)でも、ユーザー登録が可能である

ウェブアプリを使ったユーザーアカウント登録手順については、[client-app/README.md](../client-app/README.md)を参照してほしい。



実行する
--------

2019年、Google Cloud PlatformにてPython 3がサポートされるようになって以降、`dev_appserver.py`の利用は非推奨となった。

- ADC2021では、使っていない
- ADC2020では、もう使うのをあきらめた（いろいろ、メンドクサすぎる…）
- ADC2019では、まだ使っていた


### 開発時 (OBSOLETE)

datastoreを`dev_appserver.py`でのぞき見するためにダミーアプリを実行しているが、そのプロジェクトがtest813なので、それと同じにしておく。

```
gcloud config set project test813
```

プロジェクト名を指定した後に、datastore emulatorを起動すべきである。
そのあとで、datastoreを使うための環境設定をする。

```
source /work/venv36/bin/activate
# export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keyfile.json <<< 2020年8月現在、不要。どうも、2019年8月当時のgoogleのバグではないか？
$(gcloud beta emulators datastore env-init)
```

(ADC2020 注) `dev_appserver.py`は、もう使わないことにした。

`dev_appserver.py`の立ち上げ方は、[../hello_world/README.md](../hello_world/README.md)を参照。

Datastore Viewerは
http://localhost:8000/datastore


## (backend) API server

```
python main.py
または
gunicorn -b :4280 main:app
アクセスログが見たいときは
gunicorn -b :4280 --access-logfile '-' main:app
```
    
http://127.0.0.1:4280/ で動いている。




adc2019 API server
==================

Google App Engineへ、deployする。

テスト用プロジェクト

```
cd server/
gcloud app deploy
プロジェクト名を指定する場合
gcloud app deploy --project=trusty-obelisk-631
```

本番(?予定?)用プロジェクト

```
gcloud app deploy --project=das-adc
```


APIの疎通確認

```
curl -v https://trusty-obelisk-631.appspot.com/api/test_get
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


curlを使って、APIサーバの動作確認を行う
---------------------------------------

以下ではport番号4280を指定しているが、実際にAPIサーバが使用しているポート番号に変更すること。

```
$ curl -v http://127.0.0.1:4280/api/test_get
* About to connect() to 127.0.0.1 port 4280 (#0)
*   Trying 127.0.0.1...
* Connected to 127.0.0.1 (127.0.0.1) port 4280 (#0)
> GET /api/test_get HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 127.0.0.1:4280
> Accept: */*
> 
< HTTP/1.1 200 OK
< Server: gunicorn/19.9.0
< Date: Tue, 20 Aug 2019 01:50:34 GMT
< Connection: close
< Content-Type: application/json
< Content-Length: 57
< 
{"msg":"こんにちは世界","test":"ok","value":9876}
* Closing connection 0
```


curlを使って、ファイル・チェックを行う
--------------------------------------


```
curl -X POST --form Qfile=@FILE1 --form Afile=@FILE2 http://127.0.0.1:4280/api/check_file
```

- curlでJSON形式のデータを作るのは面倒だったので、特例として、フォームでファイルをアップロードするときの形式で、API `/api/check_file`を呼べるようにした
- FILE1は、Qデータのファイル
- FILE2は、Aデータのファイル
- `http://127.0.0.1:4280`は、APIサーバのアドレスとポート
- 結果はJSON形式で返ってくる(`Content-Type: application/json`)


### 正しいデータの例

```
$ curl -X POST --form Qfile=@sampleQ0.txt --form Afile=@sampleA0.txt http://127.0.0.1:4280/api/check_file
{"area":72,"ban_data_F":"[[ 0  1  1  1  1  2  2  2  2]\n [ 0 -1  0  0  4 -1  0  0  2]\n [ 0  8  8  8  4  4  4  4  2]\n [ 0  7  7  6 -1 -1 -1  4  2]\n [10 10 10  6 -1  2 -1  4  2]\n [-1  9  5  5 11  2  2  2  2]\n [ 3  9  0  0 11 -1 -1  0  0]\n [ 3  3  3  3  3  3  3  0  0]]","check_file":"ok","corner":"[[0 0 0 0 0 0 0 0 1]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 1 0 0 1 0]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 0 1 0 0 1]\n [0 0 0 0 0 0 0 0 0]\n [1 0 0 0 0 0 0 0 0]]","count":"[[0 1 2 2 1 1 2 2 2]\n [0 0 0 0 1 0 0 0 2]\n [0 1 2 1 2 2 2 2 2]\n [0 1 1 1 0 0 0 2 2]\n [1 2 1 1 0 1 0 1 2]\n [0 1 1 1 1 2 2 2 2]\n [1 1 0 0 1 0 0 0 0]\n [2 2 2 2 2 2 1 0 0]]","dim":[0,0,9,8],"line_corner":"[0 0 3 1 2 0 0 0 0 0 0 0]","line_length":"[ 0  4 13  8  7  2  2  2  3  2  3  2]","terminal":[[],[{"block":1,"xy":[1,0]},{"block":4,"xy":[4,0]}],[{"block":4,"xy":[5,0]},{"block":6,"xy":[5,4]}],[{"block":3,"xy":[0,6]},{"block":5,"xy":[6,7]}],[{"block":4,"xy":[4,1]},{"block":8,"xy":[7,4]}],[{"block":6,"xy":[3,5]},{"block":7,"xy":[2,5]}],[{"block":2,"xy":[3,3]},{"block":7,"xy":[3,4]}],[{"block":1,"xy":[1,3]},{"block":2,"xy":[2,3]}],[{"block":1,"xy":[1,2]},{"block":2,"xy":[3,2]}],[{"block":3,"xy":[1,6]},{"block":7,"xy":[1,5]}],[{"block":3,"xy":[0,4]},{"block":7,"xy":[2,4]}],[{"block":5,"xy":[4,6]},{"block":6,"xy":[4,5]}]]}
```


### 正しくないデータの例

```
$ curl -X POST --form Qfile=@sampleQ0.txt --form Afile=@sampleQ0.txt http://127.0.0.1:4280/api/check_file

省略
```


テスト用問題データのアップロード
--------------------------------

ローカルのテスト用サイトを選択すること。

```
adccli --URL http://127.0.0.1:4280/ --username administrator whoami

cd ../sample_hiromoto_1-12_mod/

adccli post-user-q 1 sample_hiromoto_1_Q.txt
adccli post-user-q 2 sample_hiromoto_2_Q.txt
adccli post-user-q 3 sample_hiromoto_3_Q.txt
adccli post-user-q 4 sample_hiromoto_1_Q.txt
adccli post-user-q 5 sample_hiromoto_2_Q.txt
adccli post-user-q 6 sample_hiromoto_3_Q.txt
adccli post-user-q 7 sample_hiromoto_1_Q.txt
adccli post-user-q 8 sample_hiromoto_2_Q.txt
adccli post-user-q 9 sample_hiromoto_3_Q.txt
adccli post-user-q 10 sample_hiromoto_1_Q.txt
adccli post-user-q 11 sample_hiromoto_2_Q.txt
adccli post-user-q 12 sample_hiromoto_3_Q.txt

adccli --alt-user test-01 post-user-q 1 sample_hiromoto_1_Q.txt
adccli --alt-user test-01 post-user-q 2 sample_hiromoto_2_Q.txt
adccli --alt-user test-01 post-user-q 3 sample_hiromoto_3_Q.txt

adccli --alt-user test-02 post-user-q 1 sample_hiromoto_1_Q.txt
adccli --alt-user test-02 post-user-q 2 sample_hiromoto_2_Q.txt
adccli --alt-user test-02 post-user-q 3 sample_hiromoto_3_Q.txt

adccli --alt-user test-03 post-user-q 1 sample_hiromoto_1_Q.txt
adccli --alt-user test-03 post-user-q 2 sample_hiromoto_2_Q.txt
adccli --alt-user test-03 post-user-q 3 sample_hiromoto_3_Q.txt

adccli --alt-user test-04 post-user-q 1 sample_hiromoto_1_Q.txt
adccli --alt-user test-04 post-user-q 2 sample_hiromoto_2_Q.txt
adccli --alt-user test-04 post-user-q 3 sample_hiromoto_3_Q.txt
```

テスト用問題データの確認
--------------------------------

ローカルのテスト用サイトを選択すること。

```
adccli --URL http://127.0.0.1:4280/ --username administrator whoami

adccli get-admin-q-all
```


テスト用問題データの削除
--------------------------------

ローカルのテスト用サイトを選択すること。

```
adccli --URL http://127.0.0.1:4280/ --username administrator whoami

adccli delete-admin-q-all
```


テスト用回答データのアップロード
---------------------------------

本当は、`adccli get-admin-q-list` で、問題データがどれなのかを確認したあと、それと対応する回答データをアップロードすべき。
まあ、確率33.333%で正解するはず。


```
adccli put-a 1 sample_hiromoto_1_A.txt 
adccli put-a 2 sample_hiromoto_1_A.txt 
adccli put-a 3 sample_hiromoto_1_A.txt 
adccli put-a 4 sample_hiromoto_1_A.txt 
adccli put-a 5 sample_hiromoto_1_A.txt 
adccli put-a 6 sample_hiromoto_1_A.txt 
adccli put-a 7 sample_hiromoto_1_A.txt 
adccli put-a 8 sample_hiromoto_1_A.txt 
adccli put-a 9 sample_hiromoto_1_A.txt 
adccli put-a 10 sample_hiromoto_1_A.txt 
adccli put-a 11 sample_hiromoto_1_A.txt 
adccli put-a 12 sample_hiromoto_1_A.txt 
adccli put-a 13 sample_hiromoto_1_A.txt 
adccli put-a 14 sample_hiromoto_1_A.txt 
adccli put-a 15 sample_hiromoto_1_A.txt 
adccli put-a 16 sample_hiromoto_1_A.txt 
adccli put-a 17 sample_hiromoto_1_A.txt 
adccli put-a 18 sample_hiromoto_1_A.txt 
adccli put-a 19 sample_hiromoto_1_A.txt 
adccli put-a 20 sample_hiromoto_1_A.txt 

adccli --alt-username test-01 put-a 3 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 4 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 5 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 6 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 7 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 8 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 9 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 10 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 11 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 12 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 13 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 14 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 15 sample_hiromoto_2_A.txt 
adccli --alt-username test-01 put-a 16 sample_hiromoto_2_A.txt 

adccli --alt-username test-02 put-a 2 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 3 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 4 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 5 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 6 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 7 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 8 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 9 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 10 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 11 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 12 sample_hiromoto_3_A.txt 
adccli --alt-username test-02 put-a 13 sample_hiromoto_3_A.txt 

adccli --alt-username test-03 put-a 8 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 9 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 10 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 11 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 12 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 13 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 14 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 15 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 16 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 17 sample_hiromoto_1_A.txt 
adccli --alt-username test-03 put-a 18 sample_hiromoto_1_A.txt 

adccli --alt-username test-04 put-a 2 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 3 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 4 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 5 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 6 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 7 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 8 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 9 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 10 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 11 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 12 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 13 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 14 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 15 sample_hiromoto_2_A.txt 
adccli --alt-username test-04 put-a 16 sample_hiromoto_2_A.txt 
```


# 2019-08-28 BUG

```
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1813, in full_dispatch_request
    rv = self.dispatch_request()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1799, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "/home/USER/adc2019/server/main.py", line 590, in admin_A_all
    msg, data = cds.get_or_delete_A_data(delete=True)
ValueError: not enough values to unpack (expected 2, got 0)
127.0.0.1 - - [28/Aug/2019:16:44:25 +0900] "DELETE /api/A HTTP/1.1" 500 290 "-" "adcclient/2019.08.21"
```


とりあえず修正


# 2019-08-28 1500 bytes制限バグ


```
[2019-08-28 16:52:50,223] ERROR in app: Exception on /user/administrator/Q/30 [POST]
Traceback (most recent call last):
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/grpc_helpers.py", line 57, in error_remapped_callable
    return callable_(*args, **kwargs)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/grpc/_channel.py", line 565, in __call__
    return _end_unary_response_blocking(state, call, False, None)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/grpc/_channel.py", line 467, in _end_unary_response_blocking
    raise _Rendezvous(state, None, None, deadline)
grpc._channel._Rendezvous: <_Rendezvous of RPC that terminated with:
	status = StatusCode.INVALID_ARGUMENT
	details = "The value of property "text" is longer than 1500 bytes."
	debug_error_string = "{"created":"@1566978770.223421264","description":"Error received from peer ipv4:127.0.0.1:8081","file":"src/core/lib/surface/call.cc","file_line":1052,"grpc_message":"The value of property "text" is longer than 1500 bytes.","grpc_status":3}"
>

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 2292, in wsgi_app
    response = self.full_dispatch_request()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1815, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1718, in handle_user_exception
    reraise(exc_type, exc_value, tb)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/_compat.py", line 35, in reraise
    raise value
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1813, in full_dispatch_request
    rv = self.dispatch_request()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1799, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "/home/USER/adc2019/server/main.py", line 736, in user_q
    flag, *args = cds.insert_Q_data(q_num, q_text, author=usernm, filename=filename)
  File "/home/USER/adc2019/server/conmgr_datastore.py", line 284, in insert_Q_data
    client.put(dat) # 登録する
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/client.py", line 421, in put
    self.put_multi(entities=[entity])
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/client.py", line 448, in put_multi
    current.commit()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/batch.py", line 274, in commit
    self._commit()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/batch.py", line 250, in _commit
    self.project, mode, self._mutations, transaction=self._id
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore_v1/gapic/datastore_client.py", line 501, in commit
    request, retry=retry, timeout=timeout, metadata=metadata
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/gapic_v1/method.py", line 143, in __call__
    return wrapped_func(*args, **kwargs)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/retry.py", line 273, in retry_wrapped_func
    on_error=on_error,
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/retry.py", line 182, in retry_target
    return target()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/timeout.py", line 214, in func_with_timeout
    return func(*args, **kwargs)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/grpc_helpers.py", line 59, in error_remapped_callable
    six.raise_from(exceptions.from_grpc_error(exc), exc)
  File "<string>", line 3, in raise_from
google.api_core.exceptions.InvalidArgument: 400 The value of property "text" is longer than 1500 bytes.
127.0.0.1 - - [28/Aug/2019:16:52:50 +0900] "POST /api/user/administrator/Q/30 HTTP/1.1" 500 290 "-" "adcclient/2019.08.21"
```



Aも同様


```
[2019-08-28 17:47:36,328] ERROR in app: Exception on /A/administrator/Q/30 [PUT]
Traceback (most recent call last):
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/grpc_helpers.py", line 57, in error_remapped_callable
    return callable_(*args, **kwargs)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/grpc/_channel.py", line 565, in __call__
    return _end_unary_response_blocking(state, call, False, None)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/grpc/_channel.py", line 467, in _end_unary_response_blocking
    raise _Rendezvous(state, None, None, deadline)
grpc._channel._Rendezvous: <_Rendezvous of RPC that terminated with:
	status = StatusCode.INVALID_ARGUMENT
	details = "The value of property "text" is longer than 1500 bytes."
	debug_error_string = "{"created":"@1566982056.327710812","description":"Error received from peer ipv4:127.0.0.1:8081","file":"src/core/lib/surface/call.cc","file_line":1052,"grpc_message":"The value of property "text" is longer than 1500 bytes.","grpc_status":3}"
>

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 2292, in wsgi_app
    response = self.full_dispatch_request()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1815, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1718, in handle_user_exception
    reraise(exc_type, exc_value, tb)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/_compat.py", line 35, in reraise
    raise value
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1813, in full_dispatch_request
    rv = self.dispatch_request()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/flask/app.py", line 1799, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "/home/USER/adc2019/server/main.py", line 635, in a_put
    flag, msg = cds.put_A_data(a_num, usernm, atext)
  File "/home/USER/adc2019/server/conmgr_datastore.py", line 861, in put_A_data
    client.put(entity)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/client.py", line 421, in put
    self.put_multi(entities=[entity])
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/client.py", line 448, in put_multi
    current.commit()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/batch.py", line 274, in commit
    self._commit()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore/batch.py", line 250, in _commit
    self.project, mode, self._mutations, transaction=self._id
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/cloud/datastore_v1/gapic/datastore_client.py", line 501, in commit
    request, retry=retry, timeout=timeout, metadata=metadata
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/gapic_v1/method.py", line 143, in __call__
    return wrapped_func(*args, **kwargs)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/retry.py", line 273, in retry_wrapped_func
    on_error=on_error,
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/retry.py", line 182, in retry_target
    return target()
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/timeout.py", line 214, in func_with_timeout
    return func(*args, **kwargs)
  File "/home/USER/adc2019/venv36/lib/python3.6/site-packages/google/api_core/grpc_helpers.py", line 59, in error_remapped_callable
    six.raise_from(exceptions.from_grpc_error(exc), exc)
  File "<string>", line 3, in raise_from
google.api_core.exceptions.InvalidArgument: 400 The value of property "text" is longer than 1500 bytes.
127.0.0.1 - - [28/Aug/2019:17:47:36 +0900] "PUT /api/A/administrator/Q/30 HTTP/1.1" 500 290 "-" "adcclient/2019.08.21"
e= check-QA1: number of block mismatch
127.0.0.1 - - [28/Aug/2019:17:47:36 +0900] "PUT /api/A/administrator/Q/31 HTTP/1.1" 200 57 "-" "adcclient/2019.08.21"
[2019-08-28 18:08:48 +0900] [9167] [CRITICAL] WORKER TIMEOUT (pid:9170)
[2019-08-28 18:08:48 +0900] [9170] [INFO] Worker exiting (pid: 9170)
[2019-08-28 18:08:49 +0900] [9386] [INFO] Booting worker with pid: 9386
```
