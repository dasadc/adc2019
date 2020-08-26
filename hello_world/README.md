# 2020

# What's this?

datastoreをdev_appserver.pyでのぞき見するために実行しておくダミーアプリ。

https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/standard_python37/building-an-app/building-an-app-2
をコピーした。

(2020-08-18) リンク切れを確認した。現在は、これかな？  
https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/standard_python3/building-an-app/building-an-app-2

### Service accountについて

datastore emulatorを使うとき、なぜか、必要だった。

(参考) https://googleapis.dev/python/google-api-core/latest/auth.html  
"Setting up a Service Account"に書いてある。

1. WebブラウザでGoogle Cloud Platformに行き、
2. Navigation Menuで、"APIs & Services" > "Credentials"を選ぶ。
3. Service Accountsのところに、"adc2019test"が、作ってある。


https://cloud.google.com/iam/docs/creating-managing-service-account-keys?hl=ja
によれば

> [作成] をクリックすると、サービス アカウント キーファイルがダウンロードされます。

> サービス アカウント キーの秘密鍵を取得できるのは、キーが最初に作成されるときのみです。

ということで、既存のキーは、再ダウンロードは不可能らしい。


### datastore emuldatorを実行する

- (参考) [Datastore エミュレータの実行](https://cloud.google.com/datastore/docs/tools/datastore-emulator?hl=ja)
- (参考) `../scripts/00_datastore.sh`


    不要？ <<<< どうも必要らしい。なぜかわからん。
    export GOOGLE_APPLICATION_CREDENTIALS=$HOME/adc2019/server/keyfile.json

```
mkdir /work/datastore
gcloud beta emulators datastore --data-dir /work/datastore start
```

### (参考)  `$HOME/.config/gcloud/emulators/datastore/env.yaml`

このファイルは、コマンド`gcloud beta emulators datastore start`を実行して、datastore emulatorを起動した時に作られるらしい。[関連情報](#troubleshooting)

しかもオプション`--data-dir`で指定したディレクトリに作られるようだ。上記ディレクトリは、`--data-dir`を指定しなかったときのデフォルトのディレクトリらしい。



### ダミーアプリを実行する

- dev_appserver.pyでdatastore emulatorを使うためにはgrpcioが必要なので、仮想環境を使う。
- dev_appserver.pyが仮想環境を作ろうとするために、いくつかインストールしておく。
- dev_appserver.pyが実行するpipで、オフライン・インストールできるようにするために、あらかじめダウンロードしておく。

```
sudo apt install python-virtualenv python3-pip python3-venv
cd $HOME/adc2019/
virtualenv --python=/usr/bin/python2.7 $HOME/adc2019/venv27
source $HOME/adc2019/venv27/bin/activate
pip install grpcio
pip3 download -d $HOME/adc2019/pip-dir/ pip gunicorn Flask==1.0.2 google-cloud-datastore==1.7.3 grpcio==1.31.0 protobuf
ln -s $HOME/adc2019/pip-dir /tmp/
```


dev_appserver.pyを実行する。

```
export CLOUDSDK_PYTHON=$HOME/adc2019/venv27/bin/python
export PIP_CONFIG_FILE=$(pwd)/pip.conf
$(gcloud beta emulators datastore env-init)
dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml 
```

#### (2020-08-16)

```
ERROR: Could not find a version that satisfies the requirement grpcio<2.0dev,>=1.29.0; extra == "grpc" (from google-api-core[grpc]<2.0.0dev,>=1.6.0->google-cloud-datastore==1.7.3->-r /tmp/tmpp9OvTG (line 2)) (from versions: 1.23.0)
ERROR: No matching distribution found for grpcio<2.0dev,>=1.29.0; extra == "grpc" (from google-api-core[grpc]<2.0.0dev,>=1.6.0->google-cloud-datastore==1.7.3->-r /tmp/tmpp9OvTG (line 2))
```
そのため、`grpcio==1.31.0`を追加した

```
Using legacy 'setup.py install' for grpcio, since package 'wheel' is not install                                                                                Installing collected packages: Werkzeug, MarkupSafe, Jinja2, itsdangerous, click, Flask, six, cachetools, pyasn1, pyasn1-modules, rsa, google-auth, pytz, protobuf, googleapis-common-protos, certifi, idna, urllib3, chardet, requests, grpcio,                                                                                                                                                                                                                                                Running setup.py install for grpcio: still running...                
```

ここから先が進まない？

```
Running setup.py install for grpcio: finished with status 'done'ERROR: After October 2020 you may experience errors when installing or updating packages. This is because pip will change the way that it resolves dependency conflicts.

We recommend you use --use-feature=2020-resolver to test your packages with the new resolver before it becomes the default.

google-auth 1.20.1 requires setuptools>=40.3.0, but you'll have setuptools 39.0.1 which is incompatible.
Successfully installed Flask-1.0.2 Jinja2-2.11.2 MarkupSafe-1.1.1 Werkzeug-1.0.1 cachetools-4.1.1 certifi-2020.6.20 chardet-3.0.4 click-7.1.2 google-api-core-1.22.1 google-auth-1.20.1 google-cloud-core-0.29.1 google-cloud-datastore-1.7.3 googleapis-common-protos-1.52.0 grpcio-1.31.0 gunicorn-20.0.4 idna-2.10 itsdangerous-1.1.0 protobuf-3.13.0 pyasn1-0.4.8 pyasn1-modules-0.2.8 pytz-2020.1 requests-                                                                                                                                                                                                                                                                                                                                                                                                                                                         
INFO     2020-08-16 09:21:25,548 dispatcher.py:267] Starting module "default" running at: http://localhost:8080
INFO     2020-08-16 09:21:25,549 admin_server.py:150] Starting admin server at: http://localhost:8000
[2020-08-16 18:21:26 +0900] [7015] [INFO] Starting gunicorn 20.0.4
[2020-08-16 18:21:26 +0900] [7015] [INFO] Listening at: http://0.0.0.0:19192 (7015)
[2020-08-16 18:21:26 +0900] [7015] [INFO] Using worker: sync
[2020-08-16 18:21:26 +0900] [7018] [INFO] Booting worker with pid: 7018
[2020-08-16 18:21:26 +0900] [7018] [ERROR] Exception in worker process
Traceback (most recent call last):
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/arbiter.py", line 583, in spawn_worker
    worker.init_process()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/workers/base.py", line 119, in init_process
    self.load_wsgi()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/workers/base.py", line 144, in load_wsgi
    self.wsgi = self.app.wsgi()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/app/base.py", line 67, in wsgi
    self.callable = self.load()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/app/wsgiapp.py", line 49, in load
    return self.load_wsgiapp()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/app/wsgiapp.py", line 39, in load_wsgiapp
    return util.import_app(self.app_uri)
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/gunicorn/util.py", line 358, in import_app
    mod = importlib.import_module(module)
  File "/usr/lib/python3.6/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 994, in _gcd_import
  File "<frozen importlib._bootstrap>", line 971, in _find_and_load
  File "<frozen importlib._bootstrap>", line 955, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 665, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 678, in exec_module
  File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
  File "/home/USER/adc2019/hello_world/main.py", line 38, in <module>
    datastore_client = datastore.Client()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/google/cloud/datastore/client.py", line 210, in __init__
    project=project, credentials=credentials, _http=_http
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/google/cloud/client.py", line 224, in __init__
    Client.__init__(self, credentials=credentials, _http=_http)
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/google/cloud/client.py", line 130, in __init__
    credentials, _ = google.auth.default()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/google/auth/_default.py", line 338, in default
    credentials, project_id = checker()
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/google/auth/_default.py", line 186, in _get_explicit_environ_credentials
    os.environ[environment_vars.CREDENTIALS]
  File "/tmp/tmpnvT0w3/lib/python3.6/site-packages/google/auth/_default.py", line 97, in load_credentials_from_file
    "File {} was not found.".format(filename)
google.auth.exceptions.DefaultCredentialsError: File /home/USER/keyfile.json was not found.
[2020-08-16 18:21:26 +0900] [7018] [INFO] Worker exiting (pid: 7018)
[2020-08-16 18:21:26 +0900] [7015] [INFO] Shutting down: Master
[2020-08-16 18:21:26 +0900] [7015] [INFO] Reason: Worker failed to boot.
ERROR    2020-08-16 09:21:27,556 instance.py:284] Cannot connect to the instance on localhost:19192
INFO     2020-08-16 09:21:29,626 module.py:432] [default] Detected file changes:
  /home/USER/adc2019/hello_world/README.md
```


#### ...つづき

デフォルトでは
アプリは http://localhost:8080  
admin serverが http://localhost:8000/


あまりよくないが、admin serverに他から接続可能にするには、

```
dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml --admin_host 0.0.0.0 --admin_port 8000 --enable_host_checking=False
```


**(注意)**

- dev_appserver.pyで、python3.7のアプリを実行するとき、`/tmp/`以下に仮想環境が作られて、pip installが実行される。ここに、requirements.txtに書かれたパッケージがインストールされる。
- dev_appserver.pyから起動されるアプリは、`/tmp/`以下に作られた仮想環境の`python3`を使って実行される。そのプロセスには、なぜか、datastore emulatorの環境変数が引き継がれない


<a name="troubleshooting"></a>
### (トラブルシューティング) なぜかプロジェクトが違っていてdatastore viewerに情報が出てこないとき

`gcloud beta emulators datastore env-init`
で表示される内容は、ファイル
`$HOME/.config/gcloud/emulators/datastore/env.yaml`
に書かれている。
このファイルは、
`gcloud beta emulators datastore start`
を実行したときに書き出される。
そのときのデフォルトのプロジェクト名が、この`env.yaml`に書き込まれてしまう。

