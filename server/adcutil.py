# coding: utf-8

"""
アルゴリズムデザインコンテストのさまざまな処理
"""

import conmgr_datastore as cds

from hashlib import sha1, sha256
import datetime
from tz import gae_datetime_JST

from adcconfig import YEAR


def hashed_password(username: str, password: str, salt: str) -> str:
    """
    ハッシュ化したパスワードを返す。
    """
    tmp = salt + username + password
    return sha256(tmp.encode('utf-8')).hexdigest()


def compare_password(salt: str, username: str, password: str, users: list) -> tuple:
    """
    パスワードがあっているかチェックする。

    Returns
    -------
    ユーザー情報 : tupple
        (username:str, password:str, displayname:str, uid:int, gid:int)
        ユーザーが見つからないときはNoneを返す
    """
    hashed256 = hashed_password(username, password, salt)
    u = adc_get_user_info(username, users)
    if (u is not None) and (u[1] == hashed256):
        return u  # 認証OK
    else:
        return None


def adc_login(salt: str, username: str, password: str, users: list) -> (tuple, str):
    """
    パスワードがあっているかチェックする。
    access tokenを生成する。

    Parameters
    ----------
    users : list
        adcusers.pyのUSERSで定義されたリスト。adcusers.USERS

    Returns
    -------
    ユーザー情報 : tupple
        (username:str, password:str, displayname:str, uid:int, gid:int)
        ユーザーが見つからないときはNoneを返す
        
    token : str
        access token
    """
    u = compare_password(salt, username, password, users)
    if u:
        # 認証OK
        token = cds.create_access_token(username, password)
        return u, token
    else:
        return None, None


def adc_change_password(salt, username, users, attr, priv_admin=False):
    """
    パスワードを変更する。管理者は任意のユーザーのパスワードを変更できる。

    Parameters
    ==========
    attr : dict
        key = ['password_old', 'password_new']

    Returns
    =======
    res : bool
        True=成功した、False=失敗した
    msg : str
        メッセージ
    """
    if not priv_admin: # 管理者でないときは、現在のパスワードをチェック
        u = compare_password(salt, username, attr['password_old'], users)
        if u is None:
            return False, "current password mismatched"
    if cds.change_password(username, attr['password_new'], salt):
        return True, "password changed"
    else:
        return False, "password change failed"

def adc_get_user_info(username: str, users: list) -> (str, str, str, int, int):
    """
    ユーザーの情報を返す。

    Parameters
    ----------
    username : str
        ユーザー名

    users : list
        adcusers.pyのUSERSで定義されたリスト。adcusers.USERS

    Returns
    -------
    ユーザー情報 : tuple (str, str, str, int, int)
        (username:str, password:str, displayname:str, uid:int, gid:int)
        ユーザーが見つからないときはNoneを返す
    """
    # まずはローカルに定義されたユーザを検索
    for u in users:
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

def adc_get_user_list(users: list) -> list:
    """
    ユーザー名のリストを返す。

    Parameters
    ----------
    users : list
        adcusers.pyのUSERSで定義されたリスト。adcusers.USERS

    Returns
    -------
    res : list of str
        ユーザー名のリスト
    """
    res = []
    # まずはローカルに定義されたユーザを検索
    for u in users:
        res.append(u[0])
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
