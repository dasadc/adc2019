# coding: utf-8
#

"""
a client library for ADC service
"""

import http.cookies as Cookie
import json
import os
import stat
import sys
import urllib.error
import urllib.request
import yaml
import re
import base64
import pickle


class ADCClient:
    """
    client of ADC service
    """
    
    states = ('init', 'im0', 'Qup', 'im1', 'Aup', 'im2')  # class attribute
    
    def __init__(self):
        self.config = os.environ.get('ADCCLIENT_JSON',
                                     os.path.join(os.path.expanduser('~'), 'adcclient.json'))
        self.debug = False
        self.verbose = False
        self.username = None
        self.alt_username = None
        self.password = None
        self.url = 'http://127.0.0.1:8888/'  # API server address
        self.api_root = '/api'  # API server root path
        self.cookie = None
        self.output_file = None
        self.token = None
        self.version = '2021.08.19'
        self.year = 2021

    def effective_username(self):
        """
        実効的なユーザー名を返す。
        つまり、alt_usernameが指定されている時は、alt_usernameを採用する。

        運営・管理者がadministratorで使うときに、別のユーザー名を指定して
        APIを呼び出すときに、便利な機能。
        usernameを変更すると、adcclient.jsonにusernameが保存されてしまい、
        その後、勘違いする恐れがあるため、それを避けたい。
        """
        if self.alt_username:
            return self.alt_username
        else:
            return self.username

    def setup_access_token(self):
        """
        環境変数 ADC_USER, ADC_TOKEN を参照して、セットする。
        """
        u = os.environ.get('ADC_USER')
        if u:
            self.username = u
        t = os.environ.get('ADC_TOKEN')
        if t:
            self.token = t

    def read_config(self):
        """
        設定情報をファイルから読み出す。
        """
        #print('read_config', self.config)
        r = True
        try:
            with open(self.config, "r") as f:
                data = json.load(f)
                #print("data=", data)
                for i in ['username', 'cookie', 'url', 'token']:
                    if i in data and data[i] is not None:
                        self.__dict__[i] = data[i]
        except IOError:
            # No such file or directoryなどの場合
            r = False
        except ValueError:
            # No JSON object could be decodedなどの場合
            r = False
        except Exception:
            print('Error:', sys.exc_info()[0])
            raise
        self.setup_access_token()  # 環境変数は設定情報をoverrideできる
        return r

    def write_config(self):
        """
        設定情報をファイルに保存する。
        """
        data = {'username': self.username,
                'cookie': self.cookie,
                'url': self.url,
                'token': self.token}
        try:
            with open(self.config, 'w') as f:
                json.dump(data, f)
            os.chmod(self.config, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            print('Error:', sys.exc_info()[0])
            raise

    def http_cookie_header(self, headers):
        """
        Cookieヘッダーを設定する。
        (ADC2019メモ) Cookieは使わず、アクセス・トークンを使うことにする予定。
        """
        if self.cookie is not None:
            C = Cookie.SimpleCookie()
            C.load(self.cookie)
            # C['session']['path']
            # C['session']['httponly']
            if 'session' in C:
                value = 'session=' + C['session'].coded_value
                headers['Cookie'] = value

    def http_request(self, method: str = 'GET', path: str = '/', params: str = None, headers: dict = {}) -> list:
        """
        サーバのAPIを呼び出す。

        urllib.requestを使って、http_request()を書き直してみる。
        urllib.requestを使わなかった理由が何かあった気がするが、思い出せない。

        Parameters
        ----------
        method : str
            'GET', 'POST', 'PUT', 'DELETE'など
        path : str
            URLのpath部分。'/admin/timekeeper/round'など。
            `api_root = '/api'`なので、pathに`/api`はつけない
        params : str
            POST、PUTのとき、`json.dumps({...})`のようにして、パラメータ値を渡す
        headers : dict
            http headerを追加したいとき。

        Returns
        -------
        res : list
            [0] version。HTTP/1.0なら10、HTTP/1.1なら11
            [1] status code。200とか
            [2] reason。'OK'とか
            [3] Content-Typeヘッダの値。'application/json'とか
            [4] Set-Cookieヘッダの値。
            [5] bodyデータ。bytes型、b'{"round": 999}'とか
            [6] 
        """
        # 基本的には url = self.url + api_root + path だが、'//'を避けるため
        if self.api_root[-1] == '/' and path[0] == '/':
            path = self.api_root + path[1:]
        else:
            path = self.api_root + path
        if self.url[-1] == '/' and path[0] == '/':
            url = self.url + path[1:]
        else:
            url = self.url + path
        if json:
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
        else:
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'text/plain'
        self.http_cookie_header(headers)
        if self.token:
            headers['ADC-TOKEN'] = self.token
            headers['ADC-USER'] = self.username
        headers['User-Agent'] = 'adcclient/' + self.version
        if self.debug:
            print('method=', method)
            print('url=', url)
            print('params=', params)
            print('headers=', headers)
        if method in ('POST', 'PUT'):
            params = params.encode('utf-8')  # bytes型にする
        proxy_handler = urllib.request.ProxyHandler()
        # 環境変数http_proxyなどを参照して設定してくれる。http_proxy="http://USER:PASS@HOST:PORT/" のPROXY認証つきでもOKだった
        proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()
        opener = urllib.request.build_opener(proxy_handler, proxy_auth_handler)
        # opener.addheaders = [(k, v) for k,v in headers.items()] # ここではContent-Typeを指定できなかった。Requestで指定すればよい
        req = urllib.request.Request(url=url, data=params, method=method, headers=headers)
        try:
            with opener.open(req) as f:
                # f は http.client.HTTPResponse のはず
                info = f.info()
                rurl = f.geturl()
                code = f.getcode()
                data = f.read()
                res = [f.version,  # HTTP/1.0なら10、HTTP/1.1なら11
                       f.status,  # 200とか
                       f.reason,  # 'OK'とか
                       f.getheader('Content-Type'),
                       f.getheader('Set-Cookie'),
                       data]
        except urllib.error.HTTPError as f:
            strf = str(f)
            info = f.info()
            rurl = f.geturl()
            code = f.getcode()
            data = f.read()
            res = [f.version,  # HTTP/1.0なら10、HTTP/1.1なら11
                   f.status,  # 200とか
                   f.reason,  # 'OK'とか
                   f.getheader('Content-Type'),
                   f.getheader('Set-Cookie'),
                   data]
            f.close()

        # print('res=', res)
        return res

    def fin(self, res: list) -> list:
        """
        Parameters
        ----------
        res : list
            http_header()の返り値

        Returns
        -------
        list
            [0] version。HTTP/1.0なら10、HTTP/1.1なら11
            [1] status code。200とか
            [2] reason。'OK'とか
            [3] Content-Typeヘッダの値。'application/json'とか
            [4] Set-Cookieヘッダの値。
            [5] bodyデータ。bytes型、b'{"round": 999}'とか
            [6] dict。'application/json'のときは、[5]のbodyデータから作る。

        Examples
        --------

        resの例
        [10, 200, 'OK', 'application/json', None, b'{"msg": "administrator"}']
        [10, 401, 'UNAUTHORIZED', 'application/json', None, b'{"msg": "not login yet"}']
        """
        # print('adcclient.fin: res=', res)
        if res[1] == 200:
            if self.debug:
                print('Success', res[1], res[2], '\n')  # , res[5]
            if res[4] is not None:
                self.cookie = res[4]
        else:
            if self.debug:
                print('Failed', res[1], res[2], '\n')  # , res[5]
        # print('adcclient.fin: res[5]: ', type(res[5]), res[5])
        if res[3] is None:
            info = {'msg': res[5]}
        else:
            contenttype = res[3].split(';')
            if contenttype[0] == 'application/json':
                info = json.loads(res[5])
            else:
                info = {'msg': res[5]}
            if self.verbose:
                print(info['msg'])
        res.append(info)
        return res

    def login(self):
        """
        serverにloginする
        """
        info = {'username': self.username,
                'password': self.password}
        params = json.dumps(info)
        res = self.http_request('POST', '/login', params=params)
        info = json.loads(res[5])
        # print(info)
        if 'token' in info:
            self.token = info['token']
        return self.fin(res)

    def logout(self):
        """
        serverからlogoutする
        """
        res = self.http_request('GET', '/logout')
        self.token = None
        return self.fin(res)

    def get_api_version(self):
        """
        サーバーからAPIのバージョン番号を取得する
        """
        res = self.http_request('GET', '/version')
        return self.fin(res)

    def whoami(self):
        """
        (動作確認用) サーバーからユーザー名を取得する
        """
        res = self.http_request('GET', '/whoami')
        return self.fin(res)

    def iamadmin(self):
        """
        このユーザーは管理者権限を持っているか、サーバーに教えてもらう
        """
        res = self.http_request('GET', '/admin/iam')
        return self.fin(res)

    def change_password(self, newpassword):
        """
        パスワードを変更する。
        """
        info = {'password_old': self.password,
                'password_new': newpassword}
        params = json.dumps(info)
        res = self.http_request('POST', '/user/%s/password' % self.effective_username(), params=params)
        return self.fin(res)

    def get_root(self):
        res = self.http_request('GET', '/%d/' % self.year)
        return self.fin(res)


    def put_user_alive(self, args):
        """
        aliveメッセージをサーバに送信する。
        """
        info = {'alive': args}
        params = json.dumps(info)
        res = self.http_request('PUT', '/user/%s/alive' % self.effective_username(), params=params)
        return self.fin(res)


    def get_or_delete_log(self, args: list, a: str, num: int = None):
        """
        ログを取得する、または、削除する。
        GET /admin/log

        Parameters
        ----------
        args : list
            args[0]: int,  数値
            args[1]: str,  'days', 'seconds'のどちらか
        a : str
            コマンド名。
            'get-log', 'get-user-log', 'delete-log', 'delete-user-log'のどれか
        num : int, default None
            ログの件数
        """
        if a in ('get-log', 'delete-log'):
            path0 = '/admin'
        else:
            path0 = '/user/%s' % self.effective_username()
        if a in ('delete-log', 'delete-user-log'):
            method = 'DELETE'
        else:
            method = 'GET'
        if 1 < len(args):
            key = args[1]
            val = int(args[0])
            path = '%s/log/%s/%d' % (path0, key, val)
        else:
            path = '%s/log' % path0
        if num is not None:
            path += '?' + urllib.parse.urlencode({'num': num})
        res = self.http_request(method, path)
        return self.fin(res)

    def get_user_list(self):
        """
        サーバーから、ユーザー一覧リストを取得する。
        """
        res = self.http_request('GET', '/admin/user')
        return self.fin(res)

    def get_user_info(self, args):
        """
        サーバーから、ユーザー情報を取得する。
        """
        res2 = []
        if len(args) == 0:
            args = [self.effective_username()]
        for username in args:
            path = '/admin/user/%s' % username
            res = self.http_request('GET', path)
            res2.append(self.fin(res))
        return res2

    def create_user(self, args):
        """
        サーバ側のdatastoreに、ユーザーを一人登録する。
        """
        info = {'username': args[0],
                'password': args[1],
                'displayname': args[2],
                'uid': int(args[3]),
                'gid': int(args[4])}
        params = json.dumps(info)
        path = '/admin/user/%s' % args[0]
        res = self.http_request('POST', path, params=params)
        return self.fin(res)

    def create_users(self, file):
        """
        サーバ側のdatastoreに、ユーザーを登録する。
        adcusers_in.{py,yaml}と同じフォーマットのファイルにアカウント情報を記述して、一括作成する。

        Parameters
        ==========
        file : str
            adcusers_in.{py,yaml}形式のファイルの名前
        """
        res = []
        _, ext = os.path.splitext(file)
        if ext.lower() == '.py':
            glo = {}
            exec(open(file).read(), glo)
            for u in glo['USERS']:
                res.append(self.create_user(u))
        elif ext.lower() in ('.yaml', '.yml'):
            with open(file, 'r') as f:
                o = yaml.load(f, Loader=yaml.FullLoader)
            for i in o:
                u = [i['username'], i['password'], i['displayname'], i['uid'], i['gid']]
                res.append(self.create_user(u))
        return res

    def delete_user(self, username):
        # info = {'username': username}
        # params = json.dumps(info)
        path = '/admin/user/%s' % username
        res = self.http_request('DELETE', path)
        return self.fin(res)

    def delete_users(self, args):
        res2 = []
        for username in args:
            res2.append(self.delete_user(username))
        return res2


    def convert_users(self, file_in, file_out):
        """
        adcusers_in.pyファイルを、YAML形式に変換する。

        Parameters
        ==========
        file : str
            adcusers_in.py形式のファイルの名前
        """
        glo = {}
        exec(open(file_in).read(), glo)
        res = []
        for i in glo['USERS']:
            res.append({'username': i[0],
                        'password': i[1],
                        'displayname': i[2],
                        'uid': i[3],
                        'gid': i[4]})
        with open(file_out, 'w') as f:
            yaml.dump(res, f, encoding='utf-8', allow_unicode=True)
        return True


    def get_admin_q_all(self, round_count: int = None):
        """
        admin専用。出題リストの内訳（だれが出題した問題か）を取得

        Examples
        --------

           [
            {'author': 'ADC-0',
            'blocknum': 750,
            'cols': 72,
            'date': 1630286947665665,
            'linenum': 750,
            'qnum': 9,
            'rows': 72}]
        """
        if round_count is None:
            round_count = self.get_round()
        path = '/admin/Q/all?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        return self.fin(res)

    def delete_admin_q_all(self, round_count: int = None):
        if round_count is None:
            round_count = self.get_round()
        path = '/admin/Q/all?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('DELETE', path)
        return self.fin(res)

    def get_admin_a_all(self, round_count: int = None):
        if round_count is None:
            round_count = self.get_round()
        path = '/A?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        # print('res=', res)
        return self.fin(res)

    def delete_admin_a_all(self, round_count: int = None):
        if round_count is None:
            round_count = self.get_round()
        path = '/A?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('DELETE', path)
        return self.fin(res)

    def get_admin_q_list(self, round_count: int = None):
        """
        dict keys = ['author_list', 'author_qnum_list', 'blocknum_list', 'cols_list', 'linenum_list', 'msg', 'qnum_list', 'rows_list', 'text_admin', 'text_user']
        """
        if round_count is None:
            round_count = self.get_round()
        path = '/admin/Q/list?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        # print('res=', res)
        return self.fin(res)

    def put_admin_q_list(self, round_count: int = None):
        if round_count is None:
            round_count = self.get_round()
        res = self.http_request('PUT', '/admin/Q/list', params=json.dumps({'round': round_count}))
        return self.fin(res)

    def delete_admin_q_list(self, round_count: int = None):
        if round_count is None:
            round_count = self.get_round()
        path = '/admin/Q/list?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('DELETE', path)
        return self.fin(res)

    def get_q(self, args):
        if len(args) == 0:
            res = self.http_request('GET', '/Q')
            # print('res=', res)
            return self.fin(res)
        else:
            res2 = []
            for i in args:
                path = '/Q/%d' % int(i)
                res = self.http_request('GET', path)
                res2.append(self.fin(res))
            return res2

    def get_q_all_in_one(self):
        res = self.http_request('GET', '/Q/all_in_one')
        return self.fin(res)

    def get_a(self, args):
        if len(args) == 0:
            path = '/A/%s' % self.effective_username()
            res = self.http_request('GET', path)
            """
            print('res=', res)
            res= [11, 200, 'OK', 'application/json', None, b'{"anum_list": [12], "msg": "A12\\n"}']
            """
            return [self.fin(res)]
        else:
            res2 = []
            for i in args:
                path = '/A/%s/Q/%d' % (self.effective_username(), int(i))
                res = self.http_request('GET', path)
                # print(i, 'res=', res)
                res2.append(self.fin(res))
            return res2

    def put_a(self, args):
        "PUT /A/<username>/Q/<Q-number>"
        a_num = int(args[0])
        a_file = args[1]
        a_replace = False
        if 2 < len(args):
            if args[2] == 'replace-A-number':
                a_replace = True  # Aファイル中のA番号('A1'など)を、"A${a_num}"で置換
        path = '/A/%s/Q/%d' % (self.effective_username(), a_num)
        with open(a_file, 'r') as f:
            a_text = f.read()
        if a_replace:
            tmp = []
            p = re.compile(r'A([0-9]+)', re.IGNORECASE)
            for line in a_text.splitlines():
                if p.match(line):
                    line = 'A%d' % a_num
                tmp.append(line)
            a_text = '\n'.join(tmp)
        info = {'A': a_text, 'A_filename': a_file}
        params = json.dumps(info)
        res = self.http_request('PUT', path, params=params)
        return self.fin(res)

    def put_a_info(self, args):
        """
        回答の補足情報をアップロードする。
        PUT /A/<username>/Q/<Q-number>/info
        """
        a_num = int(args[0])
        cpu_sec = float(args[1])
        mem_byte = int(args[2])
        if 3 < len(args):
            misc_text = args[3]
        else:
            misc_text = None
        path = '/A/%s/Q/%d/info' % (self.effective_username(), a_num)
        info = {'cpu_sec': cpu_sec,
                'mem_byte': mem_byte,
                'misc_text': misc_text}
        params = json.dumps(info)
        res = self.http_request('PUT', path, params=params)
        return self.fin(res)

    def get_or_delete_a_info(self, args, delete=False):
        """
        回答の補足情報を取得する、または、削除する。
        GET    /A/<username>/Q/<Q-number>/info
        DELETE /A/<username>/Q/<Q-number>/info
        """
        if 0 < len(args):
            a_num = int(args[0])
        else:
            a_num = 0
        path = '/A/%s/Q/%d/info' % (self.effective_username(), a_num)
        method = 'DELETE' if delete else 'GET'
        res = self.http_request(method, path)
        return self.fin(res)
        # print "res=",
        # for i in range(0,len(res)): print i, " ", res[i]
        # print "results=", res[6]['results']
        # for i in range(0, len(res[6]['results'])): print i, " ", res[6]['results'][i]
        # print type(res[6]['results'][0])  # <type 'dict'>

    def get_user_q(self, round_count: int = None, q_num: int = None):
        """
        GET /user/<username>/Q/<Q-number>
        """
        path = '/user/%s/Q/%d' % (self.effective_username(), q_num)
        if round_count is not None:
            path += '?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        return self.fin(res)

    def get_user_q_list(self, round_count: int = None):
        """
        GET /user/<username>/Q

        Examples
        ========
        [{'blocknum': 8, 'cols': 10, 'date': 1566473404341960, 'filename': 'sampleQ0.txt', 'linenum': 11,
         'qnum': 2, 'rows': 10}, {'blocknum': 8, 'cols': 10, 'date': 1566474951262141, 'filename': 'sampleQ0.txt',
          'linenum': 11, 'qnum': 1, 'rows': 10}]
        """
        path = '/user/%s/Q' % self.effective_username()
        if round_count is not None:
            path += '?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        # print('res=', res)
        if res[1] == 200:
            obj = json.loads(res[5])
            return obj
        else:
            return None

    def post_user_q(self, q_num: int, q_file: str, round_count: int = None):
        """
        POST /user/<username>/Q/<Q-number>

        ユーザーが自作問題をアップロードする（新規に作成する）。

        Parameters
        ----------
        q_num : int
            問題番号
        q_file : str
            問題データのファイル名
        round_count : int, default None
            round数
        """
        path = '/user/%s/Q/%d' % (self.effective_username(), q_num)
        if round_count is None:
            round_count = self.get_round()
        with open(q_file, 'r') as f:
            q_text = f.read()
        filename = os.path.basename(q_file)
        info = {'Q': q_text,
                'Q_filename': filename,
                'round': round_count}
        res = self.http_request('POST', path, params=json.dumps(info))
        return self.fin(res)

    def put_user_q(self, q_num, q_file, round_count: int = None):
        """
        PUT /user/<username>/Q/<Q-number>
        すでにPOSTしたデータを書き換える。

        Parameters
        ----------
        q_num : int
            問題番号
        q_file : str
            問題データのファイル名
        round_count : int, default None
            round数
        """
        path = "/user/%s/Q/%d" % (self.effective_username(), q_num)
        if round_count is None:
            round_count = self.get_round()
        with open(q_file, "r") as f:
            q_text = f.read()
        filename = os.path.basename(q_file)
        info = {'Q': q_text,
                'Q_filename': filename,
                'round': round_count}
        res = self.http_request('PUT', path, params=json.dumps(info))
        return self.fin(res)

    def delete_user_q(self, round_count: int = None, q_num: int = None):
        """
        DELETE /user/<username>/Q/<Q-number>
        Qデータを削除する。
        """
        path = "/user/%s/Q/%d" % (self.effective_username(), q_num)
        if round_count is not None:
            path += '?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('DELETE', path)
        return self.fin(res)

    def check_q(self, q_file):
        """
        POST /Qcheck
        """
        with open(q_file, 'r') as f:
            qtext = f.read()
        path = '/Qcheck'
        info = {'Q': qtext,
                'Q_filename': q_file}
        params = json.dumps(info)
        res = self.http_request('POST', path, params=params)
        # print('res=', res)
        # [11, 200, 'OK', 'application/json', None, b'{"check_file":"Q-ok"}\n']
        return self.fin(res)

    def delete_a(self, a_num):
        path = "/A/%s/Q/%d" % (self.effective_username(), a_num)
        res = self.http_request('DELETE', path)
        return self.fin(res)

    def score(self, round_count: int = None):
        path = '/score'
        if round_count is not None:
            path += '?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        return self.fin(res)

    def score_dump(self, round_count: int = None):
        path = '/score/dump'
        if round_count is not None:
            path += '?' + urllib.parse.urlencode({'round': round_count})
        res = self.http_request('GET', path)
        return self.fin(res)

    def timekeeper_enabled(self, args=None):
        """
        timekeeperの有効、無効の状態を取得する(GET)、状態を変更する(PUT)。
        """
        path = '/admin/timekeeper/enabled'
        if args is None or len(args) == 0:
            res = self.http_request('GET', path)
        else:
            enabled = int(args[0])
            assert enabled in (0, 1)
            dat = {'enabled': enabled}
            res = self.http_request('PUT', path, params=json.dumps(dat))
        return self.fin(res)

    def timekeeper_state(self, args=None):
        """
        timekeeperのstate値を取得する(GET)、state値を変更する(PUT)。
        """
        path = '/admin/timekeeper/state'
        if args is None or len(args) == 0:
            res = self.http_request('GET', path)
        else:
            state = args[0]
            assert state in self.states
            dat = {'state': state}
            res = self.http_request('PUT', path, params=json.dumps(dat))
        return self.fin(res)

    def timekeeper_round(self, args=None) -> list:
        """
        timekeeperのroundカウンタ値を取得する(GET)、roundカウンタ値を変更する(PUT)。
        Parameters
        ----------
        args : list of str, default None
            Noneのときは値を取得する。
            listのときは、値int(args[0])を設定する。

        Returns
        -------
        list
            fin()の返り値。[6]がdictデータ。
        """
        path = '/admin/timekeeper/round'
        if args is None or len(args) == 0:
            res = self.http_request('GET', path)
        else:
            round_count = int(args[0])
            dat = {'round': round_count}
            res = self.http_request('PUT', path, params=json.dumps(dat))
        return self.fin(res)

    def get_round(self) -> int:
        """
        roundカウンタ値の値をAPIサーバから取得して返す。

        Returns
        -------
        round_count : int
        """
        tmp = self.timekeeper_round()  # res()の結果なので
        return tmp[6]['round']

    def timekeeper(self, args=None):
        """
        timekeeperの値を取得する(GET)、変更する(PUT)。
        
        Parameters
        ----------
        args : list of str, default None
            enabled     = args[0]
            state       = args[1]
            round_count = args[2]
        """
        path = '/admin/timekeeper'
        if args is None or len(args)==0:
            res = self.http_request('GET', path)
            return self.fin(res)
        else:
            assert len(args) == 3
            enabled = int(args[0])
            assert enabled in (0, 1)
            state = args[1]
            assert state in self.states
            round_count = int(args[2])
            assert round_count in (1, 2)
            dat = {'enabled': enabled,
                   'state': state,
                   'round': round_count}
            res = self.http_request('PUT', path, params=json.dumps(dat))
            return self.fin(res)

    def test_mode(self, args=None):
        """
        TEST_MODEの値を取得する(GET)、変更する(PUT)。
        
        Parameters
        ----------
        args : None or str
            'True', 'False'
        """
        return self._admin_config_common(path='test_mode', args=args)


    def view_score_mode(self, args=None):
        """
        VIEW_SCORE_MODEの値を取得する(GET)、変更する(PUT)。
        
        Parameters
        ----------
        args : None or str
            'True', 'False'
        """
        return self._admin_config_common(path='view_score_mode', args=args)


    def log_to_datastore(self, args=None):
        """
        LOG_TO_DATASTOREの値を取得する(GET)、変更する(PUT)。
        
        Parameters
        ----------
        args : None or str
            'True', 'False'
        """
        return self._admin_config_common(path='log_to_datastore', args=args)


    def _admin_config_common(self, path, args=None):
        """
        common subroutine of 'test-mode', 'view-score-mode', 'log-to-datastore'
        
        Parameters
        ----------
        path : str
             Used as '/admin/config/{path}'
             ['test_mode', 'view_score_mode', 'log_to_datastore']
        args : None or str
            'True', 'False'
        """
        api_path = f'/admin/config/{path}'
        if args is None or len(args)==0:
            res = self.http_request('GET', api_path)
            # print(res)
            return self.fin(res)
        else:
            assert len(args) == 1
            a = args[0]
            if a.lower() == 'true' or a == '1':
                param = 1
            elif a.lower() == 'false' or a == '0':
                param = 0
            else:
                raise RuntimeError('bad argument: %s' % a)

            dat = {path: param}
            res = self.http_request('PUT', api_path, params=json.dumps(dat))
            return self.fin(res)


    def dump_datastore(self, filename):
        res = self.http_request('GET', '/admin/datastore')
        res = self.fin(res)
        bin_data = base64.b64decode(res[6]['datastore'])
        with open(filename, 'wb') as f:
            f.write(bin_data)
        res[6] = pickle.loads(bin_data)
        return res


    def restore_datastore(self, filename):
        with open(filename, 'rb') as f:
            bin_data = f.read()  # pickle dump
        params = json.dumps({'datastore': base64.b64encode(bin_data).decode('utf-8')})
        res = self.http_request('PUT', '/admin/datastore', params=params)
        return self.fin(res)
