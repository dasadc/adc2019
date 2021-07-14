Docker image
=================

ADC serverをかんたんに起動できるようにするDocker iamgeについて説明する。

- 2021-07-14現在、ADC2021にむけての作業中
- 開発者以外の、ADC運営担当者、serverを実行するだけの人は、docker imageを作成する必要は無いので、[docker run](#docker-run)から読めばよい。
- ADC参加者(`adccli`を実行するだけの人)も、このDocker imageを使って、`adccli`を実行できるが、Docker imageのサイズが大きすぎるため、メリットは無い。


Docker image作成の事前の準備作業
-------------------------------

Miniforgeをダウンロードする。

``` bash
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
```


``` bash
curl -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

conda clean --all
tar -zcf opt_miniconda3.tar.gz --owner=1000 --group=1000 -C / opt/miniconda3
```


### ユーザーadcの初期パスワードについて

- username: `adc`
- password: `adc-User`

Dockerfileで指定している初期パスワードのハッシュ値は、以下のようにして求めた。

```
$ perl -e 'print crypt("adc-User", "\$6\$ipsjdasadc"), "\n";'
$6$ipsjdasadc$j3jCv7RIO3CDs4dBWBsRHvLAjQe3tln.TdQdRVcBTM6fa3FL7.jz7hkCRxtoQxq4eX64twQRwqdvtqHBaQDmR/
```

docker build
------------

2種類のdocker imageを作成できる。

- `Dockerfile` ... 実行専用。サイズは下記"-dev"よりも小さめ
- `Dockerfile-dev` ... 実行に加えて、ソフトウェア開発もできる

``` bash
sudo docker build --tag ipsjdasadc/adc:20210713 .
sudo docker tag         ipsjdasadc/adc:20210713 ipsjdasadc/adc:latest

sudo docker build --tag ipsjdasadc/adc:20210713dev --file Dockerfile-dev .
```

### docker push to Docker Hub

```
sudo docker login  # when required
sudo docker push ipsjdasadc/adc:20200827
sudo docker push ipsjdasadc/adc:latest
sudo docker push ipsjdasadc/adc:20200827dev
```

Docker Hub  
https://hub.docker.com/repository/docker/ipsjdasadc/adc


### patch20200828

``` bash
sudo docker build --tag ipsjdasadc/adc:20200828 --file Dockerfile-patch20200828 .
sudo docker tag         ipsjdasadc/adc:20200828 ipsjdasadc/adc:latest
sudo docker push        ipsjdasadc/adc:20200828
sudo docker push        ipsjdasadc/adc:latest
```

### patch20200902

``` bash
sudo docker build --tag ipsjdasadc/adc:20200902 --file Dockerfile-patch20200902 --no-cache .
sudo docker tag         ipsjdasadc/adc:20200902 ipsjdasadc/adc:latest
sudo docker push        ipsjdasadc/adc:20200902
sudo docker push        ipsjdasadc/adc:latest
```

### patch20200907

``` bash
sudo docker build --tag ipsjdasadc/adc:20200907 --file Dockerfile-patch20200907 --no-cache .
sudo docker tag         ipsjdasadc/adc:20200907 ipsjdasadc/adc:latest
sudo docker push        ipsjdasadc/adc:20200907
sudo docker push        ipsjdasadc/adc:latest
```


### patch20200908

``` bash
sudo docker build --tag ipsjdasadc/adc:20200908 --file Dockerfile-patch20200908 --no-cache .
sudo docker tag         ipsjdasadc/adc:20200908 ipsjdasadc/adc:latest
sudo docker push        ipsjdasadc/adc:20200908
sudo docker push        ipsjdasadc/adc:latest
```


<a name="docker-run"></a>
docker run
----------


### カスタマイズ（必須）

#### 背景説明

dockerに関係なく一般に、serverを起動する前には、ファイル`adc2019/server/adcconfig.py`、`adc2019/server/adcusers.py`を生成しておく必要がある。

スクリプト`adc2019/scripts/04_server.sh`の初回実行時に、環境変数の値に基づいて、ファイル`adc2019/server/adcconfig.py`、`adc2019/server/adcusers.py`が生成される。

設定すべき環境変数は以下の通り。

- `ADC_YEAR`の値が、`adcconfig.py`の`YEAR`に設定される(default: `2020`)
- `ADC_SECRET_KEY`の値が、`adcconfig.py`の`SECRET_KEY`に設定される(default: `Change_this_secret_key!!`)
- `ADC_SALT`の値が、`adcconfig.py`の`SALT`に設定される(default: `Change_this_salt!!!`)
- `ADC_PASS_ADMIN`の値が、ユーザーadministratorのパスワードになる（ファイル`adcusers.py`に反映される。default: `Change_admin_password!!`）
- `ADC_PASS_USER`の値が、ファイル`adcusers.yaml`に反映される(default: `Change_user_password!!!`)。`adcusers.yaml`はserverの動作には何も影響せず、ユーザー登録作業のためのskeltonファイルのようなものである。初回起動時に、administrator以外の全ユーザーが、自動登録されるようなことはない。[adc2019/client-app/README.md](../client-app/README.md)にて説明している方法で、ユーザー登録をする必要がある

#### dockerコンテナ内でserverを起動する場合

ところが、このdockerコンテナでは、serverはsystemd経由で起動するため、unitファイル`/etc/systemd/system/adc-server.service`へ、dockerホスト側から環境変数を渡すのは困難である。そのため、コンテナ内でファイル`/etc/systemd/system/adc-server.service.d/env.conf`をマウントさせることにした。

参考用のファイル`env.sample.conf`をもとにして、以下のような内容のファイル`env.conf`を作成し、適切な値を設定する。`env.conf`は他人からアクセスされないように、厳重に管理する。

```
[Service]
Environment="ADC_YEAR=2020"
Environment="ADC_SECRET_KEY=__change_here__"
Environment="ADC_SALT=__change_here__"
Environment="ADC_PASS_ADMIN=__change_here__"
Environment="ADC_PASS_USER=__change_here__"
```

### dockerコンテナを実行する

シェルスクリプト`docker-run.sh`を用意してある。

`docker-run.sh`より抜粋

``` bash
docker run \
       --name adc2021 \
       -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
       -v /tmp/adc2021:/run \
       -v "${docker_dir}/env.conf":/etc/systemd/system/adc-server.service.d/env.conf \
       -p 30022:22 \
       -p 30080:8888 \
       ipsjdasadc/adc:latest
```

- コンテナのTCP/IP port 22 (SSH)が、ホスト側の30022に出てくる。必要に応じて変更すること
- コンテナのTCP/IP port 8888 (ADC server。`adc2019/scripts/04_server.sh`にて指定)が、ホスト側の30080に出てくる。必要に応じて変更すること
- ホストがUbuntuの場合、`/run`のvolume mountが必要だと[書かれていた](https://hub.docker.com/_/centos)。snapでインストールしたdockerの場合、実際には`/tmp/snap.docker/tmp/adc2021/`が使われるらしい。


### serverの動作確認

dockerホストから

``` bash
curl http://localhost:20080/api/version
```
実行例

```
$ curl http://localhost:20080/api/version
{"version": 2020}
```

### コンテナ内のユーザーアカウント

- ユーザーadcのパスワードは、上の方のperl〜の行に、わかりにくく書いてある8文字である
- ユーザーrootのパスワードは無効化されているが、SSH公開鍵認証を使ってrootでSSHログイン可能である
- ユーザーadcは、wheelグループに属しているため、sudoコマンドを実行可能である

### コンテナの中に入る

ユーザーadcとして

``` bash
sudo docker exec -it -u adc adc2020 bash
```

ユーザーrootとして

``` bash
sudo docker exec -it -u root adc2020 bash
```

### コンテナにSSHログインする

SSHは必須ではないが、Emacsのtrampのように、SSH経由でファイルを編集できるエディタがあるので、SSHは、あればあったで便利である。

``` bash
ssh -v -p 20022 adc@localhost
```

`$HOME/.ssh/config`に以下のようなエントリを追加すると便利である。

```
host adc2020
     HostName localhost
     port 20022
     User adc
```
こうしておくと、Emacs trampでは、`/ssh:adc@adc2020:`でアクセスできる。


コンテナ起動後、`/home/adc/.ssh/authorized_keys`、`/root/.ssh/authorized_keys`に、公開鍵を登録しておくと便利である。

### コンテナを止める

``` bash
sudo docker stop adc2020
```

### コンテナを削除する(コンテストのデータがすべて消える!!)

``` bash
sudo docker rm adc2020
```


### serverの状態を調べる／ログを見る


API server + httpd (gunicorn)のログ

``` bash
sudo docker exec -it -u root adc2020 systemctl status adc-server

sudo docker exec -it -u root adc2020 journalctl -xu adc-server
```

Google datastore emulatorのログ

``` bash
sudo docker exec -it -u root adc2020 systemctl status adc-datastore

sudo docker exec -it -u root adc2020 journalctl -xu adc-datastore
```




ウェブブラウザからserverにアクセスする
------------------------------------

dockerホスト上で実行しているウェブブラザなら以下のURLにアクセスする。

http://localhost:20080/


dockerホスト以外で実行しているウェブブラザなら、localhostではなく、dockerホストのアドレスを指定してアクセスする。

例 http://192.168.1.20:20080/

(備考) おそらくファイアウォールの許可ルールを追加しなくても、dockerのせいでアクセスできてしまうはず。



memo-20210713
-------------

```
docker run --name centos8 --rm -it centos:8 /bin/bash
```

```
docker cp google-cloud-sdk.repo centos8:/etc/yum.repos.d/
```


```
export CLOUDSDK_PYTHON=python3
export CLOUDSDK_GSUTIL_PYTHON=python3
export CLOUDSDK_BQ_PYTHON=python3


(cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;

yum clean all
yum update -y
yum install -y \
	    bash-completion \
	    git \
	    less \
	    openssh-server \
	    rsync \
	    sudo \
	    which \
		python39

yum -y install \
	    google-cloud-sdk \
	    google-cloud-sdk-datastore-emulator \
	    google-cloud-sdk-app-engine-python 

yum clean all

systemctl enable sshd && \
	systemctl enable systemd-user-sessions && \
	ln -s ../systemd-user-sessions.service /usr/lib/systemd/system/multi-user.target.wants/systemd-user-sessions.service
```
