

curlを使って、ファイル・チェックを行う
--------------------------------------


```
curl -X POST --form Qfile=@FILE1 --form Afile=@FILE2 http://127.0.0.1:4280/api/test_post
```

- curlでJSON形式のデータを作るのが面倒なので、特別に、フォームでファイルをアップロードするときの形式で、API `/api/test_post`を呼べるようにした
- FILE1は、Qデータのファイル
- FILE2は、Aデータのファイル
- `http://127.0.0.1:4280`は、APIサーバのアドレスとポート
- 結果はJSON形式で返ってくる(`Content-Type: application/json`)


### 正しいデータの例

```
% curl -X POST --form Qfile=@sampleQ0.txt --form Afile=@sampleA0.txt http://127.0.0.1:4280/api/test_post
{"area":72,"ban_data_F":"[[ 0  1  1  1  1  2  2  2  2]\n [ 0 -1  0  0  4 -1  0  0  2]\n [ 0  8  8  8  4  4  4  4  2]\n [ 0  7  7  6 -1 -1 -1  4  2]\n [10 10 10  6 -1  2 -1  4  2]\n [-1  9  5  5 11  2  2  2  2]\n [ 3  9  0  0 11 -1 -1  0  0]\n [ 3  3  3  3  3  3  3  0  0]]","corner":"[[0 0 0 0 0 0 0 0 1]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 1 0 0 1 0]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 0 0 0 0 0]\n [0 0 0 0 0 1 0 0 1]\n [0 0 0 0 0 0 0 0 0]\n [1 0 0 0 0 0 0 0 0]]","count":"[[0 1 2 2 1 1 2 2 2]\n [0 0 0 0 1 0 0 0 2]\n [0 1 2 1 2 2 2 2 2]\n [0 1 1 1 0 0 0 2 2]\n [1 2 1 1 0 1 0 1 2]\n [0 1 1 1 1 2 2 2 2]\n [1 1 0 0 1 0 0 0 0]\n [2 2 2 2 2 2 1 0 0]]","dim":[0,0,9,8],"line_corner":"[0 0 3 1 2 0 0 0 0 0 0 0]","line_length":"[ 0  4 13  8  7  2  2  2  3  2  3  2]","terminal":[[],[{"block":1,"xy":[1,0]},{"block":4,"xy":[4,0]}],[{"block":4,"xy":[5,0]},{"block":6,"xy":[5,4]}],[{"block":3,"xy":[0,6]},{"block":5,"xy":[6,7]}],[{"block":4,"xy":[4,1]},{"block":8,"xy":[7,4]}],[{"block":6,"xy":[3,5]},{"block":7,"xy":[2,5]}],[{"block":2,"xy":[3,3]},{"block":7,"xy":[3,4]}],[{"block":1,"xy":[1,3]},{"block":2,"xy":[2,3]}],[{"block":1,"xy":[1,2]},{"block":2,"xy":[3,2]}],[{"block":3,"xy":[1,6]},{"block":7,"xy":[1,5]}],[{"block":3,"xy":[0,4]},{"block":7,"xy":[2,4]}],[{"block":5,"xy":[4,6]},{"block":6,"xy":[4,5]}]]}
```


### 正しくないデータの例


```
% curl -X POST --form Qfile=@sampleQ0.txt --form Afile=@sampleQ0.txt http://127.0.0.1:4280/api/test_post
{"error":["ADC2019 rule violation","check-A6: syntax error","2","BLOCK_NUM 8"],"stack_trace":"Traceback (most recent call last):\n  File \"../adc2019.py\", line 467, in read_A\n    ban_data.append([int(n) for n in line2.split(',')])\n  File \"../adc2019.py\", line 467, in <listcomp>\n    ban_data.append([int(n) for n in line2.split(',')])\nValueError: invalid literal for int() with base 10: 'BLOCK_NUM 8'\n\nDuring handling of the above exception, another exception occurred:\n\nTraceback (most recent call last):\n  File \"....../adc2019/server/main.py\", line 48, in test_post\n    A = adc2019.read_A(adata)\n  File \"../adc2019.py\", line 469, in read_A\n    raise RuntimeError('check-A6: syntax error', input_line_cnt, line)\nRuntimeError: ('check-A6: syntax error', 2, 'BLOCK_NUM 8')\n"}
```



# 2019-08-11

```
npm init
npm install @angular/cli
npm install typescript
npm install http-server
npm install ngx-file-drop --save

sh ~/Downloads/Miniconda3-latest-Linux-x86_64.sh 
/opt/miniconda3
bash
conda config --set auto_activate_base false


conda update -n base -c defaults conda
conda create -n py37 python=3.7
conda activate py37
conda install Flask==1.0.2
conda install numpy
conda install gunicorn

gunicorn main:app
http://127.0.0.1:8000/static/app/index.html
```

# 開発中の実行方法

## (backend) API server

    python main.py

http://127.0.0.1:4280/

## (frontend) Angular, development server

    `npm bin`/ng serve --proxy-config proxy.conf.json --verbose
	または
	npm run test-run

http://localhost:4200/

## deploy前のテスト実行方法

ビルドする。

	cd client-app/
	$(npm bin)/ng build --prod --base-href=/static/app/index.html --output-path=../server/static/app/
	または
    npm run build

実行する。

	cd server/
	gunicorn main:app

http://127.0.0.1:8000/static/app/index.html
