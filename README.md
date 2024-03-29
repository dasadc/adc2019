DA Symposium 2022 Algorithm Design Contest (DAS ADC 2022)
=========================================================

このレポジトリには、[DAシンポジウム](http://www.sig-sldm.org/das/)2022にて開催される、[アルゴリズムデザインコンテスト](https://dasadc.github.io/)(ADC)で使用するソフトウェアが登録されてます。

ソフトウェアの名前が「adc2019」になっているのは、2019年に開催されたアルゴリズムデザインコンテストのルールに合わせて開発されたからです。コンテストの基本的なルールは同じなので、名前もadc2019のままになっています。


#### 関連ページ

- [Official Web Site](https://dasadc.github.io/)
- [DAS ADC 2022 rules](https://dasadc.github.io/adc2022/rule.html)
- [DAS ADC 2021 rules](https://dasadc.github.io/adc2021/rule.html)


<a name="news"></a>
最新情報 What's new
-------------------

- (2022-08-22) [コンテスト実施スケジュール](conmgr.md#schedule)を更新しました。


ADC自動運営システム
------------------

- [ADC自動運営システムの利用方法](conmgr.md)


ツール一覧
---------

- 参加チーム用ツール
    - [コマンドライン版クライアント adccli](client/README.md)
    - [Webアプリ client-app](client-app/README.md)
- 運営用ソフトウェア
    - [APIサーバ](server/README.md)


- 問題データと回答データのチェック・ツール
    - コマンドライン版 [adc2019.pyの使い方](server/adc2019.md)
	- Webアプリ client-appの[File Checker](client-app/README.md#file-checker)

### チェック・ツールの目的

- 参加チームは、最大3問まで、問題を自作して当日提供できます。その問題データの書式が正しいかを、確認できます。
- 回答データの書式が正しいかを、確認できます。このためには、問題データも必要です。


更新履歴
-------

### ADC2021

- (2021-09-01) [ソフトウェアを更新しました。](https://github.com/dasadc/adc2019/commits/master)以下の運営側にとってのバグ修正がメインです。すでに競技開始後ですので、コンテスト参加者のみなさんは、更新しなくてもOKです。
    - [Google App Engineで実行中のAPIサーバから返ってくる、いくつかのモード設定値が、コロコロ変化する](https://github.com/dasadc/adc2019/issues/66)
    - [File checkerおよびScoreメニューでの盤面表示にバグがある](https://github.com/dasadc/adc2019/issues/70)
- (2021-08-27) [ソフトウェアを更新しました。](https://github.com/dasadc/adc2019/commits/master)
- (2021-08-27) [スケジュールを更新しました。](conmgr.md#schedule)
- (2021-08-26) Qデータを、Zipアーカイブ形式で、一括ダウンロードできるようになりました。[adccli](client/README.md#get-q-all) [client-app](client-app/README.md#arena)
- (2021-08-25) ADC 2021年ルールに対応しました。
    - 得点計算式を変更しました。
    - 回答データの再アップロードが可能になりました
    - [roundカウンタ](client/README.md#round-count)が導入されました。
