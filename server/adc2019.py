#! /usr/bin/env python3
# coding: utf-8

"""
DA Symbosium 2019 Algorithm Design Contest
==========================================


Variables
----------

block : dict
    - key is tuple (type, index)
        - type is string, {'a', 'b', ... 'g'}, see below :ref:`block type name <image-block-type>` image.
        - index is int, {0, 1, 2, 3} means rotation 0, 90, 180, 270.
    - value is list of string, block data.

np_block : dict
    same as block, but value is numpy array

block_color : dict
    - key is string, {'a', 'b', ... 'g'}
    - value is string, RGB color '#0123ab'

.. _image-block-type:

block type name
^^^^^^^^^^^^^^^
- tetromino is 'a', 'b', 'c', 'd', 'e', 'f', 'g'.
- monomino is 'z'.

.. image:: ../_static/block_type.png
"""

from typing import List, Dict
import numpy as np
import re

debug = False
verbose = False

# '__blocks_in' is source data. block is made from __blocks_in.
__blocks_in = {
    ('a', 0): '''
X
X
X
X
''',
    ('a', 1): '''
XXXX
''',
    ('b', 0): '''
XX
XX
''',
    ('c', 0): '''
 X 
XXX
''',
    ('c', 1): '''
X 
XX
X 
''',
    ('c', 2): '''
XXX
 X 
''',
    ('c', 3): '''
 X
XX
 X
''',
    ('d', 0): '''
X 
X 
XX
''',
    ('d', 1): '''
XXX
X  
''',
    ('d', 2): '''
XX
 X
 X
''',
    ('d', 3): '''
  X
XXX
''',
    ('e', 0): '''
 X
 X
XX
''',
    ('e', 1): '''
X  
XXX
''',
    ('e', 2): '''
XX
X 
X 
''',
    ('e', 3): '''
XXX
  X
''',
    ('f', 0): '''
 XX
XX 
''',
    ('f', 1): '''
X 
XX
 X
''',
    ('g', 0): '''
XX 
 XX
''',
    ('g', 1): '''
 X
XX
X 
''',
    ('z', 0): 'X'
}

__same = (('a', ((2, 0), (3, 1))),
          ('b', ((1, 0), (2, 0), (3, 0))),
          ('f', ((2, 0), (3, 1))),
          ('g', ((2, 0), (3, 1))),
          ('z', ((1, 0), (2, 0), (3, 0))))
"""
__same is used for copying block data
(type, ((dst_index, src_index), ...)) will make
blocks[(type, dst_index)] = blocks[(type, src_index)]
"""

block_color = {'a': '#ffff00',
               'b': '#c6e3b5',
               'c': '#ffe79c',
               'd': '#bdd7ef',
               'e': '#ffc300',
               'f': '#5a9ad6',
               'g': '#f7cbad',
               'z': '#a0a0a0'}
block = {}
np_block = {}


def __setup():
    """
    setup variables: block, np_block
    """
    for k, v in __blocks_in.items():
        x = v.split('\n')
        block[k] = [i for i in x if i != '']

    for t, data in __same:
        for dst, src in data:
            block[(t, dst)] = block[(t, src)]

    tbl = str.maketrans({' ': '0', 'X': '1'})
    for k, v in block.items():
        tmp = []
        for row in v:
            tmp.append([int(i) for i in row.translate(tbl)])
            try:
                np_block[k] = np.array(tmp, dtype=int)
            except ValueError:
                raise ValueError('Error: cannot convert', k, v, tmp)


__setup()


def prt(key):
    """
    debug print block data

    Parameters
    ----------
    key : tuple (type, index)
        | type = {'a', 'b', ... 'g'}
        | index = {0, 1, 2, 3}
    """
    for v in block[key]:
        print(v)


def read_Q_file(file):
    """
    read Q file

    Parameters
    ----------
    file : str
        filename

    Returns
    -------
    read_Q : tuple
        see :py:meth:`adc2019.read_Q`
    """
    with open(file, 'r', newline=None) as f:  # universal newlines mode
        s = f.read()
        return read_Q(s)


