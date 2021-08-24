#  coding: utf-8
#
# Copyright (C) 2019, 2021 IPSJ DA Symposium

"""
Using Google Datastore
======================

See also:
https://github.com/googleapis/python-datastore


kind
----

- 'userinfo'        id = ユーザ名: str
- 'access_token'    id = ユーザ名: str
- 'q_data'
- 'log'
- 'clock'           id = 1(とくに意味はない)
- 'q_list_all'      id = round数 (1,2, 999)
- 'a_data'
"""

import logging
from google.cloud import datastore
from datetime import datetime
import random
import numpy as np

import adc2019
import adcutil
from adcconfig import YEAR
import main
from tz import gae_datetime_JST

#import argparse
#parser = argparse.ArgumentParser(description='')
#parser.add_argument('--anonymous', action='store_true', help='if set, use AnonymousCredentials')
#args, unknown = parser.parse_known_args()
#if args.anonymous:
#    global client
#    from google.auth.credentials import AnonymousCredentials
#    from os import getenv
#    client = datastore.Client(
#        credentials=AnonymousCredentials(),
#        project=getenv('PROJECT_ID')
#    )
#else:
#    client = datastore.Client()
from google.auth.credentials import AnonymousCredentials
from os import getenv
# https://github.com/googleapis/python-datastore/issues/11
if 0:
    # 2019年8月に必要だったworkaround
    client = datastore.Client(
        credentials=AnonymousCredentials(),
        project=getenv('PROJECT_ID')
    )
else:
    # 2020-08-21 バグ修正後
    client = datastore.Client()  # type: datastore.client.Client

def qdata_key(year=YEAR):
    "問題データのparent"
    return ndb.Key('Qdata', str(year))

def userlist_key():
    "UserInfoのparent"
    return ndb.Key('Users', 'all')


def p_userinfo(d):
    """
    property userinfo

    Parameters
    ----------
    d : list
        0:username      1:password       2:displayname         3:uid 4:gid

    Returns
    -------
    p : dict
    """

    return {'username': d[0],
            'password': d[1],
            'displayname': d[2],
            'uid': d[3],
            'gid': d[4]}


def get_userinfo(username):
    """
    ユーザー情報をデータベースから取り出す
    """
    key = client.key('userinfo', username)
    return client.get(key)


def get_username_list():
    "ユーザー名の一覧リストをデータベースから取り出す"
    query = client.query(kind='userinfo')
    users = query.fetch()
    res = []
    for u in users:
        res.append(u['username'])
    return res


def create_user(username, password, displayname, uid, gid, salt):
    """
    ユーザーをデータベースに登録
    """
    hashed = adcutil.hashed_password(username, password, salt)
    key = client.key('userinfo', username)
    entity = datastore.Entity(key=key)
    entity.update(p_userinfo([username, hashed, displayname, uid, gid]))
    client.put(entity)


def delete_user(username):
    """
    ユーザーをデータベースから削除する
    """
    key = client.key('userinfo', username)
    client.delete(key)


def change_password(username, password, salt):
    """
    ユーザーのパスワードを変更する。
    """
    info = get_userinfo(username)
    if info is None:
        return False
    info['password'] = adcutil.hashed_password(username, password, salt)
    client.put(info)
    return True
    

def create_access_token(username, password):
    """
    REST APIでのアクセス用トークンを生成して、データベースに保存する。

    Returns
    =======
    token : str
        トークン
    """
    key = client.key('access_token', username)
    entity = datastore.Entity(key=key)
    token = adcutil.hashed_password(username, password, str(datetime.now()))
    data = {'token': token}
    entity.update(data)
    client.put(entity)
    return token


def get_access_token(username):
    """
    REST APIでのアクセス用トークンを、データベースから取り出す。

    Returns
    =======
    token : str
        トークン
    """
    key = client.key('access_token', username)
    return client.get(key)


def check_access_token(username, token):
    """
    アクセス用トークンが正しいか、チェックする。
    """
    entity = get_access_token(username)
    #print('check_access_token: entity', entity)
    if token and entity and entity.get('token'): # Noneでは無い
        if entity.get('token') == token:
            return True
    return False


def delete_access_token(username, token):
    """
    アクセス用トークンを、データベースから削除する。
    """
    key = client.key('access_token', username)
    client.delete(key)


"""
問題データに関する処理
"""

def get_user_Q_list(author: str = None, round_count: int = None):
    """
    authorを指定して、問題データの一覧リストを返す。
    なぜか、射影クエリ(projection)でdateを取得すると、datetime型ではなくて数値に変換されてしまう。Unix epochからの秒数を1000*1000倍した値らしい。

    Parameters
    ----------
    author : str
        問題作成者の名前
    round_count : int, default None
        round数

    Returns
    -------
    list of dict

    Examples
    --------
    [{'linenum': 11,
      'cols': 10,
      'qnum': 2,
      'filename': 'sampleQ0.txt',
      'date': 1566473404341960,
      'rows': 10,
      'blocknum': 8},
     {'qnum': 1,
      'filename': 'sampleQ0.txt',
      'date': 1566474951262141,
      'rows': 10,
      'blocknum': 8,
      'linenum': 11,
      'cols': 10}]
    """
    query = query_q_data(round_count=round_count, author=author, projection=['round', 'qnum', 'blocknum', 'cols', 'rows', 'linenum', 'date', 'filename'])
    #query = query_q_data(round_count=round_count, author=author)
    query.order = ['qnum']
    return [dict(i) for i in query.fetch()]


