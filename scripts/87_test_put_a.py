#! /usr/bin/env python3
#
# coding: utf-8

"""
ADC-0が投稿したQデータに関して、正解のAデータを登録する。

81_test_post-q.shにて、ADC-0は、samples/Q/sample_*_A.txtを順番に登録している。

- ADC-0のQ1は、 samples/Q/sample_1_Q.txt
- ADC-0のQ12は、samples/Q/sample_12_Q.txt

get_admin_q_list()することで、出題リストの元データを特定することで、
ADC-0が出題した問題については、確実に正解させることが可能である。
"""

import os
import sys

def main(top_dir):
    sys.path.insert(0, os.path.join(top_dir, 'client'))
    import adcclient
    cli = adcclient.ADCClient()
    cli.read_config()
    res = cli.get_admin_q_list()
    info = res[6]
    # info.keys() = ['author_list', 'author_qnum_list', 'blocknum_list', 'cols_list', 'linenum_list', 'msg', 'qnum_list', 'rows_list', 'text_admin', 'text_user']
    for i, qnum in enumerate(info['qnum_list']):
        if info['author_list'][i] == 'ADC-0':
            author_qnum = info['author_qnum_list'][i]
            a_file = os.path.join(top_dir, 'samples', 'A', f'sample_{author_qnum}_A.txt')
            print(qnum, author_qnum, a_file)
            cli.alt_username = 'ADC-0'
            res = cli.put_a([qnum, a_file, 'replace-A-number'])
            print(res[6]['msg'])
    cli.alt_username = None


if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    top_dir = os.path.abspath(os.path.join(dir, '../'))
    main(top_dir)
