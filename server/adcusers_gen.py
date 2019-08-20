#! /usr/bin/env python
# coding: utf-8
#
"""
read `adcusers_in.py` and write `adcusers.py`
"""

from adcusers_in import USERS
from adcconfig import SALT
from hashlib import sha256
import os, stat

filename = "adcusers.py"

u = """# coding: utf-8
# DO NO EDIT THIS FILE.
# This file is created by %s

USERS = [
    # 0:username   1:password   2:displayname  3:uid   4:gid
""" % __file__

for t in USERS:
    if (t[4] == 0) or os.environ.get('DEBUG'):
        # 管理者権限を持っているユーザーだけ、出力する
        tmp = SALT + t[0] + t[1]
        h = sha256(tmp.encode('utf-8')).hexdigest()
        u +="    ('%s', '%s', u'%s', %4d, %4d),\n" % (t[0], h, t[2], t[3], t[4])
        u += "]\n"

with open(filename, 'w') as f:
    f.write(u)
os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR)