def query_q_data(round_count: int = None, q_num: int = None, author: str = None, projection: list = None) -> datastore.query.Query:
    """
    q_dataエンティティを取得するためのクエリを作る。

    Parameters
    ----------
    round_count : int
        round数
    q_num : int
        指定したQ番号だけを取得したいとき
    author : str
        指定したauthorだけを取得したいとき
    projection : list of str
        射影クエリ。['qnum', 'author']など、取得したいプロパティを指定する。

    Returns
    -------
        クエリ : datastore.query.Query
    """
    query = client.query(kind='q_data')
    # InvalidArgument: 400 cannot use projection on a property with an equality filter を防止するために
    if projection is not None:
        projection_tmp = list(projection)  # copy
        try:  # for remove()
            if round_count is not None:
                projection_tmp.remove('round')
            if q_num is not None:
                projection_tmp.remove('qnum')
            if author is not None:
                projection_tmp.remove('author')
        except ValueError:
            pass
        #print('projection_tmp', projection_tmp)
        query.projection = projection_tmp
    #
    if round_count is not None:
        query.add_filter('round', '=', round_count)
    if q_num is not None:
        query.add_filter('qnum', '=', q_num)
    if author is not None:
        query.add_filter('author', '=', author)
    return query


def get_user_Q_data(round_count: int, q_num: int, author: str, fetch_num: int = 99) -> list[dict]:
    """
    round数, 問題番号, 作者名を指定して問題データをデータベースから取り出す

    Parameters
    ----------
    round_count : int
        round数
    q_num : int
        問題番号
    author : str
        問題作成者
    fetch_num : int, default 99
        取得する個数を制限する

    Returns
    -------
    list of dict
        dictに、問題データが入ってる。

    Examples
    --------

    {'date': datetime.datetime(2019, 8, 22, 10, 24, 18, 985829, tzinfo=<UTC>),
     'rows': 10,
     'blocknum': 8,
     'linenum': 11,
     'cols': 10,
     'text': 'SIZE 10X10\r\nBLOCK_NUM 8\r\n\r\nBLOCK#1 1X4\r\n1\r\n+\r\n8\r\n7\r\n\r\nBLOCK#2 3X2\r\n0,8,0\r\n7,6,+\r\n\r\nBLOCK#3 2X3\r\n10,0\r\n+,0\r\n3,9\r\n\r\nBLOCK#4 2X2\r\n1,2\r\n4,+\r\n\r\nBLOCK#5 3X2\r\n11,+,+\r\n0,0,3\r\n\r\nBLOCK#6 3X2\r\n0,+,2\r\n5,11,0\r\n\r\nBLOCK#7 3X2\r\n0,10,6\r\n9,5,0\r\n\r\nBLOCK#8 3X2\r\n+,+,0\r\n0,+,4\r\n',
     'qnum': 1,
     'author': 'administrator',
     'filename': 'sampleQ0.txt'}
    """
    logging.debug('get_user_Q_data: round=%d, Q=%d, author=%s, fetch=%d', round_count, q_num, author, fetch_num)
    query = query_q_data(round_count=round_count, q_num=q_num, author=author)
    q = query.fetch(fetch_num)  # 存在するなら、高々、1個
    return [dict(i) for i in list(q)]


def set_Q_data(round_count: int, q_num: int, q_text: str, author: str = 'DASymposium', filename: str = '', uniq: bool = True, update: bool = False) -> (bool, str, (int, int), int, int):
    """
    問題データをデータベースに登録する。

    Parameters
    ----------
    round_count : int
        round数
    q_num : int
        問題番号
    q_text : str
        問題データ
    author : str, default 'DASymposium'
        問題作成者の名前
    filename : str, default ''
        問題データのファイル名
    uniq : bool, default True
        update=Falseかつuniq=Trueのとき、q_numとauthorが重複する場合、登録は失敗する。
    update : bool, default False
        Trueのとき、問題データを変更する。すでに登録済みのデータを置き換える。

    Returns
    -------
    flag : bool
        True=OK、False=Error
    msg : str
        エラーメッセージなど
    size : tuple
        盤の大きさ (x,y) ……flag=Trueのとき
    block_num : int
        ブロック数 ……flag=Trueのとき
    num_lines : int
        線の本数 ……flag=Trueのとき
    """
    # 重複チェック
    if uniq and (not update):
        q = get_user_Q_data(round_count=round_count, q_num=q_num, author=author)
        print('q=', q)
        if 0 < len(q):
            return False, f'Error: User {author} R{round_count} Q{q_num} data already exists', None, None, None
    # 問題データの内容チェック
    try:
        Q = adc2019.read_Q(q_text)
    except RuntimeError as e:
        return False, 'Syntax Error: ' + str(e), None, None, None

    prop_q = p_qdata_from_Q(round_count, q_num, author, Q, filename)
    size, block_num, _, _, _, num_lines = Q
    flag = False
    if update:
        # updateのときは、既存のエンティティを取り出す
        query = query_q_data(round_count=round_count, q_num=q_num, author=author)
        entities = list(query.fetch())  # 存在するなら、高々、1個
        if len(entities) == 0:
            msg = 'Not updated. You should have used POST instead of PUT?'
        elif len(entities) == 1:
            entities[0].update(prop_q)
            client.put(entities[0])
            msg = 'Update OK'
            flag = True
        else:
            msg = f'Not updated: found {len(entities)} entities. May be internal system error'
    else:
        # 新規登録の場合
        #dat = datastore.Entity(client.key('q_data'), exclude_from_indexes=['text', 'blocknum', 'cols', 'rows', 'linenum', 'filename', 'date'])  # 
        dat = datastore.Entity(client.key('q_data'), exclude_from_indexes=['text'])  # projectionで指定するモノは、indexが必要らしい???
        dat.update(prop_q)
        client.put(dat)  # 登録する
        msg = 'Insert OK'
        flag = True
    #
    return flag, msg, size, block_num, num_lines


