Client Application for DA Symposium 2020, Algorithm Design Contest (ADC2020)
============================================================================

ADC2020で使うウェブアプリについて説明する。

参加ユーザー向け情報
--------------------

あとで書き足す予定。

### ウェブアプリを使う

ウェブブラウザで https://das-adc.appspot.com/ にアクセスする。

動作確認しているウェブブラウザは、Firefox、Chromeなど。

Internet Explorer 11は、動作未確認であり、かなり怪しい。

### File Checker

ADC参加チームは、最大3問まで、問題を自作して当日提供できるが、その問題データの書式が正しいかを、File Checkerで確認できる。

ウェブアプリの、画面上のほうにメニューが表示されている。その中にある、"File Checker"メニューをクリックする。

File Checker画面にて、問題データ(Q-file)と正解データ(A-file)の2つを指定して、"Check files"ボタンをクリックすると、チェック結果が表示される。

チェック結果の読み方は、[adc2019.pyのドキュメント](../server/adc2019.md)を参照してほしい。


### "Login" (ログインする、ログアウトする)

ウェブアプリの、画面上のほうにメニューが表示されている。その中にある、"Login"メニューをクリックする。

Username、Passwordに、事前に通知されたユーザー名とパスワードを入力し、Loginボタンをクリックする。

ログイン完了後は、メニューバーの下にあるステータスラインに、`User: xxxxxx`のようにユーザー名が表示される。

### "My Account" (アカウント設定)

- "whoami"ボタンをクリックすると、ユーザー名が表示される。ログインできているか動作確認用のための機能である。
- "get-user"ボタンをクリックすると、ユーザー情報 `ユーザー名:説明:uid:gid` が表示される。同じく、動作確認用。
- Change passwordのフォームに必要事項を入力することで、パスワードを変更できる
- "Logout"ボタンで、ログアウトできる

### "My Q" (自作問題の管理)

ここから、自作の問題データをアップロードするなどの操作ができる。

#### "My Q list"

"My Q list"の表には、すでにアップロード済みの問題データが表示されている。

- "Download"ボタンで、ファイルとしてダウンロードできる
- "View"ボタンで、ウェブブラウザ上で内容を表示できる
- "Delete"ボタンで、その問題データを削除できる

#### "Upload Q"

ここで、自作問題データをアップロードできる。

(注意) すでにアップロード済みのファイルがある場合は、それらをすべて削除してから（上記の"Delete"ボタン）、まっさらな状態に戻してから、アップロードすること。

点線の四角の領域にファイルをドラッグアンドドロップするか（色が変わってから、マウスボタンを離すこと）、"Browse"ボタンをクリックして、ダイアログでファイルを選択する。

すると、"List of files to upload"の表の、アップロード対象のファイルが一覧表示される。この時点では、まだアップロードされていない。つづけて、さらにファイルを選択することも可能である。

一度の複数のファイルをアップロードできるが、ADC参加者は、アップロードできるのは3個までである。4個めからは、エラーになる。管理者（administratorユーザー）は、何個でもアップロードできる。


### "Arena" (コンテストで対戦実施中の画面)

#### "Q list"

対戦が開始されると("State"に"Aup"と表示されているとき)、表形式で、出題されたQデータが表示される。

- 表が表示されないときは、"Refresh Q list"をクリックする
- "Download"ボタンは、ファイルとしてダウンロードする
- "View"ボタンは、ブラウザ上で表示する

#### "Upload A"

回答データ(Aファイル)をアップロードする。

1. "A number"テキストボックスに、問題番号を入力する
2. 点線の四角の領域に、回答Aファイルをドラッグアンドドロップするか（色が変わってから、マウスボタンを離すこと）、"Browse"ボタンをクリックして、ダイアログで回答Aファイルを選択する
3. "Start upload A file"ボタンをクリックする
    - "A number"で指定した問題番号と、Aファイルにかかれている問題番号が一致しないときは、エラーになるので、どちらかを修正してからアップロードすればよい。※ 問題番号を間違えて回答すると不正解になってしまうため（1問につき、回答できるのは1回だけ）、それを防止するための機能


### "Score" (スコア表示)

#### "teams"の表

全チームの情報が表示される。

#### "Score board (total)"、"OK point"、"Quality point"、"Bonus point"

- 対戦中、全チームのスコアが表示される
- 運営側のコントロールによって、スコアを非表示にできる

