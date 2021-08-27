DA Symposium 2021 Algorithm Design Contest (DAS ADC 2021)
=========================================================

このレポジトリには、[DAシンポジウム](http://www.sig-sldm.org/das/)2021にて開催される、[アルゴリズムデザインコンテスト](https://dasadc.github.io/)(ADC)で使用するソフトウェアが登録されてます。

#### 関連ページ

- [Official Web Site](https://dasadc.github.io/)
- [DAS ADC 2021 rules](https://dasadc.github.io/adc2021/rule.html)


<a name="news"></a>
最新情報 What's new
-------------------

- (2021-08-27) [スケジュールを更新しました。](conmgr.md#schedule)
- (2021-08-26) Qデータを、Zipアーカイブ形式で、一括ダウンロードできるようになりました。[adccli](client/README.md#get-q-all) [client-app](client-app/README.md#arena)
- (2021-08-25) ADC 2021年ルールに対応しました。
    - 得点計算式を変更しました。
    - 回答データの再アップロードが可能になりました
    - [roundカウンタ](client/README.md#round-count)が導入されました。


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
