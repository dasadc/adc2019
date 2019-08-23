#  coding: utf-8
#
# Copyright (C) 2019 IPSJ DA Symposium

from google.cloud import datastore
from datetime import datetime

import adc2019
import adcutil
from adcconfig import YEAR
from tz import gae_datetime_JST


client = datastore.Client()


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

def get_user_Q_list(author):
    """
    authorを指定して、問題データの一覧リストを返す。
    なぜか、射影クエリでdateを取得すると、datetime型ではなくて数値に変換されてしまう。Unix epochからの秒数を1000*1000倍した値らしい。

    Examples
    ========
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
    query = query_q_data(author=author, projection=['qnum', 'blocknum', 'cols', 'rows', 'linenum', 'date', 'filename'])
    query.order = ['qnum']
    return [dict(i) for i in query.fetch()]


def query_q_data(q_num=None, author=None, projection=None):
    """
    q_dataエンティティを取得するためのクエリ

    Parameters
    ==========
    q_num : int
        指定したQ番号だけを取得したいとき
    author : str
        指定したauthorだけを取得したいとき
    projection : list of str
        射影クエリ。['qnum', 'author']など、取得したいプロパティを指定する。
    """
    query = client.query(kind='q_data')
    if q_num:
        query.add_filter('qnum', '=', q_num)
    if author:
        query.add_filter('author', '=', author)
    if projection:
        query.projection = projection
    return query


def get_user_Q_data(q_num, author, fetch_num=99):
    """
    qnumとauthorを指定して問題データをデータベースから取り出す

    Returns
    =======
    d : list of dict
        dictに、問題データが入ってる。

    Examples
    ========

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
    query = query_q_data(q_num=q_num, author=author)
    q = query.fetch(fetch_num)  # 存在するなら、高々、1個
    return [dict(i) for i in list(q)]


def insert_Q_data(q_num, q_text, author='DASymposium', filename='', uniq=True):
    """
    問題データをデータベースに登録する。
    uniq==Trueのとき、q_numとauthorが重複する場合、登録は失敗する。

    Returns
    =======
    flag : bool
        True=OK、False=Error
    msg : string
        エラーメッセージなど
    size : tuple
        盤の大きさ (x,y) ……flag=Trueのとき
    block_num : int
        ブロック数 ……flag=Trueのとき
    num_lines : int
        線の本数 ……flag=Trueのとき
    """
    # 重複チェック
    if uniq:
        q = get_user_Q_data(q_num, author)
        if 0 < len(q):
            return False, 'Error: User %s Q%d data already exists' % (author, q_num)
    # 問題データの内容チェック
    try:
        Q = adc2019.read_Q(q_text)
    except RuntimeError as e:
        return False, 'Syntax Error: ' + str(e)

    dat = datastore.Entity(client.key('q_data'))
    dat.update(p_qdata_from_Q(q_num, author, Q, filename))
    client.put(dat) # 登録する

    size, block_num, _, _, _, num_lines = Q
    return True, 'OK', size, block_num, num_lines


def update_Q_data(q_num, q_text, author='DASymposium', filename=''):
    """
    問題データを変更する。すでに登録済みのデータを置き換える。
    """
    # 問題データの内容チェック
    try:
        Q = adc2019.read_Q(q_text)
    except RuntimeError as e:
        return False, 'Syntax Error: ' + str(e)

    prop = p_qdata_from_Q(q_num, author, Q, filename)
    size, block_num, _, _, _, num_lines = Q

    # 既存のエンティティを取り出す
    query = query_q_data(q_num=q_num, author=author)
    num = 0
    for ent in query.fetch():  # 存在するなら、高々、1個
        ent.update(prop)
        client.put(ent)
        num += 1
    if num == 0:
        msg = 'Not updated. You should have used POST instead of PUT?'
    elif num == 1:
        msg = 'Update OK'
    else:
        msg = 'Updated %d entities. May be internal system error' % num
    return True, msg, size, block_num, num_lines


def delete_user_Q_data(q_num, author):
    """
    qnumとauthorを指定して、問題データをデータベースから削除する
    """
    # 既存のエンティティを取り出す
    query = query_q_data(q_num=q_num, author=author)
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


def get_Q_data(q_num, year=YEAR, fetch_num=5):
    "出題の番号を指定して、Question問題データをデータベースから取り出す"
    qla = ndb.Key(QuestionListAll, 'master', parent=qdata_key()).get()
    if qla is None:
        return None
    # q_numは1から始まる整数なので、配列のインデックスとは1だけずれる
    qn = q_num-1
    if qn < 0 or len(qla.qs) <= qn:
        return None
    return qla.qs[q_num-1].get()


def p_qdata_from_Q(q_num, author, Q, filename=''):
    """
    問題データのプロパティを返す。

    Parameters
    ==========
    Q : tuple
        return value of adc2019.read_Q()
    """
    #size, block_num, block_size, block_data, block_type, num_lines = Q
    size, block_num, _, _, _, num_lines = Q

    # 正規化した問題テキストデータ（改行コードなど）
    q_text2 = adc2019.generate_Q_data(Q)

    return {'qnum':     q_num,     # int
            'text':     q_text2,   # string
            'blocknum': block_num, # int
            'cols':     size[0],   # int
            'rows':     size[1],   # int
            'linenum':  num_lines, # int
            'author':   author,    # string
            'filename': filename,  # string
            'date':     datetime.utcnow()}


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


def log(username, what):
    """
    logを記録する。
    """
    d = {'username': username,
         'what': what,
         'timestamp': datetime.utcnow()}
    key = client.key('log')
    entity = datastore.Entity(key=key)
    entity.update(d)
    client.put(entity)
         

def log_get_or_delete(username=None, fetch_num=100, when=None, delete=False):
    """
    logを、取り出す、または、消去する。
    """
    query = client.query(kind='log')
    query.order = ['-timestamp']
    if username:
        query.add_fileter('username', '=', username)
    if when:
        before = datetime.utcnow() - when
        print('before=', before)
        query.add_filter('timestamp', '>', before)
    q = query.fetch(fetch_num)
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

def timekeeper_key():
    return client.key('clock', 1)


def timekeeper_prop(dt, s, e):
    return {'lastUpdate': dt, # datetime
            'state':      s,  # str
            'enabled':    e   # int  0=disabled, 1=enabled
    };


def timekeeper_clk():
    """
    clkの値を返す。もし存在しない場合は、新規作成する。
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


def timekeeper_check():
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
            print('TimeKeeper: state change', clk)
    return new_state, old_state


def timekeeper_enabled(new_value=None):
    """
    timekeepedのenabledの値を、取得する、または、設定する。
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


def timekeeper_state(new_value=None):
    """
    timekeepedのstateの値を、取得する、または、設定する。
    """
    clk = timekeeper_clk()
    if new_value is None:
        return clk['state']
    else:
        if new_value in ('init', 'im0', 'Qup', 'im1', 'Aup', 'im2'):
            if new_value != clk['state']:
                clk['state'] = new_value
                clk['lastUpdate'] = datetime.utcnow()
                client.put(clk)
        return clk['state']


def timekeeper_transition(prev, now, prev_state):
    """
    時刻に基づいて、状態遷移する。

    Parameters
    ==========
    prev       : datetime

    now        : datetime

    prev_state : str
        前回の状態変数の値

    Returns
    =======
    same_slot : bool

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
        print('transition: BUG')
        new_state = 'BUG'
    #print('same_slot=%s, prev_state=%s, new_state=%s' % (same_slot, prev_state, new_state))
    return same_slot, new_state
