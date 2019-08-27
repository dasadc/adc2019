# このドキュメントは、旧版をコピペしただけで、未完成です。

自動運用システムは、現在もなお開発中です。
まだ動作しない機能があります。


### 動作すると思われる機能

1. ファイルのチェック機能
2. ログイン、ログアウト
3. ユーザーの自作問題データのアップロード、管理
4. 運営管理者向けの一部の機能



# アルゴリズムデザインコンテスト(ADC)の自動運用システムの利用方法

DAシンポジウム2019にて開催されるアルゴリズムデザインコンテスト(ADC)では、クライアント・サーバ方式による、自動運用システムを導入します。

問題データの配布、回答データの提出、スコア計算、スコア表示などが、すべてネットワーク経由で自動的に行われます。

## 利用スタイル

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



## (1)adccliと(2)curlで必要なソフトウェア

以下のどちらかをご用意ください。

|名称            |参考                    |
|----------------|----------------------- |
|Python 3.6以降  |https://www.python.org/ |
|curl            |http://curl.haxx.se/    |

pythonとcurlは、LinuxやMacなどでは、ほぼ標準でインストールされています。Windowsでは、申し訳ありませんが各自でインストールをお願いします。

### APIの利用

ADCのサービスは、Web APIによって提供されています。そのため、自作プログラムからAPIを使って、ADCのサービスを利用することも可能です。