def read_Q(s):
    """
    read Q data

    Parameters
    ----------
    s : str
        | Q data is like
        | SIZE 10X10
        | BLOCK_NUM 8
        | BLOCK#1 1X4
        | ...

    Returns
    -------
    size : tuple
        (x,y) of line "SIZE xXy"

    block_num : int
        b of line "BLOCK_NUM b"

    block_size : list
        list of defined block size.

    block_data : list of numpy array, dtype=int
        list of defined block data.

    block_type : list of tuple
        (type, index)

    n_lines : int
        number of lines

    Examples
    --------

    return value of block_size is list of tuple, like
    [(1,4), (3,2), (2,2), ...]

    return value of block_data is list of defined block data.

    ============ =====================
    value        contents
    ============ =====================
         -1      block cell without number
          0      not block cell
         others  block cell with number
    ============ =====================

    return value of block_type is tuple (type, index)

    ===== ======= ===================
    value type    example
    ===== ======= ===================
    type  string  {'a', 'b', ... 'g'}
    index int     {0, 1, 2, 3}
    ===== ======= ===================
    """
    global debug
    input_line_cnt = 0
    size = (0, 0)  # (x,y)
    in_block = False
    block_num = 0  # n
    block_size_x, block_size_y = 0, 0
    dict_block_size = {}
    dict_block_data = {}
    block_tmp = []
    block_num_tmp = 0
    # numbers = {} # key=number, value=bool. True if the number exists
    num_lines = 0  # number of lines (== max number)
    pSIZE = re.compile(r'SIZE\s+([0-9]+)X([0-9]+)', re.IGNORECASE)
    pBLOCK_NUM = re.compile(r'BLOCK_NUM\s+([0-9]+)', re.IGNORECASE)
    pBLOCK = re.compile(r'BLOCK#([0-9]+)\s+([0-9]+)X([0-9]+)', re.IGNORECASE)
    s += '\n\n'  # for make possible to detect end of data

    def add_block():
        nonlocal in_block, dict_block_size, dict_block_data, block_num_tmp, block_tmp, block_size_x, block_size_y
        in_block = False
        #    block_size[1] = (x,y) of "BLOCK#1 xXy"
        dict_block_size[block_num_tmp] = (block_size_x, block_size_y)
        #    block_data[1] = body data of "BLOCK#1 xXy"
        dict_block_data[block_num_tmp] = np.array(block_tmp, dtype=int)
        if dict_block_data[block_num_tmp].shape != (block_size_y, block_size_x):
            raise RuntimeError('check-Q3: inconsistent block size', block_num_tmp, (block_size_x, block_size_y),
                               dict_block_data[block_num_tmp])
        block_num_tmp = 0
        block_tmp = []

    for line in s.splitlines():
        input_line_cnt += 1
        line = line.strip()
        if debug:
            print(in_block, line)
        if line == '':
            if in_block:  # end of BLOCK definition
                add_block()
            continue
        m = pSIZE.match(line)
        if m:
            size = [int(n) for n in m.groups()]
            if not ([1, 1] <= size <= [72, 72]):
                raise RuntimeError('check-Q4: invalid size', line)
            continue
        m = pBLOCK_NUM.match(line)
        if m:
            block_num = int(m.group(1))
            continue
        m = pBLOCK.match(line)
        if m:
            if in_block:
                add_block()
            in_block = True
            block_num_tmp, block_size_x, block_size_y = [int(n) for n in m.groups()]
            if 1 <= block_num_tmp <= block_num:
                continue
            else:
                raise RuntimeError('check-Q5: invalid block number', block_num_tmp, block_num)
        if in_block:
            tmp = []
            for c in line.split(','):
                # c = '+' or string of number('0', '1', .., '99' ...)
                c = c.strip()
                if c == '+':
                    r = -1  # block_without_number
                else:
                    r = int(c)  # 0=not_block, others=block_with_number
                tmp.append(r)
                num_lines = max(num_lines, r)
            block_tmp.append(tmp)
            continue
        raise RuntimeError('check-Q7: unknown line', input_line_cnt, line)

    # convert dict to list
    if not ((len(dict_block_size) == block_num) and
            (len(dict_block_data) == block_num)):
        raise RuntimeError('check-Q6: inconsistent block definition', block_num, len(dict_block_size),
                           len(dict_block_data))
    block_size = [None] * (block_num + 1)
    block_data = [None] * (block_num + 1)
    block_type = [None] * (block_num + 1)
    for i in range(1, block_num + 1):
        try:
            block_size[i] = dict_block_size[i]
            block_data[i] = dict_block_data[i]
        except KeyError:
            raise RuntimeError('check-Q8: BLOCK# not found', i)

    # check1. numbers: each number should appear twice.
    # check2. block shape: it must be tetromino or monomino
    num_count = np.zeros(num_lines + 1, dtype=int)
    for j, blk in enumerate(block_data[1:]):  # [0] is dummy, None
        for i in blk.ravel():
            if 0 <= i:
                num_count[i] += 1
        blk_type = match_block_shape(blk)
        if blk_type is None:
            raise RuntimeError('check-Q2: unknown block shape', blk)
        block_type[j + 1] = blk_type  # j = 0,1,2...
    # print('num_count', num_count)
    if not np.all(num_count[1:] == 2):
        raise RuntimeError('check-Q1: all numbers must appear twice', num_count)

    return size, block_num, block_size, block_data, block_type, num_lines