# def insert_Q_data(round_count: int, q_num: int, q_text: str, author: str = 'DASymposium', filename: str = '', uniq: bool = True) -> (bool, str, (int, int), int, int):
#     """
#     問題データをデータベースに登録する。

#     Parameters
#     ----------
#     round_count : int
#         round数

#     q_num : int
#         問題番号

#     q_text : str
#         問題データ

#     author : str, default 'DASymposium'
#         問題作成者の名前

#     filename : str, default ''
#         問題データのファイル名

#     uniq : bool, default True
#         uniq=Trueのとき、q_numとauthorが重複する場合、登録は失敗する。

#     Returns
#     -------
#     flag : bool
#         True=OK、False=Error
#     msg : str
#         エラーメッセージなど
#     size : tuple
#         盤の大きさ (x,y) ……flag=Trueのとき
#     block_num : int
#         ブロック数 ……flag=Trueのとき
#     num_lines : int
#         線の本数 ……flag=Trueのとき
#     """
#     # 重複チェック
#     if uniq:
#         q = get_user_Q_data(round_count, q_num, author)
#         if 0 < len(q):
#             return False, 'Error: User %s Q%d data already exists' % (author, q_num)
#     # 問題データの内容チェック
#     try:
#         Q = adc2019.read_Q(q_text)
#     except RuntimeError as e:
#         return False, 'Syntax Error: ' + str(e), None, None, None

#     prop_q = p_qdata_from_Q(round_count, q_num, author, Q, filename)
#     dat = datastore.Entity(client.key('q_data'), exclude_from_indexes=['text', 'blocknum', 'cols', 'rows', 'linenum', 'filename', 'date'])
#     dat.update(prop_q)
#     client.put(dat)  # 登録する

#     size, block_num, _, _, _, num_lines = Q
#     return True, 'OK', size, block_num, num_lines


# def update_Q_data(round_count: int, q_num: int, q_text: str, author: str = 'DASymposium', filename: str = '') -> (bool, str, (int, int), int, int):
#     """
#     問題データを変更する。すでに登録済みのデータを置き換える。

#     Parameters
#     ----------
#     round_count : int
#         round数

#     q_num : int
#         問題番号

#     q_text : str
#         問題データ

#     author : str, default 'DASymposium'
#         問題作成者の名前

#     filename : str, default ''
#         問題データのファイル名

#     Returns
#     -------
#     flag : bool
#         True=OK、False=Error
#     msg : str
#         エラーメッセージなど
#     size : tuple
#         盤の大きさ (x,y) ……flag=Trueのとき
#     block_num : int
#         ブロック数 ……flag=Trueのとき
#     num_lines : int
#         線の本数 ……flag=Trueのとき
#     """
#     # 問題データの内容チェック
#     try:
#         Q = adc2019.read_Q(q_text)
#     except RuntimeError as e:
#         return False, 'Syntax Error: ' + str(e)

#     prop = p_qdata_from_Q(round_count, q_num, author, Q, filename)
#     size, block_num, _, _, _, num_lines = Q

#     # 既存のエンティティを取り出す
#     query = query_q_data(round_count=round_count, q_num=q_num, author=author)
#     num = 0
#     for ent in query.fetch():  # 存在するなら、高々、1個
#         ent.update(prop)
#         client.put(ent)
#         num += 1
#     if num == 0:
#         msg = 'Not updated. You should have used POST instead of PUT?'
#     elif num == 1:
#         msg = 'Update OK'
#     else:
#         msg = 'Updated %d entities. May be internal system error' % num
#     return True, msg, size, block_num, num_lines


def delete_user_Q_data(round_count: int, q_num: int, author: str) -> str:
    """
    round数、qnum、authorを指定して、問題データをデータベースから削除する

    Parameters
    ----------
    round_count : int
        round数
    q_num : int
        問題番号
    author : str
        問題作成者

    Returns
    -------
    処理結果のメッセージ : str
    """
    # 既存のエンティティを取り出す
    query = query_q_data(round_count=round_count, q_num=q_num, author=author)
    num = 0
    for ent in query.fetch():  # 存在するなら、高々、1個
        client.delete(ent.key)
        num += 1
    if num == 0:
        msg = 'DELETE None'
    elif num == 1:
        msg = "DELETE /user/%s/Q/%d" % (author, q_num)
    else:
        msg = "DELETE /user/%s/Q/%d * %d times" % (author, q_num, num)
    return msg


def get_Q_data(round_count: int, q_num: int) -> dict:
    """
    出題の番号を指定して、Question問題データをデータベースから取り出す。

    Parameters
    ----------
    round_count : int
        round数
    q_num : int
        問題番号
    """
    qla = admin_Q_list_get(round_count)
    if qla is None:
        return None

    # q_numは1から始まる整数なので、配列のインデックスとは1だけずれる
    qn = q_num - 1
    q_key_list = qla['q_key_list']
    if qn < 0 or len(q_key_list) <= qn:
        return None
    key = q_key_list[qn]
    return dict(client.get(key))