#### Viewer (管理者専用)

- 回答データを表示する


### "Admin" (管理者向け機能)

一般ユーザーでも、なにかしら表示されているが、実際には何も操作できない。すべてエラーになる。


管理者向け情報
--------------

### 管理者としてログインする

管理者のユーザーアカウント(`adcusers_in.yaml`で記述された`uid`が`0`のユーザー)でログインする。

これで、管理者のみに許されたウェブアプリの機能(おもに"Admin"メニューにある)が利用できるようになる。

(注意) 一般ユーザーにもAdminメニューが表示されてしまうが、一般ユーザーが実行すると常にエラーになる。

管理者の業務はADC運営にとってクリティカルな処理を伴うので、フェイルセーフのために、ボタンをクリックする際には、Shift、Ctrl、Altキー(modifier key)などを押しながら、ボタンをクリックするようにしているところがある。どのキーを押すのかは、マウスポインタをボタン上へhoverさせたとき、tool tipsとして表示される。こうしたため、タブレットなどタッチデバイスでは、操作ができなくなってしまった。


### ユーザーを登録する

従来、コマンドライン環境でコマンド`adccli create-users adcusers_in.py`を実行してユーザー登録をしていたが、2020年バージョンから、ウェブアプリでユーザー登録ができるようになっている。

1. YAML形式のファイル`adcusers_in.yaml`にアカウント情報を書く。参考用のファイル`adc2019/server/adcusers_in.sample.yaml`がある
    - `password`は平文で記述する。
2. ディレクトリ`adc2019/server/`にて、コマンド`python adcusers_gen.py`を実行すると、2つのファイル`adcusers.py`と`adcusers.yaml`が生成される
    - `adcusers.py`には、管理者ユーザーのみが記述されていて、データストア内に登録されたアカウント情報に関係なく、固定登録のアカウントとして利用できる。
	- `adcusers.py`に記述されている`password`は、ハッシュ値である
	- `adcusers.py`はサーバー(`adc2019/server`)が起動時に参照するファイルのため、現在実行中のサーバーには、反映されない。たとえばGoogle App Engineで実行中のサーバーの場合は、反映させるにはdeployしなおす必要がある
3. ウェブブラウザでウェブアプリclient-appにアクセスする
4. ウェブアプリの"Admin"メニューにある、"Create users (Upload adcusers\_in.yaml)"にて、2で作成したYAMLファイル`adcusers.yaml`を選択するか、ファイルをドラッグ&ドロップする。
5. "Start upload"ボタンをクリックする。問題なければ、これでユーザーアカウントが作成される
6. この時点では、画面表示がまだ更新されていないので、"Get user list"の下にある"get"ボタンをクリックする。これで、現在登録されている全ユーザーが表示される


### ユーザーを削除する

1. "Admin"メニューをクリックし、Admin画面に移動する。
2. "User account management"の下に、ユーザー名の一覧リストが表示されているので、削除したいユーザーの左端にあるチェックボックスをオンにする。
3. Altキー、Ctrlキー、Shiftキーを押しながら"delete users"ボタンをクリックする。

(注意) ユーザー"administrator"が2つ表示されていることがあるが、2つとも削除しても構わない。削除しても、必ず1つは残る(`adcusers.py`にて登録されている固定ユーザーは、削除できないため)。


### その他の機能

- TimekeeperのModeは、時刻の分の値に応じて、自動的に状態遷移をする/しないを制御する。コンテスト本番中は、0にする
- TimekeeperのStateでは、強制的に、状態遷移させる
- Test modeは、Trueのとき、Aデータをファイルとしてダウンロード可能になる、など
- View score modeは、Trueのとき、"Score"画面でスコアが表示される。対戦中、前半ではTrueにしておいて、後半に入ったらFalseにするのがよい
- Admin Q Listは、出題問題リストを、表示(get)、削除(delete)、作成(put)する。
    - 作成する前に、deleteが必要である。対戦開始前の、状態"im1"のときに、deleteして、putすればよい
	- getで、問題番号ごとに、出題者と、その出題者の何番目の問題か、を確認できる
- Admin Q dataは、出題問題リストの情報を表示する
- Admin A dataは、回答データの概要を表示する
- "User account management"では、ユーザーアカウントの登録と削除ができる（前述のとおり）



****
以下、Angularで自動生成されたドキュメント。参考程度に。
****

# client-app

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 8.2.0.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