def generate_Q_data(Q):
    """
    問題のテキストデータを生成する。改行コードはCR+LFとする。

    Parameters
    ==========
    Q : tuple
        read_Q()の返り値

    Returns
    =======
    txt : str
        問題のテキストデータ
    """
    crlf = '\r\n'  # DOSの改行コード
    size, block_num, block_size, block_data, block_type, num_lines = Q
    txt = 'SIZE %dX%d%s' % (size[0], size[1], crlf)
    txt += 'BLOCK_NUM %d%s' % (block_num, crlf)
    for i in range(1, block_num+1):
        txt += crlf
        txt += 'BLOCK#%d %dX%d%s' % (i, block_size[i][0], block_size[i][1], crlf)
        for row in block_data[i]:
            txt += ','.join(['+' if n == -1 else str(n) for n in row]) + crlf

    return txt

def read_A_file(file):
    """
    read A file

    Parameters
    ----------
    file : str
        filename

    Returns
    -------
    read_A : tuple
         see :py:meth:`adc2019.read_A`
    """
    with open(file, 'r', newline=None) as f:  # universal newlines mode
        s = f.read()
        return read_A(s)


def read_A(s):
    """
    read A data

    Parameters
    ----------
    s : str
        | A data is like
        | A0
        | SIZE 9X8
        | 0, 1, 1, 1, 1, 2, 2, 2, 2
        | 0, 0, ...

    Returns
    -------
    aid : int
        id of A
    size : tuple
        For example (9,8) in case of 'SIZE 9X8'

    ban_data : numpy array
        board data

    block_pos : dict
    """
    global debug
    input_line_cnt = 0
    size = (0, 0)  # (x,y)
    in_size = False
    ban_data = []
    dict_block_pos = {}
    aid=None
    pAID = re.compile(r'A([0-9]+)', re.IGNORECASE)
    pSIZE = re.compile(r'SIZE\s+([0-9]+)X([0-9]+)', re.IGNORECASE)
    pBLOCK = re.compile(r'BLOCK\s*#\s*([0-9]+)\s+@\s*\(\s*([0-9]+)\s*,\s*([0-9]+)\s*\)', re.IGNORECASE)
    for line in s.splitlines():
        input_line_cnt += 1
        line = line.strip()
        if debug:
            print(in_size, line)
        if line == '':
            if in_size:
                if 0 < len(ban_data):
                    in_size = False
            continue

        m = pAID.match(line)
        if m:
            in_size = False
            aid = int(m.group(1))
            continue

        m = pSIZE.match(line)
        if m:
            if in_size:
                raise RuntimeError('check-A1: syntax error in SIZE')
            in_size = True
            size = [int(n) for n in m.groups()]
            if not (1 <= size[0] <= 72 and
                    1 <= size[1] <= 72):
                raise RuntimeError('check-A2: invalid size', line)
            continue

        m = pBLOCK.match(line)
        if m:
            in_size = False
            b, x, y = [int(i) for i in m.groups()]
            if b in dict_block_pos:
                raise RuntimeError('check-A3: duplicated BLOCK#', b, line)
            if size == (0, 0):
                raise RuntimeError('check-A4: SIZE not found')
            if not (0 <= x < size[0] and
                    0 <= y < size[1]):
                raise RuntimeError('check-A5: invalid block position', line)
            dict_block_pos[b] = (x, y)
            continue
        if in_size:
            # Issues#17 https://github.com/dasadc/dasadc.github.io/issues/17
            line2 = line.replace('+', '-1')
            try:
                ban_data.append([int(n) for n in line2.split(',')])
            except ValueError:
                raise RuntimeError('check-A6: syntax error', input_line_cnt, line)
            continue

        raise RuntimeError('check-A6: unknown line', input_line_cnt, line)

    block_num = len(dict_block_pos)
    if in_size or block_num == 0:
        raise RuntimeError('check-A7: BLOCK not found')
    block_pos = [None] * (block_num + 1)  # type: List[(int, int)]
    for i in range(1, block_num + 1):
        try:
            block_pos[i] = dict_block_pos[i]
        except KeyError:
            raise RuntimeError('check-A8: BLOCK# not found', i)
    ban_data = np.array(ban_data, dtype=int)
    if ban_data.shape != (size[1], size[0]):
        raise RuntimeError('check-A9: size mismatch', size, ban_data.shape[::-1])

    if aid is None:
        raise RuntimeError('check-A10: Answer ID should be specified')
    if aid <= 0:
        raise RuntimeError('check-A11: Answer ID should be >= 1')

    return aid, size, ban_data, block_pos