def p_qdata_from_Q(round_count: int, q_num: int , author: str, Q: tuple, filename: str = '') -> dict:
    """
    問題データのプロパティを作る。

    Parameters
    ----------
    round_count : int
        round数
    q_num : int
        問題番号
    author : str
        問題データ作成者の名前
    Q : tuple
        return value of adc2019.read_Q()
    filename : str, default ''
        問題データのファイル名

    Returns
    -------
        プロパティ : dict
    """
    #size, block_num, block_size, block_data, block_type, num_lines = Q
    size, block_num, _, _, _, num_lines = Q

    # 正規化した問題テキストデータ（改行コードなど）
    q_text2 = adc2019.generate_Q_data(Q)

    return {'round':    round_count, # int
            'qnum':     q_num,       # int
            'text':     q_text2,     # string
            'blocknum': block_num,   # int
            'cols':     size[0],     # int
            'rows':     size[1],     # int
            'linenum':  num_lines,   # int
            'author':   author,      # string
            'filename': filename,    # string
            'date':     datetime.utcnow()}


def p_adata_from_A(round_count: int, a_num: int, owner: str, A: tuple, a_text: str, check_result: bool, quality: float, ainfo: dict):
    """
    回答データのプロパティを作る。

    Parameters
    ----------
    round_count : int
        round数
    a_num : int
        問題番号
    owner : str
        ユーザー名
    A : tuple
        return value of adc2019.read_A()
    a_text: str
        A text
    check_result : bool
        true = 正解
    quality : float
        階の品質
    ainfo : dict
        key = 'cpu_sec', 'mem_byte', 'misc_text'

    Returns
    -------
        プロパティ : dict
    """
    if A is None:
        size, ban_data, block_pos = [], [[]], []
    else:
        size, ban_data, block_pos = A
    size2 = list(size)
    # ban_data2 = [row.tolist() for row in ban_data]  # list of list
    ban_data2 = ban_data.ravel().tolist()  # list (flatten)
    block_pos2 = np.array(block_pos[1:]).ravel().tolist() # list (flatten)
    
    return {'round':     round_count, # int
            'anum':      a_num,       # int
            'text':      a_text,      # string
            'owner':     owner,       # string
            'size':      size2,       # [int, int]
            'ban_data':  ban_data2,   # [[int, ...], [...], ... ]
            'block_pos': block_pos2,  # [[int, int], [...], ...]
            'judge':     check_result, # bool
            'quality':   quality,      # float
            'ainfo':     ainfo,        # dict
            'date':      datetime.utcnow()}


class QuestionListAll():
    """
    コンテスト用の、出題問題リスト。Repeated Propetiyにしてみた

    qs = ndb.KeyProperty(kind=Question, repeated=True)
    text_admin = ndb.StringProperty('a', indexed=False)
    text_user = ndb.StringProperty('u', indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    """
    
class Answer():
    """
    回答データ

    anum = ndb.IntegerProperty(indexed=True)
    text = ndb.StringProperty(indexed=False)
    owner = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    # 回答データの補足情報
    cpu_sec = ndb.FloatProperty(indexed=False)
    mem_byte = ndb.IntegerProperty(indexed=False)
    misc_text = ndb.StringProperty(indexed=False)
    result = ndb.StringProperty()  # 採点結果
    judge = ndb.IntegerProperty()  # True=1=正解, False=0=不正解
    q_factor = ndb.FloatProperty() # 解の品質
    """


def log(username: str, what: str):
    """
    logを記録する。

    Parameters
    ----------
    username : str
        ユーザ名

    what : str
        ログメッセージ
    """
    d = {'username': username,
         'what': what,
         'timestamp': datetime.utcnow()}
    entity = datastore.Entity(key=client.key('log'), exclude_from_indexes=['what'])
    entity.update(d)
    client.put(entity)
         

def log_get_or_delete(username=None, fetch_num=100, when=None, delete=False):
    """
    logを、取り出す、または、消去する。
    """
    query = client.query(kind='log')
    query.order = ['-timestamp']
    if username:
        query.add_filter('username', '=', username)
    if when:
        before = datetime.utcnow() - when
        # print('before=', before)
        query.add_filter('timestamp', '>', before)
        fetch_num = None
    q = query.fetch(limit=fetch_num)
    results = []
    for i in q:
        tmp = {'date': gae_datetime_JST(i['timestamp']),
               'username': i['username'],
               'what': i['what']}
        results.append( tmp )
        if delete:
            client.delete(i.key)
    return results



"""
Time keeper

時計の時刻に基づいて、状態遷移させる。
"""

def timekeeper_key() -> datastore.key.Key:
    """
    Time keeperのCloud Datastore key

    - kind: 'clock'
    - name: 1 (とくに意味はない)
    """
    return client.key('clock', 1)


def timekeeper_prop(dt: datetime = None, state: str = 'init', enabled: int = 1, round_counter: int = 1) -> dict:
    """
    property of timekeeper (kind: 'clock')
    
    Parameters
    ----------
    dt : datetime
       last update time
    state : str
       state. ['init', 'im0', 'Qup', 'im1', 'Aup', 'im2']
    enabled : int, default 1
       enabled flag. 0=disabled, 1=enabled
    round_counter : int, default 1
       round counter. 1, 2, ...

    Returns
    -------
    dict
    """
    assert main.valid_state(state)
    if dt is None:
        dt = datetime.utcnow()
    return {'lastUpdate': dt,
            'state':      state,
            'enabled':    enabled,
            'round':      round_counter}


