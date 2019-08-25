adc2019 API server
==================

初期設定
--------

```
virtualenv --python=/usr/bin/python3 /work/venv36
source /work/venv36/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

実行する
--------


### 開発時

datastoreをdev_appserver.pyでのぞき見するためにダミーアプリを実行しているが、そのプロジェクトがtest813なので、それと同じにしておく。

```
gcloud config set project test813
```

プロジェクト名を指定した後に、datastore emulatorを起動すべきである。
そのあとで、datastoreを使うための環境設定をする。

```
source /work/venv36/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keyfile.json
$(gcloud beta emulators datastore env-init)
```

dev_appserver.pyの立ち上げ方は、[../hello_world/README.md](../hello_world/README.md)を参照。

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



deploy

```
cd server/
gcloud app deploy
プロジェクト名を指定する場合
gcloud app deploy --project=trusty-obelisk-631
```

```
gcloud app deploy --project=das-adc
```


APIの疎通確認

```
curl -v https://trusty-obelisk-631.appspot.com/api/test_get
```



curlを使って、APIサーバの動作確認を行う
---------------------------------------

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


