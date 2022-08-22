#! /usr/bin/env python3
#
# coding: utf-8

"""
出題された順序で、Qデータをファイルに書き出す
"""

import pickle
import re
import os
import sys
try:
    dir = os.path.dirname(__file__)
except NameError:
    dir = '.'
top_dir = os.path.abspath(os.path.join(dir, '../'))
sys.path.insert(0, os.path.join(top_dir, 'client'))
import adcclient


def dump_q_all(cli: adcclient.ADCClient, filename: str):
    try:
        # もしもdumpファイルがすでに存在するなら、それを使う
        with open(filename, 'rb') as f:
            res = pickle.load(f)
    except FileNotFoundError:
        # ファイルがないので、API call
        res = cli.dump_datastore(filename)[6]
    # dict_keys(['userinfo', 'q_data', 'clock', 'q_list_all', 'q_zip', 'a_data'])
    q_data = res['q_data']
    """
    In [122]: type(q_data)
    Out[122]: list
    
    In [123]: len(q_data)
    Out[123]: 42
    
    In [124]: type(q_data[0])
    Out[124]: tuple
    
    In [125]: len(q_data[0])
    Out[125]: 2
    
    In [126]: type(q_data[0][0])
    Out[126]: int
    
    In [127]: type(q_data[0][1])
    Out[127]: dict
    
    In [128]: q_data[0][0]
    Out[128]: 4872897550090240
    # これは、datastoreのkeyみたいなモノ
    
    In [129]: q_data[0][1].keys()
    Out[129]: dict_keys(['text', 'linenum', 'filename', 'round', 'cols', 'date', 'rows', 'qnum', 'author', 'blocknum'])

    In [130]: q_data[0][1]
    Out[130]: 
    {'text': 'SIZE 72X72\r\nBLOCK_NUM 500\r\n\r\nBLOCK#1 2X3\r\n...',
     'linenum': 250,
     'filename': 'R1N16_72x72B500L250_Q.txt',
     'round': 1,
     'cols': 72,
     'date': datetime.datetime(2022, 8, 21, 23, 36, 9, 473981, tzinfo=<UTC>),
     'rows': 72,
     'qnum': 16,
     'author': 'administrator',
     'blocknum': 500}
    """
    q_text = {}  # q_text[round_number][author][qnum] = "---- Q text ----"
    for (_, data) in q_data:
        round = data['round']
        if round not in q_text:
            q_text[round] = {}
        author = data['author']
        if author not in q_text[round]:
            q_text[round][author] = {}
        qnum = data['qnum']
        q_text[round][author][qnum] = data['text']
    ####
    q_list_all = res['q_list_all']
    """
    In [108]: len(q_list_all)
    Out[108]: 3
    
    In [109]: type(q_list_all[0])
    Out[109]: tuple
    
    In [110]: len(q_list_all[0])
    Out[110]: 2
    
    In [111]: type(q_list_all[0][0])
    Out[111]: int
    
    In [112]: type(q_list_all[0][1])
    Out[112]: dict
    
    In [113]: q_list_all[0][0]
    Out[113]: 1
    # これは、roundカウンタの値
    
    In [114]: q_list_all[0][1].keys()
    Out[114]: dict_keys(['author_list', 'linenum_list', 'cols_list', 'blocknum_list', 'author_qnum_list', 'date', 'rows_list', 'text_user', 'qnum_list', 'text_admin', 'q_key_list'])


    In [117]: q_list_all[0][1]['text_admin']
    Out[117]: 'Q1 administrator 13\nQ2 administrator 5\nQ3 administrator 19\nQ4 administrator 9\nQ5 administrator 17\nQ6 administrator 11\nQ7 administrator 2\nQ8 administrator 18\nQ9 administrator 8\nQ10 administrator 16\nQ11 administrator 20\nQ12 administrator 6\nQ13 administrator 14\nQ14 administrator 4\nQ15 administrator 1\nQ16 administrator 12\nQ17 administrator 10\nQ18 administrator 3\nQ19 administrator 15\nQ20 administrator 7\n'
    
    In [118]: q_list_all[0][1]['author_qnum_list']
    Out[118]: [13, 5, 19, 9, 17, 11, 2, 18, 8, 16, 20, 6, 14, 4, 1, 12, 10, 3, 15, 7]

    In [119]: q_list_all[0][1]['author_list']
    Out[119]: 
    ['administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator',
     'administrator']
    """
    for q_list in q_list_all:
        round_count, data = q_list
        print(f'round={round_count}', data['text_admin'])
        qnum_list        = data['qnum_list']
        author_list      = data['author_list']
        author_qnum_list = data['author_qnum_list']
        for qnum, author, author_qnum in zip(qnum_list, author_list, author_qnum_list):
            ofile = f"round{round_count}.Q{qnum}.{author}.{author_qnum}.txt"
            print(ofile)
            with open(ofile, 'w') as f:
                f.write(q_text[round_count][author][author_qnum])


def main():
    import argparse    
    parser = argparse.ArgumentParser(
        description='a tool to get all Q and A data')
    parser.add_argument('-f', '--file', help='cache retrieved data from API server, in the file', default='dump_q_all.pickle')
    args = parser.parse_args()
    cli = adcclient.ADCClient()
    cli.read_config()
    dump_q_all(cli=cli, filename=args.file)


if __name__ == "__main__":
    main()