def timekeeper_clk() -> datastore.entity.Entity:
    """
    clkの値を返す。もし存在しない場合は、新規作成する。
    
    Returns
    -------
    datastore.entity.Entity
    """
    clk = None
    key = timekeeper_key()
    with client.transaction():
        clk = client.get(key)
        if clk is None:
            p = timekeeper_prop(datetime.utcnow(), 'init', 1)
            clk = datastore.Entity(key=key)
            clk.update(p)
            client.put(clk)
    return clk


def timekeeper_check() -> (str, str):
    """
    timekeeperがenabledのとき、
    前回時刻と今回時刻から、状態遷移させるかどうか、の判定を行う。

    Returns
    -------
    new_state : str
    old_state : str
    """
    new_state = None
    old_state = None
    clk = timekeeper_clk()
    with client.transaction():
        if clk['enabled'] == 0:
            return clk['state'], clk['state']

        now = datetime.utcnow()
        same_slot, new_state = timekeeper_transition(clk['lastUpdate'], now, clk['state'])
        old_state = clk['state']

        if not same_slot or clk['state'] != new_state:
            clk['lastUpdate'] = now
            clk['state'] = new_state
            client.put(clk)
            logging.debug('TimeKeeper: state change: %s', str(clk))
    return new_state, old_state


def timekeeper_enabled(new_value: int = None) -> int:
    """
    timekeeperのenabledの値を、取得する、または、設定する。

    Parameters
    ----------
    new_value : int, default None
        Noneのときは、値を取得する。
        Noneでないときは、値を設定する。

    Returns
    -------
        enabledの値 : int
    """
    clk = timekeeper_clk()
    if new_value is None:
        return clk['enabled']
    else:
        if new_value == 0:
            enabled = 0
        else:
            enabled = 1
        if enabled != clk['enabled']:
            clk['enabled'] = enabled
            clk['lastUpdate'] = datetime.utcnow()
            client.put(clk)
        return enabled


def timekeeper_state(new_value :str = None) -> str:
    """
    timekeeperのstateの値を、取得する、または、設定する。

    Parameters
    ----------
    new_value : str, default None
        Noneのときは、値を取得する。
        Noneでないときは、値を設定する。

    Returns
    -------
        stateの値 : str
    """
    clk = timekeeper_clk()
    if new_value is None:
        return clk['state']
    else:
        if main.valid_state(new_value):
            if new_value != clk['state']:
                clk['state'] = new_value
                clk['lastUpdate'] = datetime.utcnow()
                client.put(clk)
        return clk['state']


def timekeeper_round(new_value :int = None) -> int:
    """
    timekeeperのroundカウンタの値を、取得する、または、設定する。

    Parameters
    ----------
    new_value : int, default None
        Noneのときは、値を取得する。
        Noneでないときは、値を設定する。

    Returns
    -------
        roundカウンタの値 : int
    """
    clk = timekeeper_clk()
    if new_value is None:
        return clk.get('round')
    else:
        if new_value != clk.get('round'):
                clk['round'] = new_value
                clk['lastUpdate'] = datetime.utcnow()
                client.put(clk)
        return clk.get('round')


def timekeeper_set(value: dict = {}) -> dict:
    """
    timekeeperのstate, enabled, roundの値を、一度に設定する。
    """
    clk = timekeeper_clk()
    state = value.get('state')
    if main.valid_state(state):
        clk['state'] = state
    enabled = value.get('enabled')
    if enabled != 0:
        enabled = 1
    round_counter = value.get('round')
    if round_counter is None:
        round_counter = 999  # default値
    clk['enabled'] = enabled
    clk['lastUpdate'] = datetime.utcnow()
    clk['round'] = round_counter
    client.put(clk)
    logging.info('timekeeper_set: %s', str(clk))
    return dict(clk)


def timekeeper_transition(prev, now, prev_state) -> (bool, str):
    """
    時刻に基づいて、次の状態を返す。

    Parameters
    ----------
    prev       : datetime

    now        : datetime

    prev_state : str
        前回の状態変数の値

    Returns
    -------
    same_slot : bool
        前回時刻と今回時刻は、同じスロットである。
        同じスロットとは、時刻 HH:MM:SS のHHが同じ場合のこと。
        つまり、1時間ごとに繰り返す状態遷移の系列で、同じ１時間内にとどまっている。

    new_state : str
        次の状態
    """
    if (prev.year  == now.year  and
        prev.month == now.month and
        prev.day   == now.day   and
        prev.hour  == now.hour):
        same_slot = True
    else:
        same_slot = False
    m = now.minute
    mQup = 3   # HH:03:00-HH:14:59 ... 問題アップロード可能／出題リストを削除;回答データを削除
    mim1 = 15  # HH:15:00-HH:19:59 ... 問題アップロード締め切り／出題リストを作成
    mAup = 20  # HH:20:00-HH:54:59 ... 回答アップロード可能
    mim2 = 55  # HH:55:00-HH:59:59 ... 回答アップロード締め切り
    if 0 <= m < mQup:
        new_state = 'im0'
    elif mQup <= m < mim1:
        new_state = 'Qup'
    elif mim1 <= m < mAup:
        new_state = 'im1'
    elif mAup <= m < mim2:
        new_state = 'Aup'
    elif mim2 <= m <= 59:
        new_state = 'im2'
    else:  # ありえない
        logging.warning('timekeeper_transition: BUG')
        new_state = 'BUG'
    logging.debug('same_slot=%s, prev_state=%s, new_state=%s', same_slot, prev_state, new_state)
    return same_slot, new_state


"""
出題リスト
"""

def admin_Q_list_get(round_count: int):
    """
    コンテストの出題リストを取り出す
    """
    key = client.key('q_list_all', round_count)
    qla = client.get(key)
    return qla


