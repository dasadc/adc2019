Docker image
=================

ADC serverをかんたんに起動できるようにするDocker iamgeについて説明する。

開発者以外の、serverを実行するだけの人は、[docker run](#docker-run)から読めばよい。

ADC参加者(`adccli`を実行するだけの人)も、このDocker imageを使って、`adccli`を実行できるが、Docker imageのサイズが大きすぎるため、あまりメリットは無いかもしれない。


事前の準備作業
--------------

### opt_miniconda3.tar.gzを作成する

`/opt/miniconda3/`に、Miniconda3がインストールされているとする。

``` bash
conda clean --all
tar -zcf opt_miniconda3.tar.gz --owner=1000 --group=1000 -C / opt/miniconda3
```

### ユーザーadcの初期パスワードについて

Dockerfileで指定している初期パスワードのハッシュ値は、以下のようにして求めた。

```
$ perl -e 'print crypt("adc-User", "\$6\$ipsjdasadc"), "\n";'
$6$ipsjdasadc$j3jCv7RIO3CDs4dBWBsRHvLAjQe3tln.TdQdRVcBTM6fa3FL7.jz7hkCRxtoQxq4eX64twQRwqdvtqHBaQDmR/
```

docker build
------------

2種類のdocker imageを作成できる

- `Dockerfile` ... 実行専用。サイズは下記"-dev"よりも小さめ
- `Dockerfile-dev` ... 実行に加えて、ソフトウェア開発もできる

``` bash
sudo docker build --tag ipsjdasadc/adc:20200827 .
sudo docker tag         ipsjdasadc/adc:20200827 ipsjdasadc/adc:latest

sudo docker build --tag ipsjdasadc/adc:20200827dev --file Dockerfile-dev .
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

#### dockerコンテナを起動するとき

ところが、このdockerコンテナでは、serverはsystemd経由で起動するため、unitファイル`/etc/systemd/system/adc-server.service`へ、dockerホスト側から環境変数を渡すのは困難である。そのため、コンテナ内にでファイル`/etc/systemd/system/adc-server.service.d/env.conf`をマウントさせることにした。

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
       --name adc2020 \
       -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
       -v /tmp/adc2020:/run \
       -v "${docker_dir}/env.conf":/etc/systemd/system/adc-server.service.d/env.conf \
       -p 20022:22 \
       -p 20080:8888 \
       ipsjdasadc/adc:latest
```

- コンテナのTCP/IP port 22 (SSH)が、ホスト側の20022に出てくる。必要に応じて変更すること
- コンテナのTCP/IP port 8888 (ADC server。`adc2019/scripts/04_server.sh`にて指定)が、ホスト側の20080に出てくる。必要に応じて変更すること
- ホストがUbuntuの場合、`/run`のvolume mountが必要だと[書かれていた](https://hub.docker.com/_/centos)。snapでインストールしたdockerのせいか、実際には`/tmp/snap.docker/tmp/adc2020/`が使われていた。


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


ウェブブラウザからserverにアクセスする
------------------------------------

dockerホスト上で実行しているウェブブラザなら以下のURLにアクセスする。

http://localhost:20080/


dockerホスト以外で実行しているウェブブラザなら、localhostではなく、dockerホストのアドレスを指定してアクセスする。

例 http://192.168.1.20:20080/

(備考) おそらくファイアウォールの許可ルールを追加しなくても、dockerのせいでアクセスできてしまうはず。