def match_block_shape(npb):
    """
    from numpy array block data, detect block shape type.

    Parameters
    ----------
    npb : numpy array
        one of elements of block_data returned from read_Q()

    Returns
    -------
    k : tuple  (type, index)
        type is string, {'a', 'b', ... 'g'}
        index is int, {0, 1, 2, 3}
    """
    for k, mat in np_block.items():
        if mat.shape == npb.shape:
            if np.all(mat * npb == npb):
                return k
    return None


def detect_terminal(n_lines_Q, block_data_Q, block_pos_A):
    """
    detect start and end point of number-lines

    Parameters
    ----------
    n_lines_Q : int
        number of lines

    block_data_Q : list of numpy array
        block shape data

    block_pos_A  : list of tupple
        block position

    Returns
    -------
    terminal : list of dict

    Examples
    --------

    >>> terminal
    [[],
     [{'block': 1, 'xy': (1, 0)}, {'block': 4, 'xy': (4, 0)}],
     [{'block': 4, 'xy': (5, 0)}, {'block': 6, 'xy': (5, 4)}],
     [{'block': 3, 'xy': (0, 6)}, {'block': 5, 'xy': (6, 7)}],
     [{'block': 4, 'xy': (4, 1)}, {'block': 8, 'xy': (7, 4)}],
     [{'block': 6, 'xy': (3, 5)}, {'block': 7, 'xy': (2, 5)}],
     [{'block': 2, 'xy': (3, 3)}, {'block': 7, 'xy': (3, 4)}],
     [{'block': 1, 'xy': (1, 3)}, {'block': 2, 'xy': (2, 3)}],
     [{'block': 1, 'xy': (1, 2)}, {'block': 2, 'xy': (3, 2)}],
     [{'block': 3, 'xy': (1, 6)}, {'block': 7, 'xy': (1, 5)}],
     [{'block': 3, 'xy': (0, 4)}, {'block': 7, 'xy': (2, 4)}],
     [{'block': 5, 'xy': (4, 6)}, {'block': 6, 'xy': (4, 5)}]]

    terminal[0] is unused.
    """
    terminal = [[] for _ in range(n_lines_Q + 1)]  # type: List[List[Dict]]
    for b, blk in enumerate(block_data_Q):
        if b == 0:
            continue  # terminal[0] is dummy, None
        x, y = block_pos_A[b]
        for by, row in enumerate(blk):
            for bx, val in enumerate(row):
                if 1 <= val <= n_lines_Q:
                    info = {'block': b,
                            'xy': (x + bx, y + by)}
                    terminal[val].append(info)
    return terminal


