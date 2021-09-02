2021年版adc2019 開発者向け情報
=============================

- [client command line tool](client/devel.md)
- [client Web application](client-app/devel.md)
- [dummy application](hello_world/README.md)
- [API server](server/devel.md)


Google Cloud SDK
----------------

Ubuntu 20.04.2 LTSなどで、簡単にインストールできる。

公式ドキュメント  
https://cloud.google.com/sdk/docs/  
https://cloud.google.com/sdk/docs/install#deb  


### Google Cloud Platformの初期設定

初期設定

```
gcloud auth login
```


プロジェクトを指定する。たとえば

```
gcloud config set project das-adc
```



<a name="miniforge"></a>
<a name="miniconda"></a>
conda-forgeのMiniforgeでPython 3.9の環境を作る
-------------------------------------------

2021年6月現在、Google App EngineではPython 3.7、3.8、3.9が利用可能になっている。

Linuxディストリビューションで提供されているパッケージのPython 3はバージョンが古いことが多いため、ここではMiniforgeを使う方法を紹介する。

※ 以前はAnacondaの利用方法を紹介していたが、Anaconda repositoryの商用利用が禁止されたため、conda-forgeのMiniforgeを採用した。Anaconda (Miniconda)同様に、Miniforgeも、Windows、Mac、Linux版がある。

ADC参加者で、[コマンドライン環境のクライアントadccli](client/README.md)を実行したい場合も、MiniforgeやMinicondaでPython 3.xの実行環境を構築するのを推奨する。

#### Miniforgeをダウンロードする

以下からMiniforgeのインストーラをダウンロードできる。

https://github.com/conda-forge/miniforge/#download

curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

#### Linux版Miniforgeのインストール例

以下ではインストール先を`/opt/miniforge3`にするためにsudoを使っているが、sudoを使わずに`/opt`以外の場所にインストールしてもよい。

``` bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

sudo mkdir /opt/miniforge3
sudo chown `whoami` /opt/miniforge3
sh Miniforge3-Linux-x86_64.sh -b -p /opt/miniforge3 -u
/opt/miniforge3/bin/conda update -n base -c defaults conda

/opt/miniforge3/bin/conda init bash  # 必要ならば
/opt/miniforge3/bin/conda config --set auto_activate_base false  # 好みで
```

##### 環境を作成する（server開発・実行ユーザー用, client-app開発用, administrator権限でadccli実行用）

``` bash
/opt/miniforge3/bin/conda create -n adc2019dev python=3.9 flask=1.1.2 flask-cors=3.0.10 numpy gunicorn grpcio pytz requests protobuf pyyaml nodejs=14 pandas openpyxl
```

##### 環境を作成する（ADC参加者、[adccli](client/README.md)を実行するだけのユーザー用）

``` bash
/opt/miniforge3/bin/conda create -n adc2019 python=3.9 numpy pyyaml
```

##### 環境を使う

``` bash
conda activate adc2019dev
    # もしくは
conda activate adc2019
```

##### datastore emulator (ADC参加者は不要)

datastore emulator (google-cloud-datastore)は、serverを実行するときに必要であり、adccliコマンドを実行するだけでの場合は不要である。

もちろんAnaconda/conda-forgeではなくて、Google Clould SDKからdebパッケージなどでインストールすることも可能である。

`conda activate adc2019dev`したあとなら、これだけで十分。

```
conda install google-cloud-datastore
```

