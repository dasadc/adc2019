# What's this?

datastoreをdev_appserver.pyでのぞき見するために実行しておくダミーアプリ。

https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/standard_python37/building-an-app/building-an-app-2
をコピーした。


### datastore emuldatorを実行する

    不要？
    export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keyfile.json

```
mkdir /work/datastore
gcloud beta emulators datastore --data-dir /work/datastore start
```

### ダミーアプリを実行する

- dev_appserver.pyでdatastore emulatorを使うためにはgrpcioが必要なので、仮想環境を使う。
- dev_appserver.pyが仮想環境を作ろうとするために、いくつかインストールしておく。
- dev_appserver.pyが実行するpipで、オフライン・インストールできるようにするために、あらかじめダウンロードしておく。

```
sudo apt install python-virtualenv python3-pip python3-venv
virtualenv --python=/usr/bin/python2.7 /work/venv27
source /work/venv27/bin/activate
pip install grpcio
pip3 download -d /work/pip-dir/ pip gunicorn Flask==1.0.2 google-cloud-datastore==1.7.3
```


dev_appserver.pyを実行する。

```
export CLOUDSDK_PYTHON=/work/venv27/bin/python
export PIP_CONFIG_FILE=$(pwd)/pip.conf
$(gcloud beta emulators datastore env-init)
dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml 
```

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


### (トラブルシューティング) なぜかプロジェクトが違っていてdatastore viewerに情報が出てこないとき

`gcloud beta emulators datastore env-init`
で表示される内容は、ファイル
`$HOME/.config/gcloud/emulators/datastore/env.yaml`
に書かれている。
このファイルは、
`gcloud beta emulators datastore start`
したときに書き出される。
そのときのデフォルトのプロジェクト名が、この`env.yaml`に書き込まれてしまう。

