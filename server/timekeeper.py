# coding: utf-8
#
# Copyright (C) 2019 IPSJ DA Symposium

"""
時計の時刻に基づいて、状態遷移させる
"""

from google.cloud import datastore
import datetime
from conmgr_datastore import TimeKeeper


def transition( prev, now, prev_state ):
    """
    時刻に基づいて、状態遷移する。

    Parameters
    ==========
    prev : datetime

    now : datetime

    prev_state: str
        前回の状態変数の値

    Returns
    =======
    same_slot : bool

    new_state : str
        次の状態
    """
    if (prev.year == now.year and
        prev.month == now.month and
        prev.day == now.day and
        prev.hour == now.hour):
        same_slot = True
    else:
        same_slot = False
    m = now.minute
    mQup = 3
    mim1 = 15
    mAup = 20
    mim2 = 55
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
    else: # ありえない
        print('transition: BUG')
        new_state = 'BUG'
    #print('same_slot=%s, prev_state=%s, new_state=%s' % (same_slot, prev_state, new_state))
    return same_slot, new_state


#@ndb.transactional
def check():
    clk = TimeKeeper.get_or_insert('CLOCK')
    #                               ^^^^^ Key Name
    if clk.enabled is None:
        clk.enabled = 1
    #print('clk=', clk)
    if clk.state is None:
        clk.state = 'init'
        clk.lastUpdate = datetime.datetime.now()
        clk.enabled = 1
        clk.put()
    if clk.enabled == 0:
        return clk.state, clk.state
    now = datetime.datetime.now()
    same_slot, new_state = transition(clk.lastUpdate, now, clk.state)
    old_state = clk.state
    if not same_slot or clk.state != new_state:
        clk.state = new_state
        clk.lastUpdate = now
        clk.put()
        #print('TK: state change', clk)
    return new_state, old_state


def get_enabled():
    clk = TimeKeeper.get_or_insert('CLOCK')
    return clk.enabled


def set_enabled(val):
    clk = TimeKeeper.get_or_insert('CLOCK')
    if val == 0:
        enabled = 0
    else:
        enabled = 1
    if enabled != clk.enabled:
        clk.enabled = enabled
        clk.put()
    return clk.enabled


def get_state():
    clk = TimeKeeper.get_or_insert('CLOCK')
    return clk.state


def set_state(val):
    clk = TimeKeeper.get_or_insert('CLOCK')
    if val in ('init', 'im0', 'Qup', 'im1', 'Aup', 'im2'):
        if val != clk.state:
            clk.state = val
            clk.put()
    ret = clk.state
    return ret
