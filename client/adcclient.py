# coding: utf-8
#

"""
a client library for ADC service
"""

import os, stat, sys, json
import http.client as httplib
from urllib.parse import urlparse
import urllib.request
import urllib.error
import http.cookies as Cookie
import http_post
import base64


class ADCClient:
    def __init__(self):
        self.config = os.path.join( os.path.expanduser('~'), 'adcclient.json' )
        self.debug = False
        self.verbose = False
        self.username = None
        self.alt_username = None
        self.password = None
        self.url = 'http://127.0.0.1:8080/'  # API server address
        self.api_root = '/api'               # API server root path
        self.cookie = None
        self.output_file = None
        self.scheme = 'http'
        self.hostname = None
        self.port = None
        self.path = None
        self.http_proxy = None
        self.http_proxy_auth = None
        self.token = None
        self.version = '2019.08.21'


    def effective_username(self):
        """
        実効的なユーザー名を返す。
        つまり、alt_usernameが指定されている時は、alt_usernameを採用する。
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
        r = True
        try:
            with open(self.config, "r") as f:
                data = json.load(f)
                #print "data=",data
                for i in ['username', 'cookie', 'url', 'token']:
                    if i in data and data[i] is not None:
                        self.__dict__[i] = data[i]
        except IOError:
            # No such file or directoryなどの場合
            r = False
        except ValueError:
            # No JSON object could be decodedなどの場合
            r = False
        except:
            print('Error:', sys.exc_info()[0])
            raise
        self.setup_access_token() # 環境変数は設定情報をoverrideできる
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
            os.chmod(self.config, stat.S_IRUSR|stat.S_IWUSR)
        except:
            print('Error:', sys.exc_info()[0])
            raise


    def parse_url(self):
        """
        URLにアクセスするための事前準備。
        (ADC2019メモ) この関数は不要のはず。
        """
        o = urlparse(self.url)
        if not (o.scheme=='http' or o.scheme=='https'):
            print("Error: scheme %s is not supported", o.scheme)
            return None
        self.scheme = o.scheme
        self.hostname = o.hostname
        self.port = o.port
        self.path = o.path
        if self.path is None: self.path = '/'
        self.setup_http_proxy(o.hostname)


    def setup_http_proxy(self, hostname):
        """
        HTTP Proxyサーバに関する処理。
        httplibだけでやるとメンドクサイ
        (ADC2019メモ) この関数は不要のはず。
        """
        self.http_proxy = [False]
        if 'http_proxy' in os.environ:
            proxy = urlparse(os.environ['http_proxy'])
            use_proxy = True
            if 'no_proxy' in os.environ:
                no_proxy = os.environ['no_proxy'].split(',')
                if hostname in no_proxy: # (BUG) この判定は、厳しすぎる
                    return
            # http proxyを使う
            self.http_proxy = [True, proxy.hostname, proxy.port]
            if proxy.username is not None and proxy.password is not None:
                # proxy認証がある場合
                tmp = '%s:%s' % (proxy.username, proxy.password)
                self.http_proxy_auth = 'Basic ' + base64.b64encode(tmp.encode('utf-8')).decode('utf-8')
                # ステータス407 Proxy Authentication Requiredを確認せずに、いきなりヘッダを送ってもいいのか？


    def http_request_old(self, method, path, params=None, json=True, headers={}):
        """
        サーバのAPIを呼び出す。
        (ADC2019メモ) Python 2.7時代に使っていた関数。
        """
        path = self.api_root + path
        if self.path[-1]=='/' and path[0]=='/':
            path = path[1:] # 先頭の/は不要
        if json:
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
        else:
            if not 'Content-Type' in headers:
                headers['Content-Type'] = 'text/plain'
        self.http_cookie_header(headers)
        if self.token:
            headers['ADC-TOKEN'] = self.token
            headers['ADC-USER']  = self.username
        if self.http_proxy[0]:
            if self.http_proxy_auth is not None:
                headers['Proxy-Authorization'] = self.http_proxy_auth
            conn = httplib.HTTPConnection(self.http_proxy[1], self.http_proxy[2])
            port = '' if self.port is None else ':%d' % self.port
            path2 = '%s://%s%s%s%s' % (self.scheme, self.hostname, port, self.path, path)
        else:
            port = self.port
            if port is None:
                port = 80
            conn = httplib.HTTPConnection(self.hostname, port)
            path2 = self.path + path
        if self.debug:
            print('http_proxy=', self.http_proxy)
            print('method=', method)
            print('path2=', path2)
            print('params=', params)
            print('headers=', headers);
        conn.request(method, path2, params, headers)
        response = conn.getresponse()
        data = response.read()
        if self.debug:
            print("getheaders=", response.getheaders())
        res = [response.version,
               response.status,
               response.reason,
               response.getheader('Content-Type'),
               response.getheader('Set-Cookie'),
               data]
        conn.close()
        # print('res=', res)
        return res


    def http_post_multipart(self, path, fields, files):
        content_type, body = http_post.encode_multipart_formdata(fields, files)
        headers = {'Content-Type': content_type,
                   'Content-Length': str(len(body))}
        #print "headers=",headers
        #print "body=",body
        return self.http_request('POST', path, params=body, json=False, headers=headers)


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
                headers['Cookie'] = value;


    def http_request(self, method='GET', path='/', params=None, headers={}):
        """
        サーバのAPIを呼び出す。

        urllib.requestを使って、http_request()を書き直してみる。
        urllib.requestを使わなかった理由が何かあった気がするが、思い出せない。
        """
        # 基本的には url = self.url + api_root + path だが、'//'を避けるため
        if self.api_root[-1]=='/' and path[0]=='/':
            path = self.api_root + path[1:]
        else:
            path = self.api_root + path
        if self.url[-1]=='/' and path[0]=='/':
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
            headers['ADC-USER']  = self.username
        headers['User-Agent'] = 'adcclient/' + self.version
        if self.debug:
            print('http_proxy=', self.http_proxy)
            print('method=', method)
            print('url=', url)
            print('params=', params)
            print('headers=', headers);
        if method in ('POST', 'PUT'):
            params = params.encode('utf-8') # bytes型にする
        proxy_handler = urllib.request.ProxyHandler() # 環境変数http_proxyなどを参照して設定してくれる。http_proxy="http://USER:PASS@HOST:PORT/" のPROXY認証つきでもOKだった
        proxy_auth_handler = urllib.request.ProxyBasicAuthHandler()
        opener = urllib.request.build_opener(proxy_handler, proxy_auth_handler)
        #opener.addheaders = [(k, v) for k,v in headers.items()] # ここではContent-Typeを指定できなかった。Requestで指定すればよい
        req = urllib.request.Request(url=url, data=params, method=method, headers=headers)
        try:
            with opener.open(req) as f:
                # f は http.client.HTTPResponse のはず
                info = f.info()
                rurl = f.geturl()
                code = f.getcode()
                data = f.read()
                res = [f.version, # HTTP/1.0なら10、HTTP/1.1なら11
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
            res = [f.version, # HTTP/1.0なら10、HTTP/1.1なら11
                   f.status,  # 200とか
                   f.reason,  # 'OK'とか
                   f.getheader('Content-Type'),
                   f.getheader('Set-Cookie'),
                   data]
            f.close()

        # print('res=', res)
        return res


    def fin(self, res):
        """
        resの例
        [10, 200, 'OK', 'application/json', None, b'{"msg": "administrator"}']
        [10, 401, 'UNAUTHORIZED', 'application/json', None, b'{"msg": "not login yet"}']
        """
        #print('adcclient.fin: res=', res)
        if res[1] == 200:
            if self.debug:
                print("Success", res[1], res[2], "\n") #, res[5]
            if res[4] is not None:
                self.cookie = res[4]
        else:
            if self.debug:
                print("Failed", res[1], res[2], "\n") #, res[5]
        #print('adcclient.fin: res[5]: ', type(res[5]), res[5])
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


    def login(self, args):
        """
        serverにloginする
        """
        self.parse_url()
        info = {'username': self.username,
                'password': self.password }
        params = json.dumps(info)
        res = self.http_request('POST', '/login', params=params)
        info = json.loads(res[5])
        #print(info)
        if 'token' in info:
            self.token = info['token']
        return self.fin(res)


    def logout(self, args):
        """
        serverからlogoutする
        """
        self.parse_url()
        res = self.http_request('GET', '/logout')
        self.token = None
        return self.fin(res)


    def whoami(self, args):
        """
        (動作確認用) サーバーからユーザー名を取得する
        """
        self.parse_url()
        res = self.http_request('GET', '/whoami')
        return self.fin(res)


    def change_password(self, newpassword):
        """
        パスワードを変更する。
        """
        self.parse_url()
        info = {'password_old': self.password,
                'password_new': newpassword}
        params = json.dumps(info)
        res = self.http_request('POST', '/user/%s/password' % self.effective_username(), params=params)
        return self.fin(res)


    def get_root(self, args):
        self.parse_url()
        res = self.http_request('GET', '/2019/')
        return self.fin(res)

    def put_user_alive(self, args):
        self.parse_url()
        res = self.http_request('PUT', '/user/%s/alive' % self.effective_username(), params=args[0])
        return self.fin(res)

    def get_or_delete_log(self, args, a):
        "GET /admin/log"
        self.parse_url()
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
            path = "%s/log/%s/%d" % (path0, key, val)
        else:
            path = '%s/log' % path0
        res = self.http_request(method, path)
        return self.fin(res)

                
    def get_user_list(self):
        """
        サーバーから、ユーザー一覧リストを取得する。
        """
        self.parse_url()
        res = self.http_request('GET', '/admin/user')
        return self.fin(res)


    def get_user_info(self, args):
        """
        サーバーから、ユーザー情報を取得する。
        """
        self.parse_url()
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
        self.parse_url()
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
        adcusers_in.pyと同じフォーマットのファイルにアカウント情報を記述して、一括作成する。

        Parameters
        ==========
        file : str
            adcusers_in.py形式のファイルの名前
        """
        glo = {}
        exec(open(file).read(), glo)
        res2 = []
        for u in glo['USERS']:
            res2.append( self.create_user(u) )
        return res2


    def delete_user(self, username):
        self.parse_url()
        info = {'username': username}
        params = json.dumps(info)
        path = '/admin/user/%s' % username
        res = self.http_request('DELETE', path, json=False)
        return self.fin(res)


    def delete_users(self, args):
        res2 = []
        for username in args:
            res2.append( self.delete_user(username) )
        return res2

    def get_admin_q_all(self, args):
        self.parse_url()
        res = self.http_request('GET', '/admin/Q/all')
        return self.fin(res)

    def get_admin_a_all(self, args):
        self.parse_url()
        res = self.http_request('GET', '/A')
        return self.fin(res)

    def delete_admin_a_all(self, args):
        self.parse_url()
        res = self.http_request('DELETE', '/A')
        return self.fin(res)

    def get_admin_q_list(self, args):
        self.parse_url()
        res = self.http_request('GET', '/admin/Q/list')
        return self.fin(res)

    def put_admin_q_list(self, args):
        self.parse_url()
        res = self.http_request('PUT', '/admin/Q/list', params="dummy", json=False)
        return self.fin(res)

    def delete_admin_q_list(self, args):
        self.parse_url()
        res = self.http_request('DELETE', '/admin/Q/list', json=False)
        return self.fin(res)

    def get_q(self, args):
        self.parse_url()
        if len(args) == 0:
            res = self.http_request('GET', '/Q')
            return self.fin(res)
        else:
            res2 = []
            for i in args:
                path = '/Q/%d' % int(i)
                res = self.http_request('GET', path)
                res2.append(self.fin(res))
            return res2

    def get_a(self, args):
        self.parse_url()
        if len(args) == 0:
            path = '/A/%s' % self.effective_username()
            res = self.http_request('GET', path)
            return self.fin(res)
        else:
            res2 = []
            for i in args:
                path = '/A/%s/Q/%d' % (self.effective_username(), int(i))
                res = self.http_request('GET', path)
                res2.append(self.fin(res))
            return res2

    def put_a(self, args):
        "PUT /A/<username>/Q/<Q-number>"
        self.parse_url()
        a_num = int(args[0])
        a_file = args[1]
        path = '/A/%s/Q/%d' % (self.effective_username(), a_num)
        with open(a_file, "r") as f:
            a_text = f.read()
        res = self.http_request('PUT', path, params=a_text, json=False)
        return self.fin(res)

    def put_a_info(self, args):
        "PUT /A/<username>/Q/<Q-number>/info"
        self.parse_url()
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
        res = self.http_request('PUT', path, params=params, json=True)
        return self.fin(res)


    def get_or_delete_a_info(self, args, delete=False):
        """
        GET    /A/<username>/Q/<Q-number>/info
        DELETE /A/<username>/Q/<Q-number>/info
        """
        self.parse_url()
        if 0 < len(args):
            a_num = int(args[0])
        else:
            a_num = 0
        path = '/A/%s/Q/%d/info' % (self.effective_username(), a_num)
        method = 'DELETE' if delete else 'GET'
        res = self.http_request(method, path, json=True)
        return self.fin(res)
        #print "res=",
        #for i in range(0,len(res)): print i, " ", res[i]
        #print "results=", res[6]['results']
        #for i in range(0, len(res[6]['results'])): print i, " ", res[6]['results'][i]
        #print type(res[6]['results'][0])  # <type 'dict'>


    def get_user_q(self, q_num):
        """
        GET /user/<username>/Q/<Q-number>
        """
        self.parse_url()
        path = '/user/%s/Q/%d' % (self.effective_username(), q_num)
        res = self.http_request('GET', path)
        return self.fin(res)


    def get_user_q_list(self):
        """
        GET /user/<username>/Q

        Examples
        ========
        [{'blocknum': 8, 'cols': 10, 'date': 1566473404341960, 'filename': 'sampleQ0.txt', 'linenum': 11, 'qnum': 2, 'rows': 10}, {'blocknum': 8, 'cols': 10, 'date': 1566474951262141, 'filename': 'sampleQ0.txt', 'linenum': 11, 'qnum': 1, 'rows': 10}]
        """
        self.parse_url()
        path = '/user/%s/Q' % self.effective_username()
        res = self.http_request('GET', path)
        # print('res=', res)
        if res[1] == 200:
            obj = json.loads(res[5])
            return obj
        else:
            return None


    def post_user_q(self, q_num, q_file):
        """
        POST /user/<username>/Q/<Q-number>

        ユーザーが自作問題をアップロードする（新規に作成する）。
        """
        self.parse_url()
        path = '/user/%s/Q/%d' % (self.effective_username(), q_num)
        with open(q_file, 'r') as f:
            q_text = f.read()
        filename = os.path.basename(q_file)
        info = {'Q': q_text,
                'Q_filename': filename}
        params = json.dumps(info)
        res = self.http_request('POST', path, params=params)
        return self.fin(res)

        
    def put_user_q(self, q_num, q_file):
        """
        PUT /user/<username>/Q/<Q-number>
        すでにPOSTしたデータを書き換える。
        """
        self.parse_url()
        path = "/user/%s/Q/%d" % (self.effective_username(), q_num)
        with open(q_file, "r") as f:
            q_text = f.read()
        filename = os.path.basename(q_file)
        info = {'Q': q_text,
                'Q_filename': filename}
        params = json.dumps(info)
        res = self.http_request('PUT', path, params=params)
        return self.fin(res)


    def delete_user_q(self, q_num):
        """
        DELETE /user/<username>/Q/<Q-number>
        Qデータを削除する。
        """
        self.parse_url()
        path = "/user/%s/Q/%d" % (self.effective_username(), q_num)
        res = self.http_request('DELETE', path)
        return self.fin(res)


    def check_q(self, q_file):
        "PUT /Qcheck"
        self.parse_url()
        with open(q_file, "r") as f:
            qtext = f.read()
        path = "/Qcheck"
        res = self.http_request('PUT', path, params=qtext, json=False)
        return self.fin(res)

    def delete_a(self, a_num):
        self.parse_url()
        path = "/A/%s/Q/%d" % (self.effective_username(), a_num)
        res = self.http_request('DELETE', path, json=False)
        return self.fin(res)

    def score(self, args):
        self.parse_url()
        path = '/score'
        res = self.http_request('GET', path, json=True)
        return self.fin(res)

    def score_dump(self, args):
        self.parse_url()
        path = '/score/dump'
        res = self.http_request('GET', path, json=True)
        return self.fin(res)


    def timekeeper_enabled(self, args=None):
        """
        timekeeperの有効、無効の状態を取得する(GET)、状態を変更する(PUT)。
        """
        self.parse_url()
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
        self.parse_url()
        path = '/admin/timekeeper/state'
        if args is None or len(args) == 0:
            res = self.http_request('GET', path)
        else:
            state = args[0]
            assert state in ('init', 'im0', 'Qup', 'im1', 'Aup', 'im2')
            dat = {'state': state}
            res = self.http_request('PUT', path, params=json.dumps(dat))
        return self.fin(res)


    def timekeeper(self):
        """
        timekeeperの値を取得する。
        """
        self.parse_url()
        path = '/admin/timekeeper'
        res = self.http_request('GET', path)
        return self.fin(res)
