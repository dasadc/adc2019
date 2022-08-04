アルゴリズムデザインコンテスト(ADC)の自動運用システムの利用方法 (client)
=====================================================================

**(注意)** ~~このドキュメントは、まだ、アルゴリズムデザインコンテスト2021年向けの更新漏れがあり、古い情報が書かれている可能性があります。~~


DAシンポジウム2021にて開催されるアルゴリズムデザインコンテスト(ADC)では、クライアント・サーバ方式による、自動運用システムを導入します。

問題データの配布、回答データの提出、スコア計算、スコア表示などが、すべてネットワーク経由で自動的に行われます。

このドキュメントでは、コマンドライン環境からサーバにアクセスする方法について説明しています。それとは別に、[ウェブアプリ](../client-app/README.md)もあります。おそらく、ウェブアプリのほうが、かんたんに使えると思います。


利用スタイル
-----------

3通りの使い方ができます。

1. [専用ツールadccliを経由して使う](#adccli)
   - 無人処理（自動処理）に向いています。
2. [curlを経由して使う](#curl)
   - 無人処理（自動処理）に向いています。
   - APIを直接呼び出すプログラムを自作する場合に、参考にしてください。
   - もっぱら、システム開発時の動作確認用手段として、使っています。
   - この部分のドキュメントが更新が遅れています。現在はAPIが変わっている可能性があります。
3. [Webブラウザを使う](#web-browser)
   - 人力で処理する場合に向いてます。
   - これまでのADCでは、これが一番よく使われています。



(1)adccliと(2)curlで必要なソフトウェア
-------------------------------------

以下のどちらかをご用意ください。

|名称            |参考                    |
|----------------|----------------------- |
|Python 3.9以降  |https://www.python.org/ |
|curl            |http://curl.haxx.se/    |

pythonとcurlは、LinuxやMacなどでは、ほぼ標準でインストールされています。Windowsでは、申し訳ありませんが各自でインストールをお願いします。

Windows/Mac/Linuxともに、[Miniforgeがおすすめです](../devel.md#miniforge)。



### APIの利用

ADCのサービスは、Web APIによって提供されています。そのため、自作プログラムからAPIを使って、ADCのサービスを利用することも可能です。

- APIの詳細は、[curlを用いて確認](#curl)できます。
- [クライアントライブラリ](#adcclient)を利用することもできます。※[adccli](#adccli)は、そのサンプル実装です。

### 2021年版の変更

- Roundカウンタという概念が増えました。
- 2021年ルールに合わせて修正しました。

### 2019年版の変更

このドキュメントは旧版をベースに記載されているため、クッキーを使ってAPIを呼び出す方法を示していますが、現在、クッキーを使わずに、アクセストークンを使って認証を行う機能が実装されています。

アクセストークンは、ログイン成功時に取得できます。ログインしなおすたびに、アクセストークンは新規生成されます。

adcclient.pyでは、ユーザー名とアクセストークンをそれぞれ環境変数`ADC_USER`、`ADC_TOKEN`にセットしてAPIを呼び出せます。

curlなどで、HTTPプロトコルでアクセスするときは、`ADC-USER`ヘッダ、`ADC-TOKEN`ヘッダを付加します。

``` bash
curl -H "ADC-USER: administrator" -H "ADC-TOKEN: acbfacf7dbe922d84c58aa8314ac6e98324639106d3bddf9808f633894a20cd6" -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:4200/api/whoami
```


入出力データのフォーマットがまちまちだったのが、JSONで統一しています。ウェブブラウザからアクセスしたときのための、HTMLを出力する機能は、すべて廃止しました。
ウェブアプリ部分は、Angularを使って、新規に作り直しました。

従来、Python 2.7系で開発されていましたが、Python 3系へ移行しました。ほぼ全面的に書き換えたため、Python 2.7では、もう動きません。


注意事項
--------

インターネット上のサイト`das-adc.appspot.com`は、Google App EngineにてホスティングされたWebサービスです。

- Google App Engineの利用料金を節約するために、大量アクセスによる負荷テストのようなことは、ご遠慮ください。



ADCサービスを利用するためのツール
-------------------------------

[adccliを使う方法](#adccli)(要 Python 3.6以降)と、[curlを使う方法](#curl)(要 curl)の2通りを紹介します。

<a name="adccli"></a>
### コマンドラインツール adccli （クライアントのサンプル実装）

ADCサービスを利用するためのコマンドラインツール`adccli`を用意しました。Python 3.6以降で実行できます。

#### adccliの入手

1. `git clone -b adc2021-yt https://github.com/dasadc/adc2019.git` を実行します。
2. `adc2019/client/`フォルダーにファイル一式が入ってます。



以下の環境で、ある程度の動作確認を行っています。

- Ubuntu 20.04.2 LTS x86_64  (Miniforge Python 3.9.4)
- CentOS 7 x86_64  (Python 3.6.8)

このツールについての、ご意見、改良案、パッチなど、[フィードバックを歓迎します](https://github.com/dasadc/adc2019/issues)。


#### 実行のための環境設定

実行ファイル`adccli`が存在するディレクトリを、環境変数`PATH`に追加してください。

シェルスクリプト[env.sh](env.sh)を参考にしてください。
`source $(dir)/adc2019/client/env.sh` のように設定できます。


#### おもなオプション

`adccli --help`で、かんたんなヘルプメッセージが表示されます。

```
$ ./adccli --help
usage: adccli [-h] [--debug] [--verbose] [-c FILE] [-u USERNAME]
              [--alt-username ALT_USERNAME] [-p PASSWORD] [-U URL] [-o FILE]
              cmd [arg [arg ...]]

DA Symposium 2020 Algorithm Design Contest, Command Line Interface tool

positional arguments:
  cmd                   "adccli help" will show help of cmd.
  arg

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug mode
  --verbose             verbose message
  -c FILE, --config FILE
                        config file (default: /home/USER/adcclient.json)
  -u USERNAME, --username USERNAME
                        set username (default: administrator)
  --alt-username ALT_USERNAME
                        set alternative username. admin only
  -p PASSWORD, --password PASSWORD
                        set password
  -U URL, --URL URL     set server URL (default: http://127.0.0.1:8888/)
  -o FILE, --output FILE
                        output file name (default: None)
```


サブコマンド`cmd`のヘルプが、`adccli help`で表示されます。

以下はadccli helpの実行例です。実際の実行結果とは異なる場合があります。

```
$ adccli help

  login
  logout
  version
  whoami
  password [NEWPASSWORD]
  get-user-list
  get-user [USERNAME ...]
  get-q [NUMBER ...]
  get-q-all                   # all-in-one Zip archive
  put-a NUMBER FILENAME [replace-A-number]
  put-a-info NUMBER CPU_SEC MEM_BYTE [MISC_TEXT]
  get-a-info [NUMBER]
  delete-a-info NUMBER
  get-a [NUMBER ...]          # test mode only, when NUMBER specified
  delete-a [NUMBER ...]       # test mode only
  get-user-q [NUMBER ...]
  post-user-q NUMBER FILENAME
  put-user-q NUMBER FILENAME
  delete-user-q [NUMBER ...]
  check-q FILENAME
  put-user-alive MSG
  get-user-log [NUMBER (seconds|days)]
  delete-user-log [NUMBER (seconds|days)]
  score
  score-dump
  get-root
admin command:
  convert-users FILENAME_IN.py FILENAME_OUT.yaml
  create-user USERNAME PASSWORD DISPLAYNAME UID GID
  create-users FILENAME.(py|yaml)
  delete-user [USERNAME ...]
  get-admin-q-all
  get-admin-q-list
  put-admin-q-list
  delete-admin-q-list
  delete-admin-q-all
  get-admin-a-all
  delete-admin-a-all
  get-log [NUMBER (seconds|days)]
  delete-log [NUMBER (seconds|days)]
  timekeeper-enabled [0|1]                            # Get/Set enabled flag
  timekeeper-state [init|im0|Qup|im1|Aup|im2]         # Get/Set state
  timekeeper-round [1|2]                              # Get/Set round counter
  timekeeper [[0|1] [init|im0|Qup|im1|Aup|im2] [1|2]] # Get/Set all at once
  test-mode [True|False]
  view-score-mode [True|False]
  log-to-datastore [True|False]
```

#### 設定保存ファイル adcclient.json

adccliの設定を保存するファイル`adcclient.json`が、ホームディレクトリに自動的に作成されます。

- 設定保存ファイルのパス名は、環境変数`ADCCLIENT_JSON`や、コマンドライン引数`adccli --config FILE`で指定することも可能です（引数`--config`が優先）。

オプション`--username`や`--URL`で指定した値は、設定ファイルに保存され、以後、デフォルト値として利用されるようになります。

Webのクッキーもこの設定ファイルに保存されます。loginに成功した後は、ログイン状態が継続します。設定ファイルにパスワードは保存されません。


<a name="adcclient"></a>
#### クライアント・ライブラリ adcclient.py

ADCサービスのAPIを呼び出すためのライブラリです。

adccliを使わずに、adcclient.py経由で、自作プログラムからWeb APIを利用することも容易です。


#### プロキシーサーバ経由での利用

環境変数`http_proxy`、`no_proxy`を参照して、プロキシーサーバ経由で動作します。


## adccliを使ってADCサービスを利用する

### loginする

    adccli --URL='https://das-adc.appspot.com/' --username='USERNAME' --password='PASSWORD' login

- `--password`オプションを指定しなかった場合、その場でパスワード入力が要求されます。

### logoutする

    adccli logout

### loginしたときのユーザー名を確認する

    adccli whoami

### パスワードを変更する

    adccli password
    adccli password NEW-PASSWORD
    adccli --password='OLD-PASSWORD' password
    adccli --password='OLD-PASSWORD' password NEW-PASSWORD

- `--password`オプションを指定しなかった場合、その場でパスワード入力が要求されます。
- `NEW-PASSWORD`を指定しなかった場合、その場でパスワード入力が要求されます。

### クライアントのステータスをサーバへ報告する

    adccli put-user-alive メッセージ

- `メッセージ`には、今何をやっているか、などを文字列で指定します。
- これはクライアントの死活監視のための機能です。コンテスト本番中は、最長3分に1回間隔で、サーバと通信することを推奨します。サーバは、クライアントからのアクセスが無い時間がつづくと、クライアントに異常が発生しているのでは？と認識します。
  - サーバからクライアントへ、ステータスを問い合わせる機能は、今のところありません。

実行例

```
$ adccli put-user-alive 'I am now working on Q7.'
OK
```

### アクセスログを確認する (2021-08-24時点ではログ記録は無効化されている)

ユーザが行ったアクセスログを表示します。
サーバ側の設定により（データストア使用量を削減することで、クラウド利用料を節約するため）、ログが記録されていない場合があり、そのときは、このコマンドでログは見られません。

    adccli get-user-log

実行例

```
$ adccli get-user-log
/user/test-01/log
2015-07-17 09:02:51 JST+0900 test-01: GET /user/test-01/log
2015-07-17 09:02:18 JST+0900 test-01: alive: I am now working on Q7.
2015-07-17 08:57:53 JST+0900 test-01: GET /user/test-01/log
2015-07-17 08:57:38 JST+0900 test-01: GET /whoami
2015-07-16 18:10:22 JST+0900 test-01: DELETE /user/test-01/log
2015-07-16 18:10:05 JST+0900 test-01: GET /user/test-01/log
2015-07-16 18:10:00 JST+0900 test-01: POST /login
```

期間を指定することもできます。

    adccli get-user-log 数値 単位

- 数値は、正の整数を指定します。
- 単位は、`seconds`か`days`です。単数でも`s`がつきます。
- たとえば過去2日のログを見たいときは、`adccli get-user-log 2 days`です。

<a name="qcheck"></a>
### 問題ファイルの書式をチェックする

自作問題のファイルの内容に、誤りがないか、簡易チェックを行うことができます。

    adccli check-q ファイル名

- ファイルがサーバにアップロードされ、内容のチェックが行われます
- ファイルはサーバには保存されません

[詳細](#curl-qcheck)


### テスト期間中と、コンテスト開始前の準備期間中に実行可能な機能

#### 自作問題をアップロードする

    adccli post-user-q 問題番号 ファイル名

- 問題番号は、1、2、3のいずれかを指定してください。
- すでにその問題番号でアプロード済みの場合は、エラーになります。`delete-user-q`で削除してから`post-user-q`するか、または、`put-user-q`してください。

#### アップロード済の自作問題の一覧リストを見る

    adccli get-user-q

[参考](#get-user-q)

#### 自作問題をダウンロードする

    adccli get-user-q 問題番号

- ファイルに保存されます。

#### 自作問題を削除する

    adccli delete-user-q 問題番号

#### 自作問題を差し換える

    adccli put-user-q 問題番号 ファイル名

- これは、すでにアップロード済みの問題を差し替えるコマンドです。`delete-user-q`で削除してから`post-user-q`で新規登録しても構いません。

[参考](#put-user-q)

### テスト期間中と、コンテスト開始後に実行可能な機能

#### 出題問題の番号を確認する

コンテストがスタートしたら、まず、出題された問題番号の一覧リストを取得してください。

    adccli get-q

ファイルに出力したい場合

    adccli --output ファイル名 get-q


[参考](#GETQ)


<a name="get-q-all"></a>
#### 出題問題をZipアーカイブ形式でまとめてダウンロードする

ファイル名`Q-all.zip`として、ダウンロードできます。

    adccli get-q-all

Zipファイルのファイル名に出力したい場合

    adccli --output ファイル名 get-q-all


#### 出題問題をダウンロードする

出題番号を指定して、出題された問題データをダウンロードしてください。

    adccli get-q 出題番号

- `出題番号`は、[出題問題](#GETQ)の整数値を指定します。`Q`はつけません。

ファイルに出力したい場合

    adccli --output ファイル名 get-q 出題番号


#### 回答をアップロードする

    adccli put-a 出題番号 ファイル名

自動運営システム開発時の動作テスト用として、オプション引数`replace-A-number`がある。

    adccli put-a 出題番号 ファイル名 replace-A-number

この場合、ファイル中に記述されている出題番号(`A5`のようなテキスト)を、コマンドライン引数で指定した出題番号で置き換えることができる(ファイルが書き換えられるのではなく、サーバへの送信時に置換する)。


[参考](#put-a)


<a name="adccli-put-a-info"></a>
#### 回答の補足情報をアップロードする (ADC2021ではdeprecated)

回答を得るまでにかかった、計算時間（単位: 秒）、使用メモリ量（単位: Byte）、その他（文字列）を、アップロードします。

    adccli put-a-info 出題番号 CPU_SEC MEM_BYTE MISC_TEXT

- これ(put-a-info)を実行する前に、回答をアップロード(put-a)しておく必要があります。
- 出題番号は、数値。`Q`も`A`もつけない
- `CPU_SEC`は、実数。小数も可
- `MEM_BYTE`は、整数
- `MISC_TEXT`は、任意の文字列

実行例

    adccli put-a-info 2 10.234 56789 test


[参考](#put-a-info)

### テスト期間中に実行可能な機能

#### アップロード済の回答データの一覧リストを見る

    adccli get-a

[参考](#GETA)

#### アップロード済の回答データをダウンロードする

    adccli get-a 出題番号

- `出題番号`は、[回答済の出題問題](#GETA)の整数値を指定します。`A`はつけません。

[参考](#get-a-num)

#### アップロード済の回答データを削除する

    adccli delete-a 出題番号

- `出題番号`は、[回答済の出題問題](#GETA)の整数値を指定します。`A`はつけません。
- 回答の補足情報も同時に削除されます。

[参考](#delete-a)


#### 回答の補足情報をダウンロードする

    adccli get-a-info 出題番号

- 出題番号に0を指定するか、もしくはつけない場合、すべての回答補足情報がダウンロードされます。

実行例

    $ adccli get-a-info 2
    GET A2 info 1
    mem_byte: 56789
    cpu_sec: 10.234
    result: i= 0
    check_1 True
    check_2 True
    check_3 True
    check_4 True
    check_5 True
    check_6 True
    judges =  [True]
    Get 3.141592 point [DUMMY]
    
    misc_text: test
    anum: 2

- 1行めの`GET A2 info 1`の`A2`は出題番号、最後の`1`はダウンロードしたデータ数（通常は1）
- 2行め以降は、順不同
  - `anum`は、出題番号
  - `mem_byte`、`cpu_sec`、`misc_textは`、[`put-a-info`](#adccli-put-a-info)で指定した値
  - `result`は、採点結果。改行コードを含む


[参考](#get-a-info)

#### 回答の補足情報を削除する

    adccli delete-a-info 出題番号

- 出題番号に0を指定するか、もしくはつけない場合、すべての回答補足情報が削除されます。

### スコアを見る

    adccli score

TBD

<a name="curl"></a>
## curlを使ってADCサービスを利用する

adccliは実行のためにPythonの実行環境が必要となりますが、その代りに、curl単体でも、ADCサービスを利用できます。

また、自作プログラムからADCサービスAPIを直接呼び出したい方も、参考にしてください。curlに`-v`オプションをつけて実行すると、より詳細な情報が得られます。

ちなみに、das-adc.appspot.comへは、httpでもhttpsでもアクセスできるようになっています。

### loginする

2021年方式

コマンドの書式

``` bash
curl -H "Accept: application/json" -H "Content-Type: application/json" -X POST -d '{"username":"USERNAME", "password":"PASSWORD"}' http://localhost:4200/api/login
```

具体的には

``` bash
curl -H "Accept: application/json" -H "Content-Type: application/json" -X POST -d '{"username":"test-06", "password":"cagI....8"}' http://localhost:4200/api/login
```

以下のような結果が返ってきます。

``` json
{"msg": "login OK", "token": "dada66aa3eec5933f82582f83715d5771684fddef9c605a39cf898c515f7f37a"}
```

このtokenを使って、API実行をテストします。API '/api/whoami'は、ユーザー名を返します。

``` bash
curl -H "ADC-USER: test-06" -H "ADC-TOKEN: dada66aa3eec5933f82582f83715d5771684fddef9c605a39cf898c515f7f37a" -H "Accept: application/json" -H "Content-Type: application/json" http://localhost:4200/api/whoami
```

以下のような結果が返ってきます。

``` json
{"msg": "test-06"}
```

以下、クッキーを使った旧方式。※ 以下の記述は、2021年方式に修正されていないようなので注意!!

    curl -H "Accept: application/json" -H "Content-Type: application/json" -X POST -d '{"username":"USERNAME", "password":"PASSWORD"}' --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/login

- `USERNAME`と`PASSWORD`の部分を、実際のアカウントのものへ差し換えてください。
- `CURL_COOKIES`の部分では、クッキーを保存するファイル名を指定します。他人から見られないように、アクセス制限をしてください（例: `chmod 600 CURL_COOKIES`）。

loginに成功した場合、以下のような応答が来ます。JSON形式になっています。

    {"msg": "login OK"}

### logoutする

以下のどちらでもかまいません。

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -X POST -d 'dummy' https://das-adc.appspot.com/logout

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/logout

### loginしたときのユーザー名を確認する

HTML形式で応答を得る方法

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/whoami

JSON形式で応答を得る方法

    curl -H "Accept: application/json" -H "Content-Type: application/json" --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/whoami

### パスワードを変更する

    curl -H "Accept: application/json" -H "Content-Type: application/json" -X POST -d '{"password_old":"PASSWORD", "password_new1":"NEW-PASSWORD", "password_new2":"NEW-PASSWORD"}' --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/user/USERNAME/password

- パスワード変更する前に、先にloginしてください。
- `USERNAME`と`PASSWORD`の部分を、実際のアカウントのものへ差し換えてください。
- `PASSWORD`は現在のパスワード、`NEW-PASSWORD`は新しいパスワードです。

### クライアントのステータスをサーバへ報告する

    curl -H "Content-Type: text/plain" --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -X PUT --data 'STATUS' https://das-adc.appspot.com/user/USERNAME/alive

- `STATUS`には、今何をやっているか、などを文字列で指定します。たとえば'CPU: 98.5%\nMEM: 1344M'など。
- `USERNAME`は、アカウントのユーザー名を指定してください


### アクセスログを確認する

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/user/USERNAME/log

- `USERNAME`は、アカウントのユーザー名を指定してください
- 結果は、JSON形式で返ってきます。

期間を指定することもできます。

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/user/USERNAME/log/KEY/VALUE

- KEYは、`seconds`か`days`です。単数でも`s`がつきます。
- VALUEは、正の整数です。
- たとえば過去2日のログを見たいときは、`.../days/2`となります。


<a name="curl-qcheck"></a>
### 問題ファイルの書式をチェックする

自作問題のファイルの内容に、誤りがないか、簡易チェックを行うことができます。

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES  -H "Content-Type: text/plain" --upload-file QFILENAME https://das-adc.appspot.com/Qcheck

- QFILENAMEは、問題ファイルのファイル名を指定してください
- ファイルがサーバにアップロードされ、内容のチェックが行われます
- ファイルはサーバには保存されません

実行例 1
[正常なファイル](support/NL_Q01.txt)

```
OK
----------------------------------------
SIZE 10X10
LINE_NUM 7
LINE#1 (8,1)-(8,8)
LINE#2 (2,4)-(2,9)
LINE#3 (7,6)-(0,9)
LINE#4 (6,6)-(0,8)
LINE#5 (9,3)-(5,6)
LINE#6 (1,1)-(7,2)
LINE#7 (1,2)-(6,2)
----------------------------------------
```

実行例 2
[異常があるファイル](support/NL_Q01.bad2.txt)

```
NG
----------------------------------------
SIZE 10X10
LINE_NUM 7
LINE#1 (8,1)-(8,8)
LINE#2 (2,4)-(2,9)
LINE#3 (7,6)-(0,9)
LINE#4 (6,6)-(0,8)
LINE#5 (9,3)-(5,6)
LINE#6 (1,1)-(7,2)
LINE#6 (1,2)-(6,2)
----------------------------------------
ERROR: duplicated line number: LINE#6 (1,2)-(6,2)
ERROR: LINE#7 not found
```




### テスト期間中と、コンテスト開始前の準備期間中に実行可能な機能

#### 自作問題をアップロードする

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES --form "qfile=@QFILENAME" https://das-adc.appspot.com/user/USERNAME/Q/QNUMBER

- QFILENAMEは、問題ファイルのファイル名を指定してください
- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、1、2、3のいずれかを指定してください。

<a name="get-user-q"></a>
#### アップロード済の自作問題の一覧リストを見る

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/user/USERNAME/Q

- USERNAMEは、アカウントのユーザー名を指定してください

応答の例

    Q1 SIZE 10X10 LINE_NUM 7 (test-01)
    Q2 SIZE 10X10 LINE_NUM 10 (test-01)
    Q3 SIZE 10X18 LINE_NUM 9 (test-01)

意味は以下の通りです。

    Q{問題番号} SIZE {盤の大きさ} LINE_NUM {線の本数} ({ユーザー名})

#### 自作問題をダウンロードする

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/user/USERNAME/Q/QNUMBER

- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、1、2、3のいずれかを指定してください。

ファイルに保存したい場合は、curlの`-o`オプションを使用します。

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/user/USERNAME/Q/QNUMBER -o FILENAME


#### 自作問題を削除する

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -X DELETE https://das-adc.appspot.com/user/USERNAME/Q/QNUMBER

- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、1、2、3のいずれかを指定してください。


<a name="put-user-q"></a>
#### 自作問題を差し換える

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -H "Content-Type: text/plain" --upload-file QFILENAME https://das-adc.appspot.com/user/USERNAME/Q/QNUMBER

- QFILENAMEは、問題ファイルのファイル名を指定してください
- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、1、2、3のいずれかを指定してください。

QNUMBERの問題がすでにアップロード済の場合に、問題データが差し換えられます。新規登録はしません。

差し換えに成功したときの応答メッセージの例

    PUT OK update 1 {USERNAME} Q{QNUMBER} size ***x*** line_num ***

差し換えなかった（新規登録もしない）ときの応答メッセージの例

    PUT OK update 0 {USERNAME} Q{QNUMBER} size ***x*** line_num ***



### テスト期間中と、コンテスト開始後に実行可能な機能

<a name="GETQ"></a>
#### 出題問題の番号を確認する

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/Q

以下のような応答が返ってきます。

    Q1
    Q2
    Q3
    Q4
    Q5

- 番号は1から順番に、通し番号で割り振っています。歯抜けはありません。最後が`Q5`ならば、全部で5問あるという意味です。
- `Q`がついていますが、問題をダウンロードするときは、`Q`はつけません。


#### 出題問題をダウンロードする

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/Q/QNUMBER

- QNUMBERには、[出題問題](#GETQ)の整数値を指定します。`Q`はつけません。

ファイルに保存したい場合は、curlの`-o`オプションを使用します。

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/Q/QNUMBER -o FILENAME


<a name="put-a"></a>
#### 回答をアップロードする

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -H "Content-Type: text/plain" --upload-file AFILENAME https://das-adc.appspot.com/A/USERNAME/Q/QNUMBER

- AFILENAMEは、回答ファイルのファイル名を指定してください
- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERには、[出題問題の番号](#GETQ)の整数値を指定します。ただし`Q`はつけません。

以下のような応答が返ってきます。


```
i= 0
check_1 True
check_2 True
check_3 True
check_4 True
check_5 True
res= True
length= [107  11  15  17  10  31   8  12   6   6  11  11  10]
corner= [16  1  1  1  1  3  0  2  0  0  0  0  1]
quality= 0.00355871886121
check_6 True
judges =  [[True, 0.0035587188612099642]]
Quality factor = 0.0035587188612099642
```


この出力形式は、2014年のアルゴリズムデザインコンテストで提供した[回答チェックツール](http://www.sig-sldm.org/nlcheck.html)とほぼ同じです。ただし、ファイル名のチェック処理は、2015年のコンテストでは不要なため、省いています。

- `judges =  [True]`ならば、回答は正しいという意味です。
- `check_1`〜`check_6`は、2014年の回答チェックルールと同じままです。
  - チェック1. 問題の数字の位置と、同じである。
  - チェック2. 問題にはない数字があってはいけない。
  - チェック3. 問題の数字の位置が、線の端点である。
  - チェック4. 線は枝分かれしない。
  - チェック5. 線はつながっている。
  - チェック6. 複数解があるときに、同一の解が含まれていたら、２つめ以降は不正解として扱う。 【2015年ルールでは対象外】
- 2015年ルールで導入した**解の品質**は、Quality factorの行に出ています。


<a name="put-a-info"></a>
#### 回答の補足情報をアップロードする

回答を得るまでにかかった、計算時間（単位: 秒）、使用メモリ量（単位: Byte）、その他（文字列）を、アップロードします。

    curl -H "Accept: application/json" -H "Content-Type: application/json" --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -X PUT --data '{"cpu_sec": CPU_SEC, "mem_byte": MEM_BYTE, "misc_text": "MISC_TEXT"}'  https://das-adc.appspot.com/A/USERNAME/Q/QNUMBER/info

- これを実行する前に、[回答をアップロード](#put-a)しておく必要があります。
- `--data`オプションで、補足情報をJSON形式で指定します。
  - CPU_SECは、実数。小数も可
  - MEM_BYTEは、整数
  - MISC_TEXTは、任意の文字列
- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERには、[出題問題の番号](#GETQ)の整数値を指定します。ただし`Q`はつけません。



### テスト期間中に実行可能な機能

コンテスト本番中には、以下の機能は実行できなくなります。

<a name="GETA"></a>
#### アップロード済の回答データの一覧リストを見る

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/A/USERNAME

- USERNAMEは、アカウントのユーザー名を指定してください

応答の例

    A2
    A6

- アップ済の回答データの番号が返ってきます。番号は、出題番号の頭に`A`をつけたものです


<a name="get-a-num"></a>
#### アップロード済の回答データをダウンロードする

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/A/USERNAME/Q/QNUMBER

- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、[回答済の出題問題](#GETA)の整数値を指定します。`A`も`Q`もつけません。


<a name="delete-a"></a>
#### アップロード済の回答データを削除する

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -X DELETE https://das-adc.appspot.com/A/USERNAME/Q/QNUMBER

- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、[回答済の出題問題](#GETA)の整数値を指定します。`A`も`Q`もつけません。
- 回答の補足情報も同時に削除されます。

応答の例

    DELETE A6


<a name="get-a-info"></a>
#### 回答の補足情報をダウンロードする

    curl -H "Accept: application/json" -H "Content-Type: application/json" --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/A/USERNAME/Q/QNUMBER/info

- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、[回答済の出題問題](#GETA)の整数値を指定します。`A`も`Q`もつけません。0を指定した場合、すべての回答補足情報がダウンロードされます。


ダウンロードしたデータの例

    {"msg": "GET A2 info 1", "results": [{"anum": 2, "cpu_sec": 10.234, "mem_byte": 56789, "misc_text": "test", "result": null}]}

- JSON形式の文字列が返ってきます。
- `msg`に入っている`GET A2 info 1`の`A2`は出題番号、最後の`1`はダウンロードしたデータ数（通常は1）
- `results`には、配列が入っています。配列のサイズは、`msg`のデータ数と同じです。
- 配列の各要素は以下の通り
  - `anum`は、出題番号
  - `mem_byte`、`cpu_sec`、`misc_textは`、[`put-a-info`](#put-a-info)で指定した値
  - `result`は、採点結果。改行コードを含む


#### 回答の補足情報を削除する

    curl -H "Accept: application/json" -H "Content-Type: application/json" --cookie-jar CURL_COOKIES --cookie CURL_COOKIES -X DELETE https://das-adc.appspot.com/A/USERNAME/Q/QNUMBER/info

- USERNAMEは、アカウントのユーザー名を指定してください
- QNUMBERは、[回答済の出題問題](#GETA)の整数値を指定します。`A`も`Q`もつけません。0を指定した場合、すべての回答補足情報が削除されます。

応答の例

    {"msg": "DELETE A2 info 1", "results": [{"anum": 2}]}


### スコアを見る


TBD


<a name="web-browser"></a>
## ウェブブラウザを使ってADCサービスを利用する

[ウェブアプリclient-appのドキュメントは、こちらにあります](../client-app/README.md)。



adccliの管理者専用の機能
-----------------------

一般ユーザー権限では利用できません。

### 実効ユーザー名を`--alt-username`オプションで指定する

RESTful APIのパス名に、ユーザー名を含むもの(例: `/user/ADC-1/Q/1`)について、管理者は、そのユーザー名(例では`ADC-1`)を`adccli --alt-username USERNAME ...`のように引数で指定することができる。

`--alt-username`を指定せず、`--username`オプションで指定した場合はそのユーザー名が使われる。

しかし、`--username`オプションを使うと、設定保存ファイルにて、以降のデフォルト値として使われるようになってしまうので、使い勝手が悪く、不便である。

`--alt-username`も`--username`も指定しなかった場合は、設定保存ファイルに保存されているユーザー名が使われる。


### ユーザー作成

(備考: 2020年バージョンから、[ウェブアプリでユーザー作成が可能](../client-app/README.md))

ユーザーを1人ずつ登録する場合。

    adccli create-user 'ユーザー名' 'パスワード'  '説明など' ユーザーID グループID

|グループID |意味       |
|-----------|-----------|
|0          |管理者用   |
|1000       |テスト用   |
|2000       |ADC参加者用|

`adcusers_in.py`または`adcusers_in.yaml`と同じフォーマットのファイルにアカウント情報を記述して、一括作成する場合。

    adccli create-users FILE.(py|yaml)

### ユーザー削除

    adccli delete-user ユーザー名1 [ユーザー名2 ...]

### ユーザー一覧リスト

	adccli get-user-list

ユーザー情報は、データストアから毎回取り出すのではなく、APIサーバ上でオンメモリで保持している。
`adccli get-user-list`を実行することで、データストアから取り出して、オンメモリの情報が、更新される。

なお、ユーザー作成・削除時にも、オンメモリの情報が、更新される。


### 問題データへのアクセス

管理権限を持ったユーザーは、`get-user-q`、`post-user-q`、`put-user-q`、`delete-user-q`にて、全ユーザの問題に対して、アップロード、ダウンロード、削除が可能。

ユーザー名は`--alt-username`オプションで指定する。`--username`オプションで指定することも可能だが、設定ファイルにユーザー名が書き込まれて、以後のデフォルト値になるので、後々、トラブルや勘違いの元となるので、避けたほうがよい。

全問題のリスト(すべてのユーザー、すべての問題番号)

    adccli get-admin-q-all

出題番号、作者、問題番号の対応関係を出力する

    adccli get-admin-q-list

出題番号を決める（シャフルする）

    adccli put-admin-q-list

出題番号を消去する

    adccli delete-admin-q-list

すべての問題データを消去する

    adccli delete-admin-q-all

### 回答データへのアクセス

すべての回答データの一覧リストを得る

    adccli get-admin-a-all

すべての回答データを消去する

    adccli delete-admin-a-all

### ログ管理

ログを見たり、削除したりする。  
サーバ側の設定により（データストア使用量を削減することで、クラウド利用料を節約するため）、ログが記録されていない場合があり、そのときは、このコマンドではログは見られない。

    adccli [--number NUM] get-log [数値 単位]
    adccli [--number NUM] delete-log [数値 単位]
    adccli [--number NUM] --username='USERNAME' get-user-log [数値 単位]
    adccli [--number NUM] --username='USERNAME' delete-user-log [数値 単位]

数値は整数、単位は、`seconds` か `days` を指定する。

`--number NUM`では、取得／削除するレコード数を指定する。デフォルトは100である。

### スコア表示

やっつけ仕事なので、まだ不完全だが、HTML形式でスコアボードを出力。

    adccli score


### timekeeperのモード切り替え

現在のモードを確認する（Webアプリでは、ステータス行のEnabledに表示されている）。

```
adccli timekeeper-enabled
```

手動モードにする

```
adccli timekeeper-enabled 0
```

自動モードにする

```
adccli timekeeper-enabled 1
```

### timekeeperの状態


現在の状態を確認する（Webアプリでは、ステータス行のStateに表示されている）。

```
adccli timekeeper-state
```

状態遷移する

```
adccli timekeeper-state 状態
```


状態は、'init', 'im0', 'Qup', 'im1', 'Aup', 'im2'のいずれか。


timekeeperを手動モードにして、状態遷移させる例

```
adccli timekeeper-enabled 0

adccli timekeeper-state im0
adccli timekeeper-state Qup
adccli timekeeper-state im1
adccli timekeeper-state Aup
adccli timekeeper-state im2
```

<a name="round-count"></a>
### timekeeperのroundカウンタ

現在のroundカウンタの値を確認する（Webアプリでは、ステータス行のRoundに表示されている）。

``` bash
adccli timekeeper-round
```

roundカウンタの値を設定する。今の所、有効な値は、1, 2, 999

``` bash
adccli timekeeper-round 999  # コンテスト開始前の、動作テスト期間中

adccli timekeeper-round 1    # コンテスト当日より前の、事前競技

adccli timekeeper-round 2    # コンテスト当日の、本番競技
```


### timekeeperのモードと状態を確認する、設定する

enbaled、state、roundの3つをまとめて扱える。

確認する

```
adccli timekeeper
```

設定する

```
adccli timekeeper モード 状態 Roundカウンタ値
```

### その他のサーバconfig設定の取得or変更

サーバconfig設定、(adcconfig.py)[../server/adcconfig.py]の設定を、API経由で制御する。

```
adccli test-mode [True|False]
adccli view-score-mode [True|False]
adccli log-to-datastore [True|False]
```


### Datastoreのデータをダンプする

ファイル形式は、Python pickleである。

コマンドの書式

``` bash
adccli dump-data FILENAME
```

実行例

``` bash
adccli dump-data dump-20210901_1109.pickle
```

### Datastoreのデータをリストアする

**注意** Datastore上のデータがすべて上書きされる。

- コンテスト本番データを上書きして消してしまわないように注意が必要である。
- とくに、アクセス先APIサーバに注意すること。
- アカウント情報もリストアされるが、同一パスワードを利用可能にするためには、ダンプ元環境と、リストア先環境とで、adcconfig.SALTが一致している必要がある。

この、データのダンプ＆リストアのユースケースとしては、Google App Engine上で動作しているAPIサーバのデータをダンプして、ローカル環境で実行しているAPIサーバへデータをリストアする、というものである。
Google App Engine上のAPIサーバへリストアするユースケースは、想定していないが、エラーにはしていないので、くれぐれも注意が必要である。

リストア前に、Qデータ、Aデータは削除しておくこと。

``` bash
adccli delete-admin-q-list
adccli delete-admin-q-all
adccli delete-admin-a-all
```

コマンドの書式

``` bash
adccli restore-data FILENAME
```

実行例

``` bash
adccli restore-data dump-20210901_1109.pickle
```
