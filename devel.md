2020年版adc2019 開発者向け情報
=============================

- [client command line tool](client/devel.md)
- [client Web application](client-app/devel.md)
- [dummy application](hello_world/README.md)
- [API server](server/devel.md)


Google Cloud SDK
----------------

https://cloud.google.com/sdk/docs/


### Ubuntu 18.04.5 LTSの場合

公式ドキュメント  
https://cloud.google.com/sdk/docs/#deb

実行するコマンド

```
export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install google-cloud-sdk
```

追加インストール

```
sudo apt install google-cloud-sdk-datastore-emulator google-cloud-sdk-app-engine-python
```

### Google Cloud Platformの初期設定

初期設定

```
gcloud auth login
```


プロジェクトを指定する。たとえば

```
gcloud config set project test813
```



<a name="miniconda"></a>
Anaconda (Miniconda)でPython 3.8の環境を作る
-------------------------------------------

2020年8月現在、Google App EngineではPython 3.7と3.8が利用可能になっている。

Linuxディストリビューションで提供されているPython 3のバージョンが古いことが多いため、Anacondaを使うのがよい（ファイルサイズの小さいMinicondaで十分である）。

※ Anaconda(Miniconda)は、Windows、Mac、Linux版がある。

ADC参加者で、[コマンドライン環境のクライアントadccli](client/README.md)を実行したい場合も、MinicondaでPythonの実行環境を構築するのを推奨する。

#### Linux版Minicondaのインストール例

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

sudo mkdir /opt/miniconda3
sudo chown `whoami` /opt/miniconda3
sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 -u
/opt/miniconda3/bin/conda update -n base -c defaults conda

/opt/miniconda3/bin/conda init bash  # 必要ならば
/opt/miniconda3/bin/conda config --set auto_activate_base false  # 好みで
```

環境を作成する（server開発・実行ユーザー用）

```
/opt/miniconda3/bin/conda create -n py38 python=3.8 Flask=1.1.2 numpy gunicorn grpcio pytz requests protobuf pyyaml nodejs
```

環境を作成する（ADC参加者、[adccli](client/README.md)を実行するだけのユーザー用）

```
/opt/miniconda3/bin/conda create -n py38 python=3.8 numpy pyyaml
```

環境を使う

```
conda activate py38
```

##### datastore emulator (ADC参加者は不要)

datastore emulator (google-cloud-datastore)は、serverを実行するときに必要であり、adccliコマンドを実行するだけでの場合は不要である。

`conda activate py38`したあとなら、これだけで十分。

```
pip install google-cloud-datastore
```

google-cloud-datastoreは、仮想環境へpipでインストールする例

```
python3 -m venv --system-site-packages ./venv
source venv/bin/activate
pip install google-cloud-datastore
```

