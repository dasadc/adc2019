Docker image
=================


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

``` bash
sudo docker build --tag ipsjdasadc/adc:20200826 .
```

### docker push to Docker Hub

```
sudo docker login
sudo docker push ipsjdasadc/adc:20200826
```

Docker Hub  
https://hub.docker.com/repository/docker/ipsjdasadc/adc


docker run
----------

参考 https://hub.docker.com/_/centos

``` bash
sudo docker run -it -u root --name adc2020 -v /sys/fs/cgroup:/sys/fs/cgroup:ro -v /tmp/adc2020:/run -p 20022:22 ipsjdasadc/adc:20200826
```
`/tmp/snap.docker/tmp/adc2020/`が使われていた。

### コンテナにSSHログインする

SSHは必須ではないが、Emacsのtrampのように、SSH経由でファイルを編集できるエディタがあるので、あればあったで便利である。

``` bash
ssh -v -p 20022 adc@localhost
```

初期パスワードは、上の方に、わかりにくくして書いてある。

#### `$HOME/.ssh/config`の記述例

```
host adc2020
     HostName localhost
     port 20022
     User adc
```

Emacs trampでは、`/ssh:adc@adc2020:`でアクセス。

datastore emulator
------------------

``` bash
/home/adc/adc2019/scripts/00_datastore.sh >/tmp/datastore.log 2>&1 &
```