def check_data(data_Q, data_A):
    """
    Check block position is correct in board data.
    Number in block definition must be equal to number in board data.
    Check Number Link puzzle rules.
    Calculate attribute values of DA Symposium Algotirim Design Contest.


    Parameters
    ----------
    data_Q : tuple
        return value of read_Q()

    data_A : tuple
        return value of read_A()[1:] (exclude 1st element aid)


    Returns
    -------
    info : dict
        several information of check results


    Examples
    --------

    >>> ban_data_A
    array([[ 0,  1,  1,  1,  1,  2,  2,  2,  2],
           [ 0,  0,  0,  0,  4,  0,  0,  0,  2],
           [ 0,  8,  8,  8,  4,  4,  4,  4,  2],
           [ 0,  7,  7,  6,  0,  0,  0,  4,  2],
           [10, 10, 10,  6,  0,  2,  0,  4,  2],
           [ 0,  9,  5,  5, 11,  2,  2,  2,  2],
           [ 3,  9,  0,  0, 11,  0,  0,  0,  0],
           [ 3,  3,  3,  3,  3,  3,  3,  0,  0]])

    >>> block_size_Q
    [None, (1, 4), (3, 2), (2, 3), (2, 2), (3, 2), (3, 2), (3, 2), (3, 2)]

    >>> block_pos_A
    [None, (1, 0), (2, 2), (0, 4), (4, 0), (4, 6), (3, 4), (1, 4), (5, 3)]
    
    >>> x,y = block_pos_A[1]
    
    >>> bx,by = block_size_Q[1]
    
    >>> x,y,bx,by
    (1, 0, 1, 4)

    >>> ban_data_A[y:(y+by), x:(x+bx)]
    array([[1],
           [0],
           [8],
           [7]])

    >>> block_data_Q[1]
    array([[ 1],
           [-1],
           [ 8],
           [ 7]])

    >>> ban_data_F
    array([[ 0,  1,  1,  1,  1,  2,  2,  2,  2],
           [ 0, -1,  0,  0,  4, -1,  0,  0,  2],
           [ 0,  8,  8,  8,  4,  4,  4,  4,  2],
           [ 0,  7,  7,  6, -1, -1, -1,  4,  2],
           [10, 10, 10,  6, -1,  2, -1,  4,  2],
           [-1,  9,  5,  5, 11,  2,  2,  2,  2],
           [ 3,  9,  0,  0, 11, -1, -1,  0,  0],
           [ 3,  3,  3,  3,  3,  3,  3,  0,  0]])
    """
    size_Q, block_num_Q, block_size_Q, block_data_Q, block_type_Q, n_lines_Q = data_Q
    size_A, ban_data_A, block_pos_A = data_A

    block_num_A = len(block_pos_A) - 1  # dummy data, block_pos_A[0]=None
    if not (block_num_A == len(block_size_Q) - 1 and
            block_num_A == len(block_data_Q) - 1):
        raise RuntimeError('check-QA1: number of block mismatch')

    # check-QA2: numbers on blocks in the board must be same as defined blocks.
    # check-QA3: block must not be overlapped.
    ban_check3 = np.zeros(ban_data_A.shape, dtype=int)
    ban_data_F = ban_data_A.copy()  # care for Issues#17
    for b in range(1, block_num_A + 1):
        key = block_type_Q[b]
        x, y = block_pos_A[b]
        w, h = block_size_Q[b]
        # print('block %d: xy(%d, %d) wh(%d, %d)' % (b, x, y, w, h))
        block_ban = ban_data_A[y:(y + h), x:(x + w)]
        block_ban_masked = block_ban * np_block[key]
        ban_check3[y:(y + h), x:(x + w)] += np_block[key]  # put block on ban_check3
        # Issues#17 https://github.com/dasadc/dasadc.github.io/issues/17
        # Replace -1 by 0
        tmp_block_Q = block_data_Q[b].copy()
        tmp_block_ban_masked = block_ban_masked.copy()
        tmp_block_Q[tmp_block_Q == -1] = 0
        tmp_block_ban_masked[tmp_block_ban_masked == -1] = 0
        # print(tmp_block_Q)
        # print(tmp_block_ban_masked)
        # print(tmp_block_Q == tmp_block_ban_masked)
        # set -1 where cells should be -1 rather than 0
        block_ban_F = block_ban.copy()
        block_ban_F[block_data_Q[b] == -1] = -1
        ban_data_F[y:(y + h), x:(x + w)] = block_ban_F
        if not np.all(tmp_block_Q == tmp_block_ban_masked):
            raise RuntimeError('check-QA2: inconsistent numbers on block', b, (x, y), block_data_Q[b], block_ban_masked)

    if not np.all(ban_check3 <= 1):
        raise RuntimeError('check-QA3: block overlapped', ban_check3)

    terminal = detect_terminal(n_lines_Q, block_data_Q, block_pos_A)
    ban_count, ban_corner, _, _, _, _ = count_neighbors(ban_data_A)
    line_length, line_corner = check_lines(ban_data_A, terminal, ban_count, ban_corner, n_lines_Q)
    x0, y0, x1, y1 = bounding_box(ban_data_F)
    # Aの面積は、Qの面積以下であること issues#26
    if (size_Q[0] * size_Q[1]) < (size_A[0] * size_A[1]):
        raise RuntimeError('check-QA4: A-area oversized', size_Q, size_A)
    info = {'terminal': terminal,
            'count': ban_count,
            'corner': ban_corner,
            'line_length': line_length,
            'line_corner': line_corner,
            'area': (x1 - x0) * (y1 - y0),
            'dim': (x0, y0, x1, y1),
            'ban_data_F': ban_data_F}
    return info


