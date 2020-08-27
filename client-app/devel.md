ADC2019 Web application (client-app)
====================================


初期設定
--------

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

### (frontend) Angular, development server

```
$(npm bin)/ng serve --proxy-config proxy.conf.json --live-reload --watch --poll 9999
または
npm run test-run
```

http://localhost:4200/


### deploy前のテスト実行方法

ビルドする。

```
cd client-app/
$(npm bin)/ng build --prod --base-href=/static/app/index.html --output-path=../server/static/app/
または
npm run build
```

実行する。

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
