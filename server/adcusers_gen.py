#! /usr/bin/env python
# coding: utf-8
#
"""
1. read `adcusers_in.yaml`, if not exists `adcusers_in.py`, and
2. write `adcusers.yaml` and `adcusers.py`.
"""

try:
    from adcusers_in import USERS  # adcusers_in.py
except ModuleNotFoundError:
    pass
from adcconfig import SALT
from hashlib import sha256
import os
import stat
import yaml

input_filename  = 'adcusers_in.yaml'  # used if exists
output_filename = 'adcusers.py'
output_file_yaml = 'adcusers.yaml'

users_out = []
if os.path.exists(input_filename):
    USERS = []   # overwrite
    with open(input_filename, 'r') as f:
        users = yaml.load(f, Loader=yaml.FullLoader)
        for i in users:
            u = [i['username'], i['password'], i['displayname'], i['uid'], i['gid']]
            USERS.append(u)
    users_out = users
else:
    for t in USERS:
        users_out.append({'username': t[0],
                          'password': t[1],
                          'displayname': t[2],
                          'uid': t[3],
                          'gid': t[4]})

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

with open(output_filename, 'w') as f:
    f.write(u)
os.chmod(output_filename, stat.S_IRUSR|stat.S_IWUSR)

with open(output_file_yaml, 'w') as f:
    yaml.dump(users_out, f, encoding='utf-8', allow_unicode=True)
