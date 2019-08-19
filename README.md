DA Symposium 2019 Algorithm Design Contest
==========================================

- [Official Web Site](https://dasadc.github.io/)
- [DAS ADC 2019 rules](https://dasadc.github.io/adc2019/rule.html)


問題データと回答データのチェックツール adc2019.py
=================================================

- Python 3.6にて、動作確認をした。
- チェック結果がNGのときは、例外RuntimeErrorが発生する。


コマンドライン上での実行方法
----------------------------

```
% python3 adc2019.py --help
usage: adc2019.py [-h] [--debug] [--verbose] [--report] [--Q-file Q_FILE]
                  [--A-file A_FILE]

DA Symposium 2019 Algorith Degisn Contest, Command Line Interface tool

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug mode
  --verbose             verbose message
  --report              output detailed report
  --Q-file Q_FILE, -Q Q_FILE
                        Q filename
  --A-file A_FILE, -A A_FILE
                        A filename
```

引数で、`-Q　file`、`-A file`の両方、もしくは、いずれか１つだけを指定する。

- 両方指定したときは、すべてのチェックを行う。
- １つだけ指定したときは、そのファイル単体でのチェックを行う。

チェックでエラーになったとき（例外が発生する）、`--verbose`を指定すると、例外発生時の詳細な情報が表示される。

`--report`を指定すると、チェック結果が詳細に表示される。詳細は、`adc2019.py`中のコメントを参照のこと。


### 実行例 (1)

```
% python3 adc2019.py --Q-file sampleQ0.txt --A-file sampleA0.txt
0.013888888888888888
```

正解のときは、解の品質が表示される。

    (解の品質) = 1 / (全ブロックと配線を囲む矩形面積)


### 実行例 (2)

```
% python3 adc2019.py --Q-file sampleQ0.txt --A-file sampleA0.txt --report
0.013888888888888888
terminal:
[[], [{'block': 1, 'xy': (1, 0)}, {'block': 4, 'xy': (4, 0)}], [{'block': 4, 'xy': (5, 0)}, {'block': 6, 'xy': (5, 4)}], [{'block': 3, 'xy': (0, 6)}, {'block': 5, 'xy': (6, 7)}], [{'block': 4, 'xy': (4, 1)}, {'block': 8, 'xy': (7, 4)}], [{'block': 6, 'xy': (3, 5)}, {'block': 7, 'xy': (2, 5)}], [{'block': 2, 'xy': (3, 3)}, {'block': 7, 'xy': (3, 4)}], [{'block': 1, 'xy': (1, 3)}, {'block': 2, 'xy': (2, 3)}], [{'block': 1, 'xy': (1, 2)}, {'block': 2, 'xy': (3, 2)}], [{'block': 3, 'xy': (1, 6)}, {'block': 7, 'xy': (1, 5)}], [{'block': 3, 'xy': (0, 4)}, {'block': 7, 'xy': (2, 4)}], [{'block': 5, 'xy': (4, 6)}, {'block': 6, 'xy': (4, 5)}]]
count:
[[0 1 2 2 1 1 2 2 2]
 [0 0 0 0 1 0 0 0 2]
 [0 1 2 1 2 2 2 2 2]
 [0 1 1 1 0 0 0 2 2]
 [1 2 1 1 0 1 0 1 2]
 [0 1 1 1 1 2 2 2 2]
 [1 1 0 0 1 0 0 0 0]
 [2 2 2 2 2 2 1 0 0]]
corner:
[[0 0 0 0 0 0 0 0 1]
 [0 0 0 0 0 0 0 0 0]
 [0 0 0 0 1 0 0 1 0]
 [0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 0 0 0 0]
 [0 0 0 0 0 1 0 0 1]
 [0 0 0 0 0 0 0 0 0]
 [1 0 0 0 0 0 0 0 0]]
line_length:
[ 0  4 13  8  7  2  2  2  3  2  3  2]
line_corner:
[0 0 3 1 2 0 0 0 0 0 0 0]
area:
72
```

Qデータのチェック処理
---------------------

関数`read_Q()`では、Qデータ単体で行えるチェック処理を実行する。


### check-Q3: inconsistent block size

Qデータにて、`BLOCK#2 3X2`のように記述されているブロックサイズが、その次に記述されている行列データのサイズと一致しているか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-4.e.txt
ADC2019 rule violation
check-Q3: inconsistent block size
1
(4, 1)
[[ 1]
 [-1]
 [ 8]
 [ 7]]
```

1. ブロック番号
2. ブロックのサイズ。(横, 縦)
3. ブロックの形状

サイズ指定は(4,1)なのに、実際に定義されているブロックは(1,4)なのでエラー。

### check-Q4: invalid size

Qデータにて、`SIZE 10X10`のように記述されている盤サイズが、コンテストルールである`[1, 72]`の範囲内か、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-5.e.txt
ADC2019 rule violation
check-Q4: invalid size
SIZE 78X10
```

1. サイズ指定の行

78はサイズオーバーなのでエラー。


### check-Q5: invalid block number

Qデータにて、`BLOCK_NUM 8`のようにブロック数が指定されているとき、ブロック番号の範囲は`[1, 8]`である。たとえば`BLOCK#1 1X4`のように記述されている各ブロック番号（例では`1`）が、ブロック番号の範囲内か、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-6.e.txt 
ADC2019 rule violation
check-Q5: invalid block number
9
8
```

1. 定義されたブロックの番号
2. 最大のブロック番号

ブロック番号9はありえないので、エラー。


### check-Q7: unknown line

Qデータ中に、解釈不可能な行が含まれていないか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-8.e.txt 
ADC2019 rule violation
check-Q7: unknown line
27
0, +,2
```

1. エラーのあった行番号
2. その行の内容

このファイルでは、ブロック形状を定義する行列データの途中に改行が入ってるため、エラーにされている。


### check-Q6: inconsistent block definition

Qデータにて、`BLOCK#2 3X2`のような記述の個数と、その次に記述されている行列の個数が一致しているか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-9.e.txt
ADC2019 rule violation
check-Q6: inconsistent block definition
8
7
7
```

1. `BLOCK_NUM`で宣言された、ブロックの個数
2. `BLOCK#`で宣言されている、ブロックの個数
3. ブロック形状の個数

このファイルでは、ブロック4の定義が抜けている。


### check-Q8: BLOCK# not found

Qデータにて、`BLOCK_NUM 8`のようにブロック数が指定されているとき、8個のブロックが定義されていなければならない。
すべてのブロックが定義されているか、確認する。

### check-Q2: unknown block shape

Qデータにて定義できるブロックの形状は、テトロミノ（4マス）と、モノミノ（1マス）だけである。行列で定義されたブロックの形状が、決められた形状のどれかに一致しているか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-2.e.txt 
ADC2019 rule violation
check-Q2: unknown block shape
[[10  0]
 [-1  9]
 [ 3  9]]
```

1. エラーとされたブロックの形状。-1は`+`のこと。


### check-Q1: all numbers must appear twice

Qデータにて定義されたブロックは、数字マスが含まれている。数字マスは、ナンバーリンクパズルでのラインの端点となるマスである。
この数字マスが、2個ずつのペアで存在しているか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-10.e.txt
ADC2019 rule violation
check-Q1: all numbers must appear twice
[12  2  2  2  1  2  2  2  2  2  2  2  1]
```

1. 各数字(0, 1, 2, ...)が出現した回数のリスト。

リスト先頭の0番目の要素は、数字0のことであり無視してよい。
12番目の要素の値は1であり、このデータでは数字12が1回しか出現していないことを示している。


Aデータのチェック処理(第1段階)
------------------------------

関数`read_A()`では、Aデータ単体で行えるチェック処理を実行する。

### check-A1: syntax error in SIZE

Aデータにて、`SIZE 9X8`のようなサイズ指定が2回以上出現しないか、確認する。

### check-A2: invalid size

Aデータにて、`SIZE 9X8`のように記述されている盤サイズが、コンテストルールである`[1, 72]`の範囲内か、確認する。

### check-A3: duplicated BLOCK#

Aデータにて、`BLOCK#1 @(1,0)`のように記述されているブロック位置情報にて、ブロック番号が重複して出現しないか、確認する。

### check-A4: SIZE not found

Aデータにて、`SIZE 9X8`のようなサイズ指定がされているか、確認する。

### check-A5: invalid block position

Aデータにて、`BLOCK#1 @(1,0)`のように記述されているブロック位置情報にて、ブロックの左上座標が、盤の座標範囲内にあるか、確認する。
なお、盤の左上の座標は、(0,0)である。

### check-A6: unknown line

Aデータにて、解釈不可能な行が含まれていないか、チェックする。

行列データの途中で、空行を入れてはいけない。それ以外では、空行が入ってもよい。

```
% ./adc2019.py --Q-file tests/testQ0-0.txt --A-file tests/testA0-6.e.txt 
ADC2019 rule violation
check-A6: unknown line
7
10,10,10, 6, 0, 2, 0, 4, 2
```

1. 7行目がエラー
2. その行の内容

行列データの途中に空行が入ってるため、エラーにされた。

### check-A6: syntax error

これは、その他の理由で、ファイルの書式が正しくないときに出るエラー。

```
% ./adc2019.py -Q sampleQ0.txt -A sampleQ0.txt
ADC2019 rule violation
check-A6: syntax error
2
BLOCK_NUM 8
```

1. 2行目がエラー
2. その行の内容

行列データの途中に空行が入ってるため、エラーにされた。エラーになるのは、Aデータを指定するべきところに、Aデータのファイルを指定してるため。


### check-A7: BLOCK not found

Aデータにて、`BLOCK#1 @(1,0)`のように記述されているブロック位置情報が存在しているか、確認する。

### check-A8: BLOCK# not found

Aデータにて、`BLOCK#1 @(1,0)`のように記述されているブロック位置情報のブロック番号が、1, 2, 3,…と途中で抜けることなく、すべて存在しているか、確認する。

### check-A9: size mismatch

Aデータにて、`SIZE 9X8`のように記述されている盤サイズが、その次に記述されている行列のサイズと一致しているか、確認する。


Aデータのチェック処理(第2段階)
------------------------------

関数`check_dataA()`では、QデータとAデータを照合しながら、チェック処理を行う。


### check-QA1: number of block mismatch

QデータとAデータとで、ブロック数が一致しているか、チェック処理を行う。

### check-QA2: inconsistent numbers on block

Aデータの盤面上のブロックの数字マスが、Qデータでのブロックの数字マスと一致しているか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-0.txt --A-file tests/testA0-4.e.txt
ADC2019 rule violation
check-QA2: inconsistent numbers on block
1
(1, 0)
[[ 1]
 [-1]
 [ 8]
 [ 7]]
[[1]
 [0]
 [7]
 [8]]
```

1. `1`は、ブロック番号1
2. `(1,0)`は、ブロックの配置座標
3. 問題データのブロック
4. 回答データでのブロック

`8`と`7`のマスで、値が不一致している。
なお、`-1`は、問題データで`+`の箇所である。2019年ルールでは0として回答することにしたため、-1と0は不一致とは見なさない。


### check-QA3: block overlapped

Aデータの盤面上のブロックが重なって配置されていないか、確認する。

```
% ./adc2019.py --Q-file tests/testQ0-0.txt --A-file tests/testA0-5.e.txt
ADC2019 rule violation
check-QA3: block overlapped
[[0 0 1 0 1 1 0 0 0]
 [0 0 1 0 1 1 0 0 0]
 [0 0 1 1 0 0 0 0 0]
 [0 0 2 1 1 1 1 0 0]
 [1 0 1 1 1 1 1 1 0]
 [1 1 1 1 1 0 0 0 0]
 [1 1 0 0 1 1 1 0 0]
 [0 0 0 0 0 0 1 0 0]]
```

- 値が2以上の箇所が、ブロックが重なっていることを示している。


### check-A10: not terminal

ブロック内の数字マスが、線の始点か終点になってるか、確認する。


### check-A11: line is branched

線が枝分かれしていないことを確認する。


### check-A12: line is disjoint

線がすべてつながっていることを確認する。




チェック結果（check_dataの返り値）
---------------------------------

dictの意味は以下の通り。

- `terminal`は、線の始点と終点の情報
- `count`は、「マスの接続数」の行列。マスの接続数とは、四方の隣接マスで同じ数を持つマスの個数
- `corner`は、線の折れ曲がり位置を示す行列
- `line_length`は、線長の配列（線の番号ごと）
- `line_corner`は、線の折れ曲がり回数（線の番号ごと）
- `area`は、盤面上で、全ブロックと配線が占有している矩形領域の面積



ファイル・フォーマットのあいまいな点を修正
------------------------------------------

https://dasadc.github.io/adc2019/rule.html

### Qデータのブロック定義

> ブロックのサイズは `BLOCK#[i] [W]X[H]`で定義される。iはブロック番号、WとHはそれぞれブロックの幅と高さである

- iは、1,2,3,…の通し番号とする。途中で番号が飛ぶことはなく、最大値は、`BLOCK_NUM [N]`のNに等しい、とする。ただし、`adc2019.py`で処理するときは、ブロック番号はソートされていなくてもよいことにする。

### Qデータの空行

> 問題フォーマット例
> 
> BLOCK#1 1X4
> 1
> +
> 8
> 7
> 
> BLOCK#2 3X2
> 0,8,0
> 7,6,+

BLOCK ? BLOCKの間に、空行が無くても、`adc2019.py`は処理できることにする。


### AデータのBLOCK位置記述

> 回答フォーマット例
> 
> BLOCK#1 @(1,0)
> BLOCK#2 @(2,2)
> BLOCK#3 @(0,4)
> BLOCK#4 @(4,0)
> BLOCK#5 @(4,6)
> BLOCK#6 @(3,4)
> BLOCK#7 @(1,4)
> BLOCK#8 @(5,3)

- 番号1,2,3...は、ソートされていなくても、`adc2019.py`は処理できることにする。
- `BLOCK #8 @ ( 5 , 3 )`のように、途中にスペースが入っても、`adc2019.py`は処理できることにする。


### 問題点: 回答フォーマットの「0」の扱いがあいまいではないか？

https://github.com/dasadc/dasadc.github.io/issues/17

https://dasadc.github.io/adc2019/rule.html

回答フォーマット例が以下のようになっていて

```
SIZE 9X8
 0, 1, 1, 1, 1, 2, 2, 2, 2
 0, 0, 0, 0, 4, 0, 0, 0, 2
 0, 8, 8, 8, 4, 4, 4, 4, 2
 0, 7, 7, 6, 0, 0, 0, 4, 2
10,10,10, 6, 0, 2, 0, 4, 2
 0, 9, 5, 5,11, 2, 2, 2, 2
 3, 9, 0, 0,11, 0, 0, 0, 0
 3, 3, 3, 3, 3, 3, 3, 0, 0
BLOCK#1 @(1,0)
BLOCK#2 @(2,2)
BLOCK#3 @(0,4)
BLOCK#4 @(4,0)
BLOCK#5 @(4,6)
BLOCK#6 @(3,4)
BLOCK#7 @(1,4)
BLOCK#8 @(5,3)
```

BLOCK#1の定義は以下のようになっている。

```
BLOCK#1 1X4
1
+
8
7
```

回答フォーマットから、該当箇所を抜き出した場合、

```
1
0
8
7
```

となってしまい、`0`と`+`とで、辻褄が合わないのではないか？

#### 暫定処置

今からルール変更すると迷惑をかけてしまうため、今回（2019年）は、回答フォーマットでの`0`と`+`を同一視する、ということにする。

回答フォーマットでは、`0`としても、`+`としても、どちらでもよい。
