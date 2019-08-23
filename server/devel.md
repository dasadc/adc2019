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



# 初期設定

```
npm init
npm install @angular/cli
npm install typescript
npm install http-server
npm install ngx-file-drop --save

sh ~/Downloads/Miniconda3-latest-Linux-x86_64.sh 
/opt/miniconda3 にインストールした
bash
conda config --set auto_activate_base false


conda update -n base -c defaults conda
conda create -n py37 python=3.7
conda activate py37
conda install Flask==1.0.2
conda install numpy
conda install gunicorn

gunicorn main:app
http://127.0.0.1:8000/static/app/index.html
```

## 2019-08-17

### 初期設定

```
virtualenv --python=/usr/bin/python3 ~/adc2019/venv
source ~/adc2019/venv/bin/activate
pip install -r requirements.txt
```

### 開発時＆実行時

datastoreをdev_appserver.pyでのぞき見するためにダミーアプリを実行しているが、そのプロジェクトがtest813なので、それと同じにしておく。

```
gcloud config set project test813
```

プロジェクト名を指定した後に、datastore emulatorを起動すべきである。


そのあとで、datastoreを使うための環境設定をする。


```
source ~/adc2019/venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/test813-570bf90326e3.json
$(gcloud beta emulators datastore env-init)
```



# 開発中の実行方法

## dev_appserver.py

```
dev_appserver.py --application=test813 --support_datastore_emulator=true --port=18080 app.yaml 
```

Datastore Viewer
http://localhost:8000/datastore


## (backend) API server

```
python main.py
または
gunicorn -b :4280 main:app
アクセスログが欲しいときは
gunicorn -b :4280 --access-logfile '-' main:app
```
    
http://127.0.0.1:4280/ で動いている。


## (frontend) Angular, development server

```
$(npm bin)/ng serve --proxy-config proxy.conf.json --live-reload --watch --poll 9999
または
npm run test-run
```

http://localhost:4200/


## deploy前のテスト実行方法

ビルドする。

```
cd client-app/
$(npm bin)/ng build --prod --base-href=/static/app/index.html --output-path=../server/static/app/
または
npm run build
```

実行する。

	cd server/
	gunicorn main:app
    ポート番号8000がすでに使われていて変更したいとき
    gunicorn -b :28000 --access-logfile '-' main:app

- http://127.0.0.1:8000/static/app/index.html
- http://127.0.0.1:28000/static/app/index.html

もしも、開発中のdevelopment serverが動き続けているなら、それも使える。

- http://127.0.0.1:4280/static/app/index.html


## Google Cloud Platform

初期設定

```
gcloud auth login
gcloud config set project xxxxxx-xxxxxxx-xxx
```

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