def count_neighbors(a):
    """count

    count number of cells in neighbors

    Examples
    --------

    | □…target  Ｘ…neighbor
    | 
    |    Ｘ           N
    |  Ｘ□Ｘ        W□E
    |    Ｘ           S
    |                     4C2 = 6
    | (線の折れ曲がり) = (接続数=2) && (直線で突き抜けている場合を除く)
    | ■      ■      ■□      □■
    | □■    ■□      ■      ■
    | 
    | (直線で突き抜けている場合) = north_eq && south_eq || west_eq && north_eq
    | ■      ■□■
    | □
    | ■

    Parameters
    ----------
    a : numpy array
        board data

    Returns
    -------
    count    : numpy array
       number of cells located in neighbor(E,N,W,S) with same number
    corner   : numpy array
       1 = corner of line
    east_eq  : numpy array
       0 = cell has same number with east cell. 1 = not
    north_eq : numpy array
       0 = cell has same number with north cell. 1 = not
    west_eq  : numpy array
       0 = cell has same number with west cell. 1 = not
    south_eq : numpy array
       0 = cell has same number with south cell. 1 = not

    Examples
    --------

    >>> a
    array([[ 0,  1,  1,  1,  1,  2,  2,  2,  2],
           [ 0,  0,  0,  0,  4,  0,  0,  0,  2],
           [ 0,  8,  8,  8,  4,  4,  4,  4,  2],
           [ 0,  7,  7,  6,  0,  0,  0,  4,  2],
           [10, 10, 10,  6,  0,  2,  0,  4,  2],
           [ 0,  9,  5,  5, 11,  2,  2,  2,  2],
           [ 3,  9,  0,  0, 11,  0,  0,  0,  0],
           [ 3,  3,  3,  3,  3,  3,  3,  0,  0]])
    
    >>> count
    array([[0, 1, 2, 2, 1, 1, 2, 2, 2],
           [0, 0, 0, 0, 1, 0, 0, 0, 2],
           [0, 1, 2, 1, 2, 2, 2, 2, 2],
           [0, 1, 1, 1, 0, 0, 0, 2, 2],
           [1, 2, 1, 1, 0, 1, 0, 1, 2],
           [0, 1, 1, 1, 1, 2, 2, 2, 2],
           [1, 1, 0, 0, 1, 0, 0, 0, 0],
           [2, 2, 2, 2, 2, 2, 1, 0, 0]])
    
    >>> corner
    array([[0, 0, 0, 0, 0, 0, 0, 0, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 1, 0, 0, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [1, 0, 0, 0, 0, 0, 0, 0, 0]])
    
    >>> east_eq
    array([[0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 0, 1, 1, 1, 0, 0],
           [0, 1, 0, 0, 0, 0, 0, 0, 0],
           [1, 1, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 0, 0, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [1, 1, 1, 1, 1, 1, 0, 0, 0]])
    
    >>> north_eq
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 1],
           [0, 0, 0, 0, 1, 0, 0, 0, 1],
           [0, 0, 0, 0, 0, 0, 0, 1, 1],
           [0, 0, 0, 1, 0, 0, 0, 1, 1],
           [0, 0, 0, 0, 0, 1, 0, 0, 1],
           [0, 1, 0, 0, 1, 0, 0, 0, 0],
           [1, 0, 0, 0, 0, 0, 0, 0, 0]])
    
    >>> west_eq
    array([[0, 0, 1, 1, 1, 0, 1, 1, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 1, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 0, 0, 1, 1, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 1, 1, 1, 1, 0, 0]])
    
    >>> south_eq
    array([[0, 0, 0, 0, 0, 0, 0, 0, 1],
           [0, 0, 0, 0, 1, 0, 0, 0, 1],
           [0, 0, 0, 0, 0, 0, 0, 1, 1],
           [0, 0, 0, 1, 0, 0, 0, 1, 1],
           [0, 0, 0, 0, 0, 1, 0, 0, 1],
           [0, 1, 0, 0, 1, 0, 0, 0, 0],
           [1, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    """
    h, w = a.shape
    a_east = np.zeros(a.shape, a.dtype)
    a_north = np.zeros(a.shape, a.dtype)
    a_west = np.zeros(a.shape, a.dtype)
    a_south = np.zeros(a.shape, a.dtype)
    a_east[0:h, 0:(w - 1)] = a[0:h, 1:w]  # shift west  by 1
    a_north[1:h, 0:w] = a[0:(h - 1), 0:w]  # shift south by 1
    a_west[0:h, 1:w] = a[0:h, 0:(w - 1)]  # shift east  by 1
    a_south[0:(h - 1), 0:w] = a[1:h, 0:w]  # shift north by 1
    east_eq = ((a != 0) & (a == a_east)).astype(int)
    north_eq = ((a != 0) & (a == a_north)).astype(int)
    west_eq = ((a != 0) & (a == a_west)).astype(int)
    south_eq = ((a != 0) & (a == a_south)).astype(int)
    count = east_eq + north_eq + west_eq + south_eq
    corner = ((count == 2) & ~(((west_eq + east_eq) == 2) | ((north_eq + south_eq) == 2))).astype(
        int)  # 論理最適化して、式を簡単にできるかも?

    return count, corner, east_eq, north_eq, west_eq, south_eq


