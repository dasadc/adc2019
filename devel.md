adc2019 開発者向け情報
======================

- [client command line tool](client/devel.md)
- [client Web application](client-app/devel.md)
- [dummy application](hello_world/README.md)
- [API server](server/devel.md)


Google Cloud SDK
----------------

https://cloud.google.com/sdk/docs/


### Ubuntu 18.04.3 LTSの場合

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

プロジェクトを指定する。

gcloud config set project test813


### Google Cloud Platformの初期設定

初期設定

```
gcloud auth login
gcloud config set project xxxxxx-xxxxxxx-xxx
```



Anaconda (Miniconda)
--------------------

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3

conda config --set auto_activate_base false

conda update -n base -c defaults conda
conda create -n py37 python=3.7
conda activate py37
conda install Flask==1.0.2 numpy gunicorn
```
