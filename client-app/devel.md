ADC2022 Web application (client-app)
====================================

**(注意)** このドキュメントは、まだ、アルゴリズムデザインコンテスト2022年向けの更新漏れがあり、古い情報が書かれている可能性がある。


初期設定
--------

[Anaconda(Miniconda)の環境を使う](../devel.md#miniconda)

ADC201x当時使用していたUbuntu 18.04では、aptでインストールされるnode.jsが古かったので、Anacondaのnpmを使っていた。


#### 2022年7月5日時点でのメモ

- [Node.js](https://nodejs.org/ja/about/releases/)のLTSは16
- conda-forgeのnodejsパッケージのバージョンは、16.14.2だった
- [ngx-file-drop](https://www.npmjs.com/package/ngx-file-drop)は、Angular 14に対応している
- [Flask](https://flask.palletsprojects.com/en/2.1.x/)のバージョンが、2.1.2。conda-forgeでも同じ

#### 2021年7月13日時点でのメモ

- [../devel.md](../devel.md)の説明にあるように、Anaconda環境adc2019devを使用する。
    - conda-forgeからは、node.js 14.17.1がインストールされていた。version番号が奇数はLTSではないそうなので、14を指定している。
- なぜか`node_modules`が腐ったり、ソフトウェアのバージョンを上げたかったので、ファイル`package.json`の`dependencies`と`devDependencies`を削除して、ファイル`package-lock.json`を削除して、やり直した。
    - 今の[ngx-file-drop ](https://www.npmjs.com/package/ngx-file-drop)は、Angular 11に対応している

``` bash
npm init
npm install \
  ngx-file-drop \
  typescript \
  http-server \
  js-yaml \
  @angular/cli \
  @angular/core \
  @angular/common \
  @angular-devkit/build-angular \
  @angular/platform-browser-dynamic \
  @angular/platform-browser \
  @angular/router \
  @angular/forms \
  @angular/compiler-cli \
  @angular/compiler \
  d3@5 @types/d3@5.16.4 \
  zone.js@0.11.4
```

- `yaml.safeLoad()`が無くなった。`yaml.load()`にすればよい。


#### 2020年8月時点でのメモ

- node.js 10.13.0がインストールされた。
- angularは、10.0.6がインストールされてしまうが、ngx-file-dropが、angular 10に対応していないらしいので、angular 9を明示指定してインストールする。

#### 一番最初のとき

``` bash
npm init
npm install @angular/cli@9
npm install typescript
npm install http-server
npm install ngx-file-drop --save
npm install js-yaml --save
npm install --save-dev @angular/core@9
npm install --save-dev zone.js@~0.10.3
npm install --save-dev @angular/common@9
```


#### 2回目以降

``` bash
npm install
```

実行する
---------

### google datastore emulatorを実行しておく

``` bash
../scripts/00_datastore.sh
```

### ADCのAPI serverを実行しておく

port番号は8888を使う(以下で説明する[proxy.conf.json](proxy.conf.json)で指定されているため)。

``` bash
../scripts/04_server.sh
```

### (frontend) Angular, development serverを実行する

``` bash
$(npm bin)/ng serve --proxy-config proxy.conf.json --live-reload --watch --poll 9999 --host 0.0.0.0
または
npm run test-run
```

http://localhost:4200/

#### (Trouble shooting) ウェブブラウザのページに"Invalid Host header"とだけ表示されるとき

ウェブブラウザ(http client)が送ってきた、HTTPのHostヘッダが違うので、Angularの開発用httpサーバが拒否しているのだと思われる。たとえば、routerで、NATのような中継をやっていて、ウェブブラウザで指定したホスト名がlocalhostではないとき、そうなる。

`--disable-host-check`を追加する。

```
$(npm bin)/ng serve --proxy-config proxy.conf.json --live-reload --watch --poll 9999  --host 0.0.0.0 --disable-host-check
```

#### (Trouble shooting) npm installで、`fibers@5.0.0`がエラーと言われる

g++がインストールされていなかったのが原因だった。

`sudo apt install g++`

#### (Trouble shooting) `npm run build`したとき、意味不明なエラーがでた

ディレクトリ`node_modules`を消して、`npm install`からやり直したら、不思議なことに、直った。


### deploy前のテスト実行方法

ビルドする。

```
cd client-app/
$(npm bin)/ng build --prod --base-href=/static/app/index.html --output-path=../server/static/app/
または
npm run build
```

datastore emulartorを実行する。
スクリプト[00_datastore.sh](../scripts/00_datastore.sh)が使える。

serverを実行する。 
スクリプト[99_server.sh](../scripts/99_server.sh)が使える。`./99_server.sh -h`で簡単なヘルプを表示する。

手動でserverを実行する場合

```
cd ../server/
gunicorn main:app
ポート番号8000がすでに使われていて変更したいとき
gunicorn -b :28000 --access-logfile '-' main:app
```

- http://127.0.0.1:8000/static/app/index.html   # `99_server.sh`
- http://127.0.0.1:28000/static/app/index.html

もしも、開発中のAPI serverのdevelopment serverが動き続けているなら、それも使える。

- http://127.0.0.1:4280/static/app/index.html


### GitHub Pagesへdeployする

client-appの「Edit」機能（通称「テトリス・エディタ」）を、GitHub Pagesのhttps://dasadc.github.io/static/app/index.html#/edit から実行できるようにしている。

client-appのファイルをコピーする。

``` bash
    # ファイルコピー前の確認
rsync -navpr --delete ../server/static/app/ ../../dasadc.github.io/static/app/
    # 実際にファイルコピーする
rsync  -avpr --delete ../server/static/app/ ../../dasadc.github.io/static/app/
```

そのあと、git commit、git pushする


### (TIP) GitHub Pages経由でWebアプリを使いつつ、Google AppEngine上で実行中のAPIサーバを使う

My Accountメニューの、「(BETA test) API server」 のテキストボックスに`https://das-adc.appspot.com`と入力して、set API serverボタンをクリックする。


### Google App Engineへdeployする

serverをdeployすればよい。client-appのファイルも同時にアップロードされる。

``` bash
cd ../server/
gcloud app deploy --project=das-adc
```


カスタマイズ
------------

### 年号を変えたい

年号は、サーバー側で設定されているので、サーバーの設定ファイルを修正する。

ファイル `adc2019/server/adcconfig.py`

``` python
YEAR = 2020
```

### Helpメニューのリンク先URLを変えたい

1. デフォルトは、`src/app/adc.service.ts`にハードコーディングされている。
2. サーバーからURLを取得するようになっているので、サーバーの設定ファイルを修正する。

ファイル `adc2019/server/adcconfig.py`

``` python
URL_CLIENT_APP_README = 'https://github.com/dasadc/adc2019/blob/master/client-app/README.md'
```


d3.js
-----

https://medium.com/better-programming/reactive-charts-in-angular-8-using-d3-4550bb0b4255

npm info d3 versions
npm install d3@5 --save

> d3@5.16.0 がインストールされた

Trouble shootings
-----------------

### google.auth.exceptions.DefaultCredentialsError

`cd ../server/; gunicorn main:app"` したときに、エラー

```
  File "/opt/miniforge3/envs/adc2019dev/lib/python3.9/site-packages/google/auth/_default.py", line 483, in default
    raise exceptions.DefaultCredentialsError(_HELP_MESSAGE)
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials. Please set GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application. For more information, please see https://cloud.google.com/docs/authentication/getting-started
```


`$(gcloud beta emulators datastore --data-dir "${datastore_dir}" env-init)`  
を実行して、環境変数`DATASTORE_*`を設定しておく必要がある。
