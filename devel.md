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

https://cloud.google.com/sdk/docs/#deb

追加インストール

sudo apt install google-cloud-sdk-datastore-emulator google-cloud-sdk-app-engine-python

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
conda install Flask==1.0.2
conda install numpy
conda install gunicorn
```