- APIの詳細は、[curlを用いて確認](#curl)できます。
- [クライアントライブラリ](#adcclient)を利用することもできます。※[adccli](#adccli)は、そのサンプル実装です。


### 2019年版の変更

このドキュメントは旧版をベースに記載されているため、クッキーを使ってAPIを呼び出す方法を示していますが、現在、クッキーを使わずに、アクセストークンを使って認証を行う機能が実装されています。

アクセストークンは、ログイン成功時に取得できます。ログインしなおすたびに、アクセストークンは新規生成されます。

adcclient.pyでは、ユーザー名とアクセストークンをそれぞれ環境変数`ADC_USER`、`ADC_TOKEN`にセットしてAPIを呼び出せます。

curlなどで、HTTPプロトコルでアクセスするときは、`ADC-USER`ヘッダ、`ADC-TOKEN`ヘッダを付加します。

入出力データのフォーマットがまちまちだったのが、JSONで統一しています。ウェブブラウザからアクセスしたときのための、HTMLを出力する機能は、すべて廃止しました。
ウェブアプリ部分は、Angularを使って、新規に作り直しました。

従来、Python 2.7系で開発されていましたが、Python 3系へ移行しました。ほぼ全面的に書き換えたため、Python 2.7では、もう動きません。


## 注意事項

インターネット上のサイト`das-adc.appspot.com`は、Google App EngineにてホスティングされたWebサービスです。

- Google App Engineを無料の範囲内で利用するために、大量アクセスによる負荷テストのようなことは、ご遠慮ください。
  - 利用制限は、24時間単位でリセットされるそうなので、最大24時間待てばアクセスできるはずです。もし繰り返し無料の範囲を越えることが発生するようでしたら、なんらかの対応策をとります。DAシンポジウム幹事までおしらせください。幹事でも、日頃から利用状況をできるだけ確認します。
- アルゴリズムデザインコンテストの本番では、Google App Engineを使わず、ローカル環境で実行するので、課金問題は発生しません。


## ADCサービスを利用するためのツール

[adccliを使う方法](#adccli)(要 Python 3.6)と、[curlを使う方法](#curl)(要 curl)の2通りを紹介します。

<a name="adccli"></a>
### コマンドラインツール adccli （クライアントのサンプル実装）

ADCサービスを利用するためのコマンドラインツールadccliを用意しました。Python 3.6で記述しています。

#### adccliの入手

1. `git clone https://github.com/dasadc/adc2019.git`します。
2. `adc2019/client/`フォルダーにファイル一式が入ってます。



以下の環境で、ある程度の動作確認を行っています。

- CentOS 7 x86_64  (Python 3.6.8)

このツールについての、ご意見、改良案、パッチなど、歓迎します。



#### おもなオプション

`adccli --help`で、かんたんなヘルプメッセージが表示されます。

```
$ ./adccli --help
usage: adccli [-h] [--debug] [--verbose] [-c FILE] [-u USERNAME]
              [--alt-username ALT_USERNAME] [-p PASSWORD] [-U URL] [-o FILE]
              cmd [arg [arg ...]]

DA Symposium 2019 Algorithm Design Contest, Command Line Interface tool

positional arguments:
  cmd                   "adccli help" will show help of cmd.
  arg

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug mode
  --verbose             verbose message
  -c FILE, --config FILE
                        config file (default:
                        /home/user/adcclient.json)
  -u USERNAME, --username USERNAME
                        set username (default: administrator)
  --alt-username ALT_USERNAME
                        set alternative username. admin only
  -p PASSWORD, --password PASSWORD
                        set password
  -U URL, --URL URL     set server URL (default: https://das-adc.appspot.com/)
  -o FILE, --output FILE
                        output file name (default: None)
```


サブコマンド`cmd`のヘルプが、`adccli help`で表示されます。


```
$ ./adccli help

  login
  logout
  whoami
  password [NEWPASSWORD]
  get-user-list
  get-user [USERNAME ...]
  get-q [NUMBER ...]
  put-a NUMBER FILENAME
  put-a-info NUMBER CPU_SEC MEM_BYTE [MISC_TEXT]
  get-a-info [NUMBER]
  delete-a-info NUMBER
  get-a [NUMBER ...]          # test mode only
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
  create-user USERNAME PASSWORD DISPLAYNAME UID GID
  create-users FILENAME
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
  timekeeper-enabled [0|1]
  timekeeper-state [init|im0|Qup|im1|Aup|im2]
  timekeeper
```

#### 設定ファイル

adccli用設定ファイル`adcclient.json`が、ホームディレクトリに自動的に作成されます。

オプション`--username`や`--URL`で指定した値は、設定ファイルに保存され、以後、デフォルト値として利用されるようになります。

Webのクッキーもこの設定ファイルに保存されます。loginに成功した後は、ログイン状態が継続します。設定ファイルにパスワードは保存されません。


<a name="adcclient"></a>
#### クライアントライブラリ adcclient.py

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

### アクセスログを確認する

ユーザが行ったアクセスログを表示します。

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


#### 出題問題をダウンロードする

出題番号を指定して、出題された問題データをダウンロードしてください。

    adccli get-q 出題番号

- `出題番号`は、[出題問題](#GETQ)の整数値を指定します。`Q`はつけません。

ファイルに出力したい場合

    adccli --output ファイル名 get-q 出題番号


#### 回答をアップロードする

    adccli put-a 出題番号 ファイル名

[参考](#put-a)

<a name="adccli-put-a-info"></a>
#### 回答の補足情報をアップロードする

回答を得るまでにかかった、計算時間（単位: 秒）、使用メモリ量（単位: Byte）、その他（文字列）を、アップロードします。

    adccli put-a-info 出題番号 CPU_SEC MEM_BYTE MISC_TEXT

- これ(put-a-info)を実行する前に、回答をアップロード(put-a)しておく必要があります。
- 出題番号は、数値。`Q`も`A`もつけない
- CPU_SECは、実数。小数も可
- MEM_BYTEは、整数
- MISC_TEXTは、任意の文字列

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

**開発中です。**


<a name="curl"></a>
## curlを使ってADCサービスを利用する

adccliは実行のためにpythonの実行環境が必要となりますが、その代りに、curl単体でも、ADCサービスを利用できます。

また、自作プログラムからADCサービスAPIを直接呼び出したい方も、参考にしてください。curlに`-v`オプションをつけて実行すると、より詳細な情報が得られます。

ちなみに、das-adc.appspot.comへは、httpでもhttpsでもアクセスできるようになっています。

### loginする

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

    curl --cookie-jar CURL_COOKIES --cookie CURL_COOKIES https://das-adc.appspot.com/logout

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

**2015年7月31日現在、回答チェック機能は、まだ開発途中です。**

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


**開発中です。**


<a name="web-browser"></a>
## ウェブブラウザを使ってADCサービスを利用する

**開発中です。一部の機能のみが動作します**

ウェブブラウザで、 https://das-adc.appspot.com/static/app/index.html にアクセスしてください。

Internet Explorerでは、正常に動作しないかもしれません。

ページの上部に、「File Checker」、「Login」、「My Account」、「My Q」、…というったリンクが並んでいるので、それをクリックしてください。各コマンド専用の画面が表示されます。


### データ確認

File Checkerは、ログインせずに使うことができます。本番用の問題データのフォーマットが正しいかを確認できます。

### コンテストの予行練習

1. まずLoginでログインしてください。
2. My Qで、問題データをアップロードできるか確認してください。ここでは、本番用の問題データは使わないでください。他のユーザーに公開される可能性があります。

（この後、ドキュメント更新する予定）




## adccliの管理者専用の機能

一般ユーザー権限では利用できません。

### ユーザー作成

ユーザーを1人ずつ登録する場合。

    adccli create-user 'ユーザー名' 'パスワード'  '説明など' ユーザーID グループID

|グループID |意味       |
|-----------|-----------|
|0          |管理者用   |
|1000       |テスト用   |
|2000       |ADC参加者用|

`adcusers_in.py`と同じフォーマットのファイルにアカウント情報を記述して、一括作成する場合。

    adccli create-users FILE

### ユーザー削除

    adccli delete-user ユーザー名1 [ユーザー名2 ...]


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

ログを見たり、削除したりする

    adccli get-log [数値 単位]
    adccli delete-log [数値 単位]
    adccli --username='USERNAME' get-user-log [数値 単位]
    adccli --username='USERNAME' delete-user-log [数値 単位]

数値は整数、単位は、`seconds` か `days` を指定する。

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

### timekeeperのモードと状態を確認する、設定する

enbaledとstateを2つをまとめて扱える。

確認する

```
adccli timekeeper
```

設定する

```
adccli timekeeper モード 状態
```