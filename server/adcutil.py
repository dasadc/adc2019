# coding: utf-8

"""
アルゴリズムデザインコンテストのさまざまな処理
"""

import logging
import conmgr_datastore as cds

from hashlib import sha1, sha256
import datetime
from tz import gae_datetime_JST

import adcconfig
import adcusers

_state_str = {'init': 'initial',
              'im0': 'intermediate_0',
              'Qup': 'Q_upload',
              'im1': 'intermediate_1',
              'Aup': 'A_upload',
              'im2': 'intermediate_2'}


_usernames = [] # 有効なユーザー名のリスト。データストア取得したデータのキャッシュ
_user_gid = {} # username -> gid 対応関係

def cached_usernames() -> list:
    global _usernames
    return _usernames

def refresh_userinfo_cache():
    """
    有効なユーザー情報をデータストアから読み出して、キャッシュデータを更新する。
    """
    global _usernames
    global _user_gid
    userinfo = adc_get_userinfo_list()
    _usernames = sorted([i[0] for i in userinfo])
    _user_gid = {i[0]: i[4] for i in userinfo}
    logging.debug('refresh_userinfo_cache: %s', str(_usernames))

def valid_user(usernm: str) -> bool:
    """
    実際に存在するユーザー名か？
    """
    return usernm in cached_usernames()

def get_gid(usernm: str) -> int:
    """
    ユーザーのgidを返す。
    """
    global _user_gid
    return _user_gid.get(usernm)

def valid_state(state: str) -> bool:
    """
    文字列stateが、状態の値として適切であれば、Trueを返す
    """
    return state in _state_str.keys()

def valid_round(round_count: int) -> bool:
    """
    round数が適切であれば、Trueを返す
    """
    return round_count in (1, 2, 3, 999)  # hard-coded !!!



def hashed_password(username: str, password: str) -> str:
    """
    ハッシュ化したパスワードを返す。
    """
    tmp = adcconfig.SALT + username + password
    return sha256(tmp.encode('utf-8')).hexdigest()


def compare_password(username: str, password: str) -> tuple:
    """
    パスワードがあっているかチェックする。

    Returns
    -------
    ユーザー情報 : tupple
        (username:str, password:str, displayname:str, uid:int, gid:int)
        ユーザーが見つからないときはNoneを返す
    """
    hashed256 = hashed_password(username, password)
    u = adc_get_user_info(username)
    if (u is not None) and (u[1] == hashed256):
        return u  # 認証OK
    else:
        return None


def adc_login(username: str, password: str) -> (tuple, str):
    """
    パスワードがあっているかチェックする。
    access tokenを生成する。

    Parameters
    ----------
    username : str
        user name
    password : str
        plain password

    Returns
    -------
    ユーザー情報 : tupple
        (username:str, password:str, displayname:str, uid:int, gid:int)
        ユーザーが見つからないときはNoneを返す
        
    token : str
        access token
    """
    u = compare_password(username, password)
    if u:
        # 認証OK
        token = cds.create_access_token(username, password)
        return u, token
    else:
        return None, None


def adc_change_password(username: str, attr: dict, priv_admin: bool = False):
    """
    パスワードを変更する。管理者は任意のユーザーのパスワードを変更できる。

    Parameters
    ----------
    attr : dict
        key = ['password_old', 'password_new']

    Returns
    -------
    res : bool
        True=成功した、False=失敗した
    msg : str
        メッセージ
    """
    if not priv_admin: # 管理者でないときは、現在のパスワードをチェック
        u = compare_password(username, attr['password_old'])
        if u is None:
            return False, "current password mismatched"
    if cds.change_password(username, attr['password_new'], adcconfig.SALT):
        return True, "password changed"
    else:
        return False, "password change failed"

def adc_get_user_info(username: str) -> (str, str, str, int, int):
    """
    ユーザーの情報を返す。

    Parameters
    ----------
    username : str
        ユーザー名

    Returns
    -------
    ユーザー情報 : tuple (str, str, str, int, int)
        (username:str, password:str, displayname:str, uid:int, gid:int)
        ユーザーが見つからないときはNoneを返す
    """
    # まずはローカルに定義されたユーザを検索
    for u in adcusers.USERS:
        if username == u[0]:
            return u
    # 次に、データベースに登録されたユーザを検索
    r = cds.get_userinfo(username)
    if r is None:
        return None
    else:
        return (r['username'],
                r['password'],
                r['displayname'],
                r['uid'],
                r['gid'])

def adc_get_userinfo_list() -> list[tuple]:
    """
    ユーザー情報のリストを返す。

    Returns
    -------
    res : list of tuple
        ユーザー情報のリスト。ユーザー情報は、以下の通り。
        (username:str, password:str, displayname:str, uid:int, gid:int)
    """
    # ローカルに定義されたユーザ + データベースに登録されたユーザ
    return list(adcusers.USERS) + cds.get_userinfo_list()

def adc_get_user_list() -> list[str]:
    """
    ユーザー名のリストを返す。

    Returns
    -------
    res : list of str
        ユーザー名のリスト
    """
    # まずはローカルに定義されたユーザを検索
    res = [u[0] for u in adcusers.USERS]
    # 次に、データベースに登録されたユーザを検索
    res2 = cds.get_username_list()
    res.extend(res2)
    return res




# OBSOLETED
# def html_score_board(score_board):
#     hd_key = '/header/'
#     out = '<table border=1>\n'
#     line = '<tr><th>-</th>'
#     for hd in score_board[hd_key]:
#         line += '<th>%s</th>' % hd
#     line += '</tr>\n'
#     out += line
#     for user in sorted(score_board.keys()):
#         if user == hd_key: continue
#         line = '<tr><th>%s</th>' % user
#         for val in score_board[user]:
#             line += '<td>%1.1f</td>' % val
#         line += '</tr>\n'
#         out += line
#     out += '</table>\n'
#     #print "out=\n", out
#     return out
