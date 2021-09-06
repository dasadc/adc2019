(QUICK START) Dockerを使ってADC自動運営システムを実行する
=======================================================

手順は、以下の通り。

1. Dockerを使えるLinuxを持っていない場合 --> Dockerを使えるLinux仮想マシンを用意してあるので、それを使えるようにする
2. env.confファイルを作成する
3. docker-run.shファイルを作成する
4. docker-run.shを実行する
5. (初回のみ) adc-serverを再起動する
6. client-appや、adccliを使う


Linux仮想マシンを使えるようにする
-------------------------------

1. Oracle VirtualBoxをインストールする
2. Googleドライブに置いてあるファイルをダウンロードする
    - `Fedora CoreOS.ova`  (Linux仮想マシン)
	- `id_rsa` (仮想マシンにSSHログインするための鍵ファイル)
	- `dump-XXX.pickle`  (必要な場合のみ。ADC2021本番のデータをダンプしたファイル)
	- `env.conf` (dump-XXX.pickle使うために必要)
3. `Fedora CoreOS.ova`を、VirtualBoxでインポートする
4. インポートした仮想マシン「Fedora CoreOS」を実行する


### 仮想マシンFedora CoreOSの構成情報

- メモリ 4096MB
- 2 CPU
- SATA AHCI, 20GB, ホストI/Oキャッシュ (virtioにしたら、OSインストール時にエラーがでたため)
- ネットワークはNAT, virtio-net。HostからVMへのport forwardは以下の通り
    - 10022 --> 22
    - 30022 --> 30022
    - 30080 --> 30080
- インストールしたOSは、Fedora CoreOS。ユーザー名はcore、パスワードは無効で、SSHログインする


### ホストから、仮想マシンFedora CoreOSに、SSH loginする

いまどきのWindows 10は、WindowsのコマンドプロンプトかWindows PowerShellからSSHできる。

カレントディレクトリに鍵ファイル`id_rsa`があるときに、

``` bash
ssh -i ./id_rsa -l core -p 10022 127.0.0.1
```

`WARNING: REMOTE HOST IDENDIFICATION HAS CHANG!`

と表示された場合は、以下のコマンドを実行する

``` bash
ssh-keygen -f $HOME/.ssh/known_hosts" -R "[127.0.0.1]:10022"
```


### ホストから、仮想マシンFedora CoreOSに、SCPでファイルコピーする

``` bash
scp -i ./id_rsa env.conf dump*.pickle scp://core@127.0.0.1:10022
```



env.confを作成する
-----------------

GitHubからダウンロードして編集する。

``` bash
curl -O https://raw.githubusercontent.com/dasadc/adc2019/master/docker/env.sample.conf

cp env.sample.conf env.conf

vi env.conf
```

[README.md](README.md)の説明を読み、適切に変更する。


docker-run.shを作成する
----------------------

GitHubからダウンロードすればよい。

``` bash
curl -O https://raw.githubusercontent.com/dasadc/adc2019/master/docker/docker-run.sh
```


docker-run.shを実行する
-----------------------

``` bash
sudo /bin/sh docker-run.sh 
```

これで、Docker hubからDocker imageのダウンロードが始まる。数分程度の時間かかる。


(初回のみ) adc-serverを再起動する
-------------------------------

これは以下のissues #78のこと。

> dockerコンテナ版で、APIサーバが、初回、起動しそこねる #78
> https://github.com/dasadc/adc2019/issues/78


``` bash
sudo docker exec -it adc2021 systemctl status adc-server.service
```

を実行して、failedになっていたら、以下を実行する。


``` bash
sudo docker exec -it adc2021 systemctl restart adc-server.service
```

#### API serverへアクセスするテスト


``` bash
curl http://localhost:30080/api/version

curl http://localhost:30080/api/test_get
```


#### 自動運営システムのアカウント

上記の手順どおりに操作すれば、以下のアカウントが登録されているはずである。

- ユーザー: administrator, パスワード: "ADC_PASS_ADMIN"で指定したもの
- ユーザー: ADC-0, パスワード: "ADC_PASS_USER"で指定したもの



client-appや、adccliを使う
-------------------------


### client-appを使う

Host側でWebブラウザを実行して、以下のURLにアクセスする。

http://localhost:30080/


あとは、[client-appのドキュメント](../client-app/README.md)を参照してほしい。


### client "adccli"を使う

まずDockerコンテナの中に入る

``` bash
sudo docker exec -it -u adc adc2021 /bin/bash

```

環境設定する。

``` bash
conda activate adc2019dev

source ~/adc2019/client/env.sh 
```


#### loginする

``` bash
adccli --URL='http://localhost:8888/' --username='administrator' login
```

ログインできたことを確認する

``` bash
adccli whoami
```

あとは、[adccliのドキュメント](../client/README.md)を参照してほしい。
