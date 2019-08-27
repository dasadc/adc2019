ADC2019スタッフ用マニュアル
=============================


以下では、`$HOME/adc2019`にファイル一式を置くとして、説明している。


初期設定
--------

```
cd $HOME/
git clone https://github.com/dasadc/adc2019.git
```

足りないファイルを追加。

```
tar xvf ~/extra.tar -C $HOME/adc2019/server/
```

### インストール

#### Google Cloud Platform SDK

詳細 [devel.md](devel.md)

Ubuntu 18.04.3 LTSの場合

```
export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk

sudo apt install google-cloud-sdk-datastore-emulator google-cloud-sdk-app-engine-python
```

プロジェクトを指定する。

```
gcloud config set project test813
```


さらに追加インストール


```
sudo apt install python-virtualenv python3-pip python3-venv
cd $HOME/adc2019/
virtualenv --python=/usr/bin/python2.7 $HOME/adc2019/venv27
source $HOME/adc2019/venv27/bin/activate
pip install grpcio
pip3 download -d $HOME/adc2019/pip-dir/ pip gunicorn Flask==1.0.2 google-cloud-datastore==1.7.3 numpy
ln -s $HOME/adc2019/pip-dir /tmp/
```

なぜか、datastore emulatorを使うためにも、credentialが必要らしい。

```
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keyfile.json
```


APIサーバ用にも仮想環境を作る。

```
virtualenv --python=/usr/bin/python3 $HOME/adc2019/venv36
source $HOME/adc2019/venv36/bin/activate
pip install -r $HOME/adc2019/server/requirements.txt
pip install gunicorn
```



実行する
--------

### datastore emulator

```
mkdir -p $HOME/adc2019/work/datastore
gcloud beta emulators datastore --data-dir $HOME/adc2019/work/datastore start
```


### ダミーアプリ

詳細 [hello_world/README.md](hello_world/README.md)

dev_appserver.pyを実行する。

```
export CLOUDSDK_PYTHON=$HOME/adc2019/venv27/bin/python
export PIP_CONFIG_FILE=$HOME/adc2019/hello_world/pip.conf
$(gcloud beta emulators datastore --data-dir $HOME/adc2019/work/datastore env-init)
dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml 
```

デフォルトでは
アプリは http://localhost:8080  
admin serverが http://localhost:8000/

あまりよくないが、admin serverに他から接続可能にするには、

```
dev_appserver.py --application=test813 --support_datastore_emulator=true app.yaml --admin_host 0.0.0.0 --admin_port 8000 --enable_host_checking=False
```


### API server 兼 Web server

参照 [server/devel.md](server/devel.md)

```
source $HOME/adc2019/venv36/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keyfile.json
$(gcloud beta emulators datastore --data-dir $HOME/adc2019/work/datastore env-init)
```

```
gunicorn -b :4280 --access-logfile '-' main:app
```

#### Webアプリ

http://127.0.0.1:4280/static/app/index.html


### ユーザー登録 (初回に1回だけ実行すればOK)

```
source ~/adc2019/client/env.sh

adccli --URL='http://127.0.0.1:4280/' --username='administrator' --password='パスワード' login

adccli create-users $HOME/adc2019/server/adcusers_in.py
```


### ネットワーク周りの設定。

VirtualBoxのport forwardingの設定。
NATで動かしているので。

ホスト TCP 8080 ---> ゲスト 4280

ファイアウォール確認

sudo ufw status


動作テスト
--------

Adminメニュー

- Mode = 0
- State = init
- Test mode = False


### テスト用データ登録

[server/devel.md](server/devel.md)の
「テスト用回答データのアップロード」
を参照。

問題リスト作成で、1回目は、なぜかうまく行かなかった。
deleteしてから、putしたら、リスト作成できた。
datastoreにentityは作られているけど、リストが空っぽだった。

