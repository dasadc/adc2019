Client Application for DA Symposium 2020, Algorithm Design Contest (ADC2020)
============================================================================

ADC2020で使うウェブアプリについて説明する。

参加ユーザー向け情報
--------------------

あとで書き足す予定。

### ウェブアプリを使う

ウェブブラウザで https://das-adc.appspot.com/ にアクセスする。

動作確認しているウェブブラウザは、Firefox、Chromeなど。

Internet Explorer 11は、動作未確認で、怪しい。

### ログインする

ウェブアプリの、画面上のほうにメニューが表示されている。その中にある、"Login"メニューをクリックする。

Username、Passwordに、事前に通知されたユーザー名とパスワードを入力し、Loginボタンをクリックする。

ログイン完了後は、メニューバーの下にあるステータスラインに、`User: xxxxxx`のようにユーザー名が表示される。


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