def admin_Q_list_create(round_count: int) -> (bool, str, datastore.entity.Entity):
    """
    コンテスト用の出題リストを作成する。

    Parameters
    ----------
    round: int, default  None
        roundカウンタの値
    """
    qla = admin_Q_list_get(round_count)
    if qla is not None:
        return False, 'Cannot create Q list, because it already exists', qla

    qlist = list(query_q_data(round_count=round_count, projection=['qnum', 'author', 'cols', 'rows', 'blocknum', 'linenum']).fetch())
    random.shuffle(qlist)
    out = '%d\n' % len(qlist)
    out_admin = ''
    out_user = ''
    qs = []
    q_num = []
    q_author = []
    q_author_qnum = []
    q_author = []
    q_author_qnum = []
    q_cols = []
    q_rows = []
    q_blocknum = []
    q_linenum = []
    for j, ent in enumerate(qlist):
        num = j + 1  # Q1 Q2 Q3  --- 1から始まる
        qs.append(ent.key)
        q_num.append(num)
        q_author.append(ent['author'])
        q_author_qnum.append(ent['qnum'])
        q_cols.append(ent['cols'])
        q_rows.append(ent['rows'])
        q_blocknum.append(ent['blocknum'])
        q_linenum.append(ent['linenum'])
        out_admin += 'Q%d %s %d\n' % (num, ent['author'], ent['qnum'])
        out_user  += 'Q%d\n' % num
        num += 1
    out += out_admin
    prop = {'q_key_list': qs,
            'qnum_list': q_num,
            'author_list': q_author,
            'author_qnum_list': q_author_qnum,
            'text_admin': out_admin,
            'text_user':  out_user,
            'cols_list': q_cols,
            'rows_list': q_rows,
            'blocknum_list': q_blocknum,
            'linenum_list': q_linenum,
            'date': datetime.utcnow()}
    key = client.key('q_list_all', round_count)
    qla = datastore.Entity(key=key)  # qla means 'Q list all'
    qla.update(prop)
    client.put(qla)
    return True, out_admin, qla


def admin_Q_list_delete(round_count: int):
    """
    コンテストの出題リストを削除する。
    """
    key = client.key('q_list_all', round_count)
    client.delete(key)
    return 'DELETE Q-list'



# def get_Q_all(html=False):
#     """
#     問題データの一覧リストを返す。

#     Returns
#     =======
#     text : string
#         ただのテキストデータ。

#     Examples
#     ========
#     Q1
#     Q2
#     Q3
#     Q4
#     Q5
#     Q6
#     Q7
#     Q8
#     """
#     qla = admin_Q_list_get(round_count)
#     if qla is None:
#         return ''
#     return qla['text_user']



def post_A(round_count: int, username: str, atext: str, form) -> (bool, str):
    """
    post A
    """
    anum = (int)(form['anum'])
    cpu_sec = 0
    mem_byte = 0
    try:
        cpu_sec = (float)(form['cpu_sec'])
        mem_byte = (int)(form['mem_byte'])
    except ValueError:
        # (float)'' がエラー
        pass
    misc_text = form['misc_text']
    print('A%d\n%f\n%d\n%s' % (anum, cpu_sec, mem_byte, misc_text.encode('utf-8')))
    return put_A_data(round_count, anum, username, atext, cpu_sec, mem_byte, misc_text)



def get_admin_A_all(round_count: int) -> (str, list):
    """
    データベースに登録されたすべての回答データの一覧リスト
    """
    query = query_a_data(round_count=round_count)
    query.order = ['owner', 'anum']
    alist = list(query.fetch())
    out = '%d\n' % len(alist)
    dat = []
    for i in alist:
        # print('i=', i)
        if type(i['date']) is datetime:
            dt = gae_datetime_JST(i['date'])
        else:
            dt = gae_datetime_JST(datetime.fromtimestamp(i['date'] / 1e6))  # 射影クエリだと、なぜか数値が返ってくる
        out += 'A%02d (%s) %s\n' % (i['anum'], i['owner'], dt)
        dat.append(dict(i))
    return out, dat


def get_A_data(round_count: int, a_num: int = None, username: str = None):
    """
    データベースから回答データを取り出す。
    a_numがNoneのとき、複数のデータを返す。
    a_numが数値のとき、その数値のデータを1つだけ返す。
    """
    query = query_a_data(round_count=round_count, a_num=a_num, owner=username)
    return query.fetch()


def query_a_data(round_count: int, a_num: int = None, owner: str = None, projection: list = None) -> datastore.query.Query:
    """
    a_dataエンティティを取得するためのクエリ

    a_numがNoneのとき、複数のデータを返す。
    a_numが数値のとき、その数値のデータを1つだけ返す。
    """
    query = client.query(kind='a_data')
    if round_count is not None:
        query.add_filter('round', '=', round_count)
    if a_num is not None:
        query.add_filter('anum', '=', a_num)
    if owner is not None:
        query.add_filter('owner', '=', owner)
    if projection is not None:
        projection_tmp = list(projection)  # copy
        try:  # for remove()
            if round_count is not None:
                projection_tmp.remove('round')
            if a_num is not None:
                projection_tmp.remove('anum')
            if owner is not None:
                projection_tmp.remove('owner')
        except ValueError:
            pass
        query.projection = projection_tmp
    return query

    
