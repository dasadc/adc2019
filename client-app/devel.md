ADC2019 Web application (client-app)
====================================


初期設定
--------

[Anaconda(Miniconda)の環境を使う](../devel.md#miniconda)


Ubuntu 18.04では、aptでインストールされるnode.jsが古い。anacondaのnpmを使う。

```
conda install nodejs
```

2020年8月時点でのメモ

- node.js 10.13.0がインストールされた。
- angularは、10.0.6がインストールされてしまうが、ngx-file-dropが、angular 10に対応していないらしいので、angular 9を明示指定してインストールする。

一番最初のとき

```
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


2回目以降

```
npm install
```

実行する
---------

### google datastore emulatorを実行しておく

```
../scripts/00_datastore.sh
```

### ADCのAPI serverを実行しておく

port番号は8888を使う(以下の`proxy.conf.json`で指定されているため)。

```
../scripts/04_server.sh
```

### (frontend) Angular, development serverを実行する

```
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

実行する。 ---> スクリプト[99_server.sh](../scripts/99_server.sh)が使える。

```
cd ../server/
gunicorn main:app
ポート番号8000がすでに使われていて変更したいとき
gunicorn -b :28000 --access-logfile '-' main:app
```

- http://127.0.0.1:8000/static/app/index.html
- http://127.0.0.1:28000/static/app/index.html

もしも、開発中のAPI serverのdevelopment serverが動き続けているなら、それも使える。

- http://127.0.0.1:4280/static/app/index.html


カスタマイズ
------------

### 年号を変えたい

年号は、サーバー側で設定されているので、サーバーの設定ファイルを修正する。

ファイル `adc2019/server/adcconfig.py`

``` python
YEAR = 2020
```


d3.js
-----

https://medium.com/better-programming/reactive-charts-in-angular-8-using-d3-4550bb0b4255

npm info d3 versions
npm install d3@5 --save

> d3@5.16.0 がインストールされた