def check_lines(ban_data, terminal, count, corner, n_lines):
    """
    - check-A10: 数字マスは、線の端点である。昔のnlcheck.pyのcheck_3に相当。
    - check-A11: 線は枝分かれしない。昔のnlcheck.pyのcheck_4に相当。
    - check-A12: 線はつながっている。昔のnlcheck.pyのcheck_5に相当。
    - 線の長さを計算する。
    - 線の折れ曲がり回数を計算する。

    Parameters
    ----------
    ban_data : numpy array
        board data

    terminal : list of dict
        given from detect_terminal

    count : numpy array
        given from count_neighbors

    corner : numpy array
        given from count_neighbors

    n_lines : int
        number of lines


    Returns
    -------
    line_length : numpy array
        length of lines

    line_corner : numpy array
        number of corners of lines


    Raises
    ------
    RuntimeError
        a condition is not satisfied.
    """
    line_length = np.zeros((n_lines + 1), dtype=int)
    line_corner = np.zeros((n_lines + 1), dtype=int)
    for line in range(1, n_lines + 1):
        bit = (ban_data == line).astype(int)  # bitmap of the line
        mat = count * bit  # count map masked by the line
        dat = bit * line  # view of the line
        for i in range(2):
            xy = terminal[line][i]['xy']
            if count[xy[1], xy[0]] != 1:
                raise RuntimeError('check-A10: not terminal', line, xy)
        if np.all(mat <= 2):
            pass  # 枝分かれしていないのでOK
        else:
            # 3以上のマスと接続しているということは、枝分かれしている
            raise RuntimeError('check-A11: line is branched', line, dat)
        if 3 <= (mat == 1).sum():
            # 端点(接続数が1のマス)が、3個以上あるということは、線は非連結である
            raise RuntimeError('check-A12: line is disjoint', line, dat)
        line_length[line] = bit.sum()
        line_corner[line] = (bit * corner).sum()
    return line_length, line_corner