def put_A_data(round_count: int, a_num: int, username: str, a_text: str, cpu_sec: float = 0, mem_byte: int = 0, misc_text: str = '') -> (bool, str):
    """
    put A, 回答データをデータベースに格納する
    """
    msg = ''
    # 重複回答していないかチェック
    adata = list(get_A_data(round_count=round_count, a_num=a_num, username=username))
    # print('adata', adata)
    if len(adata) != 0:
        msg += 'ERROR: duplicated answer\n';
        return False, msg
    # 出題データを取り出す
    q_dat = get_Q_data(round_count=round_count, q_num=a_num)
    if q_dat is None:
        msg = 'Error: Q%d data not found' % a_num
        return False, msg
    q_text = q_dat.get('text')
    if q_text is None:
        msg = 'Error: Q%d data not found' % a_num
        return False, msg
    try:
        Q = adc2019.read_Q(q_text)
    except RuntimeError as e:
        # 事前にチェック済みなので、ここでエラーになることはないはず
        Q = None
        return False, 'Error in Q%d\n' % a_num + str(e)
    # 回答データを読み込む
    try:
        A = adc2019.read_A(a_text)
    except RuntimeError as e:
        # print('e=', e)
        A = None
        msg = 'Error in A%d\n' % a_num + str(e)
    else:
        # 回答データ中の問題IDと、APIでの問題IDが異なったらエラー
        aid = A[0]
        A = A[1:]
        if a_num != aid:
            return False, "Error: Answer ID mismatch. API's ID is {}, but ID in A file is {}\n".format(a_num, aid)

    check_A = False
    quality = 0.0
    if Q and A:
        # 回答をチェック
        try:
            info = adc2019.check_data(Q, A)
        except RuntimeError as e:
            #print('put_A_data: e=', e)
            msg = 'Error A%d\n' % a_num + str(e)
        else:
            check_A = True # 正解
            quality = 1.0 / float(info['area']) # 解の品質
            msg += 'Quality factor = %1.19f\n' % quality

    # データベースに登録する。不正解でも登録する
    ainfo = {'cpu_sec': cpu_sec,
             'mem_byte': mem_byte,
             'misc_text': misc_text}
    prop_a = p_adata_from_A(round_count=round_count, a_num=a_num, owner=username, A=A, a_text=a_text, check_result=check_A, quality=quality, ainfo=ainfo)
    # print('prop_a', prop_a)
    #entity = datastore.Entity(key=client.key('a_data'), exclude_from_indexes=['text', 'size', 'ban_data', 'block_pos', 'judge', 'ainfo', 'date'])
    entity = datastore.Entity(key=client.key('a_data'), exclude_from_indexes=['text'])
    entity.update(prop_a)
    client.put(entity)
    return True, msg


def put_A_info(round_count: int, a_num: int , username: str, info: dict):
    """
    回答データの補足情報をデータベースに格納する。
    """
    msg = ''
    # 回答データを取り出す
    adata = list(get_A_data(round_count=round_count, a_num=a_num, username=username))
    if 0 == len(adata):
        return False, 'ERROR: put_A_info: record not found. A%d, %s' % (a_num, username)
    if 1 <  len(adata):
        # 複数が、条件にマッチした。>>> バグってる
        return False, 'BUG: put_A_info: %d record matched. A%d, %s' % (len(adata), a_num, username)

    adata[0]['ainfo'] = {'cpu_sec': info.get('cpu_sec'),
                         'mem_byte': info.get('mem_byte'),
                         'misc_text': info.get('misc_text')}
    client.put(adata[0])
    return True, 'UPDATE A%d info' % a_num



def get_or_delete_A_data(round_count: int = None, a_num: int = None, username: str = None, delete: bool = False):
    """
    回答データをデータベースから、取得する、または、削除する。
    """
    data = get_A_data(round_count=round_count, a_num=a_num, username=username)
    result = []
    for i in data:
        # print('get_or_delete_A_data: i=', i)
        if delete:
            result.append('DELETE A%d' % i['anum'])
            client.delete(i.key)
        else: # GETの場合
            result.append('GET A%d' % i['anum'])
            result.append(i['text'])
    return result


def get_user_A_all(round_count: int, username: str):
    """
    ユーザーを指定して、回答データの一覧リストを返す
    """
    q = get_A_data(round_count=round_count, username=username)
    text = ''
    anum_list = []
    for i in q:
        """
        print('i=', i)
        i= <Entity('a_data', 517)
           {'anum': 12,
            'ainfo': <Entity {'cpu_sec': 0, 'mem_byte': 0, 'misc_text': ''}>,
            'owner': 'administrator',
            'date': datetime.datetime(2019, 8, 25, 22, 28, 35, 353062, tzinfo=<UTC>),
            'ban_data': [1, 1, 1, 2, 2, -1, -1, 2, -1, -1, 2, 2],
            'quality': 0.08333333333333333,
            'text': 'SIZE 3X4\r\n1,1,1\r\n2,2,+\r\n+,2,+\r\n+,2,2\r\nBLOCK#1 @(0,0)\r\nBLOCK#2 @(2,0)\r\n',
            'size': [3, 4],
            'block_pos': [0, 0, 2, 0]}>
        """
        text += 'A%d\n' % i['anum']  # 'A12\n'
        anum_list.append(i['anum'])  # i['anum'] == 12
    return text, anum_list


def get_or_delete_A_info(round_count: int, a_num: int = None, username: str = None, delete: bool =False):
    """
    回答データの補足情報をデータベースから、取得する or 削除する。
    """
    data  = get_A_data(round_count=round_count, a_num=a_num, username=username)
    result = {}
    for i in data:
        # print('get_or_delete_A_info: i=', i)  # i = Entity
        result[i['anum']] = i.get('ainfo')
        if delete:
            if 'ainfo' in i:
                del i['ainfo']
            client.put(i)
    return result



