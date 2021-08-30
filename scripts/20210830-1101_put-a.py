#! /usr/bin/env python3
#
# coding: utf-8

"""
ADC-0が投稿したQデータに関して、正解のAデータを登録する。


get_admin_q_list()の結果を利用して、出題リストの元データを特定することで、
ADC-0が出題した問題については、確実に正解させることが可能である。


### 前提条件

- Qデータのファイル名の文字'Q'を文字'A'に置換すると、Aデータのファイル名になる
- Aデータのファイルは、カレントディレクトリにある
"""

import os
import sys
dir = os.path.dirname(__file__)
top_dir = os.path.abspath(os.path.join(dir, '../'))
sys.path.insert(0, os.path.join(top_dir, 'client'))
import adcclient
import re


def main(round_count=1):
    cli = adcclient.ADCClient()
    cli.read_config()
    cli.alt_username = 'ADC-0'
    adc0_q_list = cli.get_user_q_list(round_count=round_count) # list of dict, keys=['blocknum', 'cols', 'date', 'filename', 'linenum', 'qnum', 'rows']
    adc0_q_list = [None] + adc0_q_list  # Q番号が1からなので、listのindexを1だけずらす
    res = cli.get_admin_q_list(round_count=round_count)
    info = res[6]  # info.keys() = ['author_list', 'author_qnum_list', 'blocknum_list', 'cols_list', 'linenum_list', 'msg', 'qnum_list', 'rows_list', 'text_admin', 'text_user']
    for i, qnum in enumerate(info['qnum_list']):
        if info['author_list'][i] == 'ADC-0':
            author_qnum = info['author_qnum_list'][i]
            q_file = adc0_q_list[author_qnum]['filename']
            a_file = re.sub(r'Q', 'A', q_file)
            print(f'Q{qnum}: {author_qnum}: {q_file} --> {a_file}')
            res = cli.put_a([qnum, a_file, 'replace-A-number'])
            print(res[6]['msg'])
    cli.alt_username = None


if __name__ == "__main__":
    main()