def bounding_box(a):
    """
    ignore all-zero rows and columns and get bounding box of array

    Parameters
    ----------
    a : numpy array
        array

    Returns
    -------
    x0, y0, x1, y1 : tuple of int
        (x0,y0) = left-top
        (x1,y1) = right bottom

    """
    hi, wi = a.shape
    n = 1
    while np.all(a[0:n] == 0):
        n += 1
    y0 = n - 1  # nまで進んだらゼロ行列ではないので、1つ戻る(-1)
    s = 1
    while np.all(a[(hi - s):hi] == 0):
        s += 1
    y1 = hi - (s - 1)
    w = 1
    while np.all(a[:, 0:w] == 0):
        w += 1
    x0 = w - 1
    e = 1
    while np.all(a[:, (wi - e):wi] == 0):
        e += 1
    x1 = wi - (e - 1)
    return x0, y0, x1, y1


def check(Q_file, A_file):
    """
    Parameters
    ----------

    Q_file : None or [str]
        filename of Q text file

    A_file : None or [str]
        filename of A text file

    Returns
    -------
    check_data : dict
       see :py:meth:`adc2019.check_data`
    """
    global debug
    Q = None
    A = None
    if Q_file:
        Q = read_Q_file(Q_file[0])
    if A_file:
        A = read_A_file(A_file[0])
    if Q and A:
        return check_data(Q, A[1:])


def main():
    """
    command line interface
    """
    global debug, verbose
    import argparse
    parser = argparse.ArgumentParser(
        description="DA Symposium 2019 Algorithm Design Contest, Command Line Interface tool")
    parser.add_argument('--debug', action='store_true', help='enable debug mode')
    parser.add_argument('--verbose', action='store_true', help='verbose message')
    parser.add_argument('--report', action='store_true', help='output detailed report')
    parser.add_argument('--Q-file', '-Q', nargs=1, help='Q filename')
    parser.add_argument('--A-file', '-A', nargs=1, help='A filename')
    args = parser.parse_args()
    # print(args); sys.exit(1)
    debug = args.debug
    verbose = args.verbose
    if args.Q_file is None and args.A_file is None:
        return None
    try:
        info = check(args.Q_file, args.A_file)
    except Exception as e:
        if verbose or debug:
            raise e
        else:
            print('ADC2020 rule violation')
            for i in e.args:
                print(i)
            return False
    if args.Q_file is None or args.A_file is None:
        return True
    quality = 1.0 / float(info['area'])
    print(quality)
    if args.report:
        for k, v in info.items():
            print('%s:' % k)
            print(v)
    return quality


if __name__ == '__main__':
    main()
