#! /usr/bin/env python3
#
# coding: utf-8

"""
すべてのAデータをファイルに書き出す
"""

import os
import sys
import re
if '__file__' in locals():
    dir = os.path.dirname(__file__)
else:
    dir = '.'
top_dir = os.path.abspath(os.path.join(dir, '../'))
sys.path.insert(0, os.path.join(top_dir, 'client'))
import adcclient


def dump_a_all(round_count=1):
    cli = adcclient.ADCClient()
    cli.read_config()
    res = cli.get_admin_a_all(round_count=round_count)[6]
    data = res['data']  # type: list
    # In [35]: data[0].keys()
    # Out[35]: dict_keys(['ainfo', 'anum', 'ban_data', 'block_pos', 'date', 'judge', 'owner', 'quality', 'round', 'size', 'text'])
    for d in data:
        ofile = f"round{d['round']}.{d['owner']}.A{d['anum']}.txt"
        with open(ofile, 'w') as f:
            f.write(d['text'])
        print(ofile)

def main():
    import argparse    
    parser = argparse.ArgumentParser(
        description='a tool to get all A data')
    parser.add_argument('-r', '--round', metavar='NUM', default=1, type=int, help='specify round number. (default: %(default)s)')
    args = parser.parse_args()
    dump_a_all(round_count=args.round)

if __name__ == "__main__":
    main()