def get_Q_author_all():
    "出題の番号から、authorを引けるテーブルを作る ---> もともとq_list_allに入ってるから不要"
    qla = ndb.Key(QuestionListAll, 'master', parent=qdata_key()).get()
    if qla is None:
        return None
    authors = ['']*(len(qla.qs)+1) # q_numは1から始まるので、+1しておく
    qn = 1 # 出題番号
    for q_key in qla.qs:
        q = q_key.get()
        authors[qn] = q.author
        qn += 1
        # q.qnum は、問題登録したときの番号であり、出題番号ではない
    return authors


def get_admin_Q_all(round_count: int = None) -> str:
    """
    データベースに登録されたすべての問題の一覧リストを返す。

    Parameters
    ----------
    round_count : int
        round数
    """
    query = query_q_data(round_count=round_count, projection=['round', 'qnum', 'author', 'cols', 'rows', 'blocknum', 'linenum', 'date'])
    query.order = ['author', 'round', 'qnum']
    qlist = list(query.fetch())
    out = '%d\n' % len(qlist)
    for i in qlist:
        # print('i=', i)
        dt = gae_datetime_JST(datetime.fromtimestamp(i['date'] / 1e6))  # 射影クエリだと、なぜか数値が返ってくる
        out += 'R%d Q%02d SIZE %dX%d BLOCK_NUM %d LINE_NUM %d (%s) %s\n' % (i['round'], i['qnum'], i['cols'], i['rows'], i['blocknum'], i['linenum'], i['author'], dt)
    return out
    

def delete_admin_Q_all() -> str:
    """
    データベースに登録されたすべての問題データを削除する。
    """
    query = query_q_data()
    qlist = list(query.fetch())
    out = ''
    for i in qlist:
        # print('i=', i)
        out += 'R%d Q%02d SIZE %dX%d BLOCK_NUM %d LINE_NUM %d (%s) %s\n' % (i['round'], i['qnum'], i['cols'], i['rows'], i['blocknum'], i['linenum'], i['author'], i['date'])
        client.delete(i.key)
    return out
    


def calc_score_all(round_count: int):
    """
    スコア計算
    """
    qla = admin_Q_list_get(round_count)
    adata = query_a_data(round_count=round_count).fetch()

    authors = [None]
    if qla:
        authors = [None] + qla.get('author_list')  # Q1から始まるので1つずらす

    ok_point = {}     # ok_point   [番号][ユーザ名] = 0, 1
    q_factors = {}    # q_factors  [番号][ユーザ名] = 小数の値
    q_point = {}      # q_point    [番号][ユーザ名] = 値
    bonus_point = {}  # bonus_point[番号][ユーザ名] = 0, 1=出題ボーナスをもらえる
    misc = {}         # misc       [番号][ユーザ名] = list
    all_numbers = {}  # すべて数え上げる
    all_users = {}    # すべて数え上げる

    for i in adata:
        anum = 'A%02d' % i['anum']
        username = i['owner']
        all_numbers[anum] = 1
        all_users[username] = 1
        # 正解ポイント
        if anum not in ok_point:
            ok_point[anum] = {}
        ok_point[anum][username] = int(i['judge'])  # True, False --> 1, 0
        # 品質ポイント
        if username != 'ADC-0':
            if anum not in q_factors:
                q_factors[anum] = {}
            q_factors[anum][username] = i['quality']
        # 出題ボーナスポイント
        if int(i['judge']) in (0, 1) and authors[i['anum']] == username:
            # print('check_bonus:', i['anum'], i['judge'], authors[i['anum']], username)
            if anum not in bonus_point:
                bonus_point[anum] = {}
            bonus_point[anum][username] = int(i['judge'])
        # (その他) date, cpu_sec, mem_byte, misc_text
        if not(anum in misc):
            misc[anum] = {}
        ainfo = i['ainfo']
        misc[anum][username] = [i['date'], ainfo['cpu_sec'], ainfo['mem_byte'], ainfo['misc_text']]
    # 品質ポイントを計算する
    q_pt = 10.0
    for anum, values in q_factors.items():  # 問題番号ごとに
        qf_total = sum(values.values())  # Q_factorの合計
        for user, qf in values.items():
            if qf_total == 0.0:
                tmp = 0.0
            else:
                tmp = q_pt * qf / qf_total
            # 品質ポイントをセットする
            if not anum in q_point:
                q_point[anum] = {}
            q_point[anum][user] = tmp
    # 集計する
    tmp = ['']*(len(all_numbers) + 1)
    i = 0
    for anum in sorted(all_numbers.keys()):
        tmp[i] = anum
        i += 1
    tmp[i] = 'TOTAL'
    score_board = {'/header/': tmp} # 見出しの行
    for user in sorted(all_users.keys()):
        if not(user in score_board):
            score_board[user] = [0]*(len(all_numbers) + 1)
        i = 0
        ptotal = 0.0
        for anum in sorted(all_numbers.keys()):  # ['A13', 'A15', 'A16']
            p = 0.0
            p += ok_point[anum].get(user, 0)
            if anum in q_point:
                p += q_point[anum].get(user, 0)
            p += bonus_point.get(anum, {}).get(user, 0)
            score_board[user][i] = p
            ptotal += p
            i += 1
        score_board[user][i] = ptotal
    #print "score_board=", score_board
    return score_board, ok_point, q_point, bonus_point, q_factors, misc
