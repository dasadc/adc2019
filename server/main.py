# coding: utf-8
#
# Copyright (C) 2020,2021 DA Symposium

"""
DAシンポジウム 2021
アルゴリズムデザインコンテスト

RESTもどき API server
"""

from flask import Flask, request, jsonify, session, json, render_template, make_response, escape, url_for, g, redirect
#    Markup
#from werkzeug.wsgi import DispatcherMiddleware # deprecated
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import traceback
import datetime
import logging

import adc2019
import adcconfig
import adcusers
import adcutil
import conmgr_datastore as cds

#from convert_excel2QA import genA_from_b64

#werkzeug_logger = logging.getLogger("werkzeug")
#werkzeug_logger.setLevel(logging.ERROR)
#logging.basicConfig(filename='adc-server.log', level=logging.WARNING)

app = Flask(__name__)
#app.logger.setLevel(logging.INFO)
app.config['JSON_AS_ASCII'] = False
app.config['APPLICATION_ROOT'] = '/api'
app.config.from_object(adcconfig)
app.config.from_object(adcusers)
app.secret_key = app.config['SECRET_KEY']

state_str = {'init': 'initial',
             'im0': 'intermediate_0',
             'Qup': 'Q_upload',
             'im1': 'intermediate_1',
             'Aup': 'A_upload',
             'im2': 'intermediate_2'}


def adc_response(msg, code=200, json_encoded=False):
    """
    クライアントへ応答データを作る
    """
    if json_encoded:
        body = msg
    else:
        template = 'response.json'
        body = render_template(template, msg=msg)
    resp = make_response(body)
    if code == 200:
        resp.status = 'OK'
    elif code == 400:
        resp.status = 'Bad Request'
    elif code == 401:
        resp.status = 'Unauthorized'
    resp.status_code = code
    resp.headers['Content-Type'] = 'application/json'
    return resp


def adc_response_json(obj, code=200):
    """
    Parameters
    ==========
    obj : dict
        dict to send client
    """
    body = json.dumps(obj)
    resp = make_response(body)
    resp.status_code = code
    resp.headers['Content-Type'] = 'application/json'
    return resp


def adc_response_Q_data(result):
    """
    問題テキストデータを返す
    
    Parameters
    ==========
    result : list of Q-data-dict
    """
    # print('adc_response_Q_data', result)
    if len(result) == 0:
        code = 404
        text = "Not Found\r\n"
    elif len(result) == 1:
        code = 200
        text = result[0]['text']
    else:
        print('WARNING: adc_response_Q_data: too many data', len(result))
        code = 200
        text = result[0]['text']
    return adc_response_json({'text': text}, code)


def log_request(usernm):
    #print(usernm, request.method + " " + request.path)
    cds.log(usernm, request.method + " " + request.path)


def priv_admin():
    """
    ログイン中であり、admin権限をもったユーザか？
    """
    if authenticated():
        info = adcutil.adc_get_user_info(username(), app.config['USERS'])
        if info is None:
            return False
        if info[4] == 0: # gid
            #print('priv_admin: True')
            return True

    return ('login' in session and session['login']==1 and
            'gid' in session and session['gid']==0 )


def authenticated():
    """
    ログインしてユーザ認証済のユーザか？
    まず、sessionで確認して、つぎにtokenを確認する。
    tokenの確認は、datastoreへのアクセスが発生するため、その順番にしている。
    """
    r = ('login' in session and session['login']==1 and 'token' in session)
    # print('authenticated (session): r=', r)
    if r:
        return True
    user = request.headers.get('ADC-USER')
    token = request.headers.get('ADC-TOKEN')
    # print('user:', user)
    # print('token:', token)
    if user and token:
        r = cds.check_access_token(user, token)
        # print('authenticated (token): r=', r)
        if r:
            return True
    return False


def adc_logout():
    "ログアウトする"
    user = request.headers.get('ADC-USER')
    token = request.headers.get('ADC-TOKEN')
    #print('token:', token)
    #print('user:', user)
    if user and token:
        cds.delete_access_token(user, token)
        print('logout')
    for i in ['login', 'username', 'displayName', 'uid', 'gid', 'token']:
        del session[i]


def username():
    """
    ユーザー名を返す
    """
    user = request.headers.get('ADC-USER')
    if user:
        return user
    return session.get('username')


def username_matched(usernm):
    """
    ログイン中であり、ユーザ名がusernameに一致しているか？
    """
    # HTTPヘッダでチェックする
    user = request.headers.get('ADC-USER')
    if user:
        if authenticated() and user == usernm:
            return True
    # sessionでチェックする
    print(session)
    return ('login' in session and session['login']==1 and session['username']==usernm)


@app.before_request
def before_request():
    new_state, old_state = cds.timekeeper_check()
    if new_state != old_state:  # 状態遷移したとき
        if new_state == 'Qup':
            # 出題リストを削除する
            msg = cds.admin_Q_list_delete()
            cds.log('auto', 'delete Q list')
            # 回答データを削除する
            cds.get_or_delete_A_data(delete=True)
            cds.log('auto', 'delete A all')
        if new_state in ('im1', 'Aup'):  # im1を通らずにいきなりAupに遷移することがある
            # 出題リストを決める
            flag, msg, _ = cds.admin_Q_list_create()
            cds.log('auto', 'admin_Q_list_create %s' % flag)
        
    g.state = new_state  # グローバル変数。なにこれ？


@app.route('/check_file', methods=['POST'])
def check_file():
    """
    1. a client posts Q-file and/or A-file
    2. server checks file(s)
    3. return check results.
    """
    #print('request=', request)
    #print('request.data=', request.data)
    #print('request.form=', request.form)
    #print('request.files=', request.files)
    #print('request.json=', request.json)
    qdata = None
    adata = None
    Q = None
    A = None
    if request.json:
        qdata = request.json.get('Q')
        adata = request.json.get('A')
        # try b64 decode.
        # if success (= if b64 encoded file),
        # decode it and return adata by converting it into A file.
        # otherwise (= just a text data), return adata as it is.
        #adata = genA_from_b64(adata) 
    if 'Qfile' in request.files:
        qdata = request.files['Qfile'].read().decode('utf-8')
    if 'Afile' in request.files:
        adata = request.files['Afile'].read().decode('utf-8')

    #print('qdata\n', qdata)
    #print('adata\n', adata)
    try:
        if qdata:
            Q = adc2019.read_Q(qdata)
        if adata:
            A = adc2019.read_A(adata)
            aid = A[0]
            A = A[1:]
        if Q is None and A is None:
            return jsonify({'check_file': 'No data'})
        if Q is None:
            return jsonify({'check_file': 'A-ok'})
        if A is None:
            return jsonify({'check_file': 'Q-ok'})

        info = adc2019.check_data(Q, A)
        #print(info)
        info2 = info.copy()
        for k in ['count', 'corner', 'line_length', 'line_corner', 'ban_data_F']:
            info2[k]  = str(info2[k])
        info2['check_file'] = 'ok'
        return jsonify(info2)
    except Exception as e:
        #traceback.print_exc()
        errinfo = ['ADC2020 rule violation'] + [str(i) for i in e.args]
        info = {'error': errinfo, 'stack_trace': traceback.format_exc()}
        return jsonify(info)

    return jsonify({'check_file': 'ok',
                    'value': 1234567,
                    'msg': '生麦生米生卵'})
    

@app.route('/test_post', methods=['POST'])
def test_post():
    return jsonify({'test': 'not implemented'})


@app.route('/test_get', methods=['GET'])
def test_get():
    """
    test GET method
    """
    #print('request=', request)
    return jsonify({'test': 'ok',
                    'value': 9876,
                    'msg': 'こんにちは世界',
                    'my_url': url_for('test_get')})


@app.route('/login', methods=['POST'])
def login():
    """
    ログインする。
    新規ログイン時に、トークンを新規生成して返す。
    すでにログイン済みのときは、既存のトークンを返す。

    TO DO
    =====
    旧バージョンでsessionを使っていたが、これは止めたい。
    でもWebアプリのときは、ログイン状態を維持できるので、それなりに便利だ。
    """
    if authenticated():
        if 'times' not in session:
            session['times'] = 0
        session['times'] += 1
        msg = "You are already logged-in, %s, %s, %d times" % (escape(username()), escape(session.get('displayName')), session.get('times'))
        log_request(username())
        token_value = session.get('token')
        if token_value is None:
            token = cds.get_access_token(username())
            if token:
                token_value = token.get('token')
            else:
                token_value = '(BUG) Internal Error'
        res = {'msg': msg,
               'token': token_value}
        return adc_response_json(res)

    # print('request.json', request.json)
    usernm = request.json.get('username', '')
    passwd = request.json.get('password', '')
    u, token = adcutil.adc_login(app.config['SALT'], usernm, passwd, app.config['USERS'])
    if u is None:
        return adc_response("login failed", 401)
    session['login'] = 1
    session['username'] = usernm
    session['displayName'] = u[2]
    session['uid'] = u[3]
    session['gid'] = u[4]
    session['token'] = token
    session['times'] = 1
    log_request(username())
    app.logger.warning('%s logged in successfully', usernm)
    txt = json.dumps({'msg': 'login OK',
                      'token': token})
    return adc_response(txt, json_encoded=True)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    ログアウトする。セッション情報、トークンが削除される。
    """
    if authenticated():
        log_request(username())
        adc_logout()
        return adc_response('logout OK')
    else:
        return adc_response('not login yet', 401)


@app.route('/whoami', methods=['GET'])
def whoami():
    """
    ユーザー名を返す。動作確認、APIの疎通確認用。
    """
    if authenticated():
        log_request(username())
        return adc_response(username())
    else:
        return adc_response('not login yet', 401)


@app.route('/admin/user', methods=['GET'])
def admin_user_list_get():
    """
    ユーザー一覧リストを取得する。
    """
    if not authenticated():
        return adc_response("access forbidden", 403)
    res = adcutil.adc_get_user_list(app.config['USERS'])
    res.sort()
    log_request(username())
    return adc_response_json(res)


@app.route('/admin/user/<usernm>', methods=['GET'])
def admin_user_get(usernm):
    """
    ユーザーの情報を取得する。

    test-02:カメさんチーム:1002:1000
    username:displayname:uid:gid
    """
    if ( not authenticated() or
         (not priv_admin() and username() != usernm) ):
        return adc_response('access forbidden', 403)
    log_request(usernm)
    u = adcutil.adc_get_user_info(usernm, app.config['USERS'])
    if u is None:
        return adc_response('not found', 404)
    else:
        msg = '%s:%s:%d:%d' % (u[0], u[2], u[3], u[4])
        return adc_response(msg)


@app.route('/admin/user/<usernm>', methods=['POST','DELETE'])
def admin_user_post(usernm):
    """
    アカウント作成、アカウント削除
    admin権限がある人だけ可能
    """
    if not priv_admin():
        return adc_response('access forbidden', 403)
    log_request(username())
    # DELETEの場合、アカウント削除
    if request.method == 'DELETE':
        cds.delete_user(usernm)
        msg = 'delete user %s' % usernm
        return adc_response(msg)
    # POSTの場合、アカウント作成
    if usernm != request.json['username']:
        return adc_response("username mismatch error", 400)
    cds.create_user(request.json['username'],
                    request.json['password'],
                    request.json['displayname'],
                    request.json['uid'],
                    request.json['gid'],
                    app.config['SALT'])
    msg = 'create user %s' % usernm
    return adc_response(msg)



@app.route('/admin/Q/all', methods=['GET', 'DELETE'])
def admin_Q_all():
    """
    データベースに登録されたすべての問題の一覧リストを返す、
    または、すべての問題データを削除する。
    """
    if not priv_admin():
        return adc_response('access forbidden', 403)
    log_request(username())
    if request.method == 'GET':
        msg = cds.get_admin_Q_all()
        return adc_response_json({'msg': msg})
    # DELETEの場合
    msg = cds.delete_admin_Q_all()
    return adc_response_json({'msg': msg})

@app.route('/admin/Q/list', methods=['GET','PUT','DELETE'])
def admin_Q_list():
    """
    コンテストの出題リストを管理する。
    """
    if not priv_admin():
        return adc_response('access forbidden', 403)
    log_request(username())
    if request.method == 'GET':
        qla = cds.admin_Q_list_get()  # Q list all
        # print('qla=', qla)
        if qla is None:
            msg = 'Not found. Admin must run "adccli put-admin-q-list"'
            qnum_list = []
            author_list = []
            author_qnum_list = []
            cols_list = []
            rows_list = []
            blocknum_list = []
            linenum_list = []
            text_admin = ''
            text_user = ''
        else:
            msg = qla['text_admin']
            qnum_list = qla['qnum_list']
            author_list = qla['author_list']
            author_qnum_list = qla['author_qnum_list']
            cols_list = qla['cols_list']
            rows_list = qla['rows_list']
            blocknum_list = qla['blocknum_list']
            linenum_list = qla['linenum_list']
            text_admin = qla['text_admin']
            text_user = qla['text_user']
        info = {'msg': msg,
                'qnum_list': qnum_list,
                'author_list': author_list,
                'author_qnum_list': author_qnum_list,
                'cols_list': cols_list,
                'rows_list': rows_list,
                'blocknum_list': blocknum_list,
                'linenum_list': linenum_list,
                'text_admin': text_admin,
                'text_user': text_user}
        return adc_response_json(info)
    elif request.method == 'PUT':
        flag, msg, qla = cds.admin_Q_list_create()
        return adc_response_json({'msg': msg})
    elif request.method == 'DELETE':
        msg = cds.admin_Q_list_delete()
        return adc_response(msg)
    else: # ありえない
        return adc_response('unknown')


@app.route('/admin/log', methods=['GET', 'DELETE'])
def admin_log():
    """
    ログデータを取得する
    """
    if priv_admin():
        return user_log_before(None, None, None)
    else:
        return adc_response("access forbidden", 403)

    
@app.route('/admin/log/<key>/<int:val>', methods=['GET', 'DELETE'])
def admin_log_before(key, val):
    """
    ログデータ
    """
    if not priv_admin():
        return adc_response('access forbidden', 403)
    return user_log_before(None, key, val)
    

@app.route('/admin/timekeeper/enabled', methods=['GET', 'PUT'])
def admin_timekeeper_enabled():
    """
    timekeeperの有効、無効の状態を取得する(GET)、状態を変更する(PUT)。
    """
    if request.method == 'GET':
        dat = {'enabled': cds.timekeeper_enabled()}
        return adc_response_json(dat)
    # PUTの場合
    if not priv_admin():
        return adc_response('access forbidden. admin only', 403)
    #print('request.headers=', request.headers)
    val = request.json.get('enabled')
    if val in (0, 1):
        ret = cds.timekeeper_enabled(val)
        dat = {'enabled': ret}
        return adc_response_json(dat)
    else:
        return adc_response('Illeagal argument %s' % val, 400)

        
@app.route('/admin/timekeeper/state', methods=['GET', 'PUT'])
def admin_timekeeper_state():
    """
    timekeeperのstate値を取得する(GET)、state値を変更する(PUT)。
    """
    if request.method == 'GET':
        dat = {'state': cds.timekeeper_state()}
        return adc_response_json(dat)
    # PUTの場合
    if not priv_admin():
        return adc_response('access forbidden. admin only', 403)
    state = request.json.get('state')
    state2 = cds.timekeeper_state(state)
    dat = {'state': state2}
    return adc_response_json(dat)

    
@app.route('/admin/timekeeper', methods=['GET', 'PUT'])
def admin_timekeeper():
    """
    timekeeperのを取得する(GET)、または、設定する(PUT)。
    """
    if request.method == 'GET':
        clk = cds.timekeeper_clk()
        dat = dict(clk)
        dat['lastUpdate'] = dat['lastUpdate'].isoformat()  # datetime型をstring型へ変換
        return adc_response_json(dat)
    else:  # PUTの場合
        if not priv_admin():
            return adc_response('access forbidden. admin only', 403)
        e = request.json.get('enabled')
        s = request.json.get('state')
        dat = {}
        if e is not None:
            dat['enabled'] = e
        if s is not None:
            dat['state'] = s
        r = cds.timekeeper_set(dat)
        return adc_response_json(r)

    
@app.route('/admin/config/test_mode', methods=['GET', 'PUT'])
def admin_config_test_mode():
    """
    TEST_MODEの値を取得する(GET)、または、設定する(PUT)。
    """
    if request.method == 'GET':
        dat = {'test_mode': app.config['TEST_MODE']}
        return adc_response_json(dat)
    else:  # PUTの場合
        if not priv_admin():
            return adc_response('access forbidden. admin only', 403)
        i = request.json.get('test_mode')
        if i in (0, 1):
            app.config['TEST_MODE'] = bool(i)
            dat = {'test_mode': app.config['TEST_MODE']}
            return adc_response_json(dat)
        else:
            return adc_response('illeagal argument %s' % i, 400)

    
@app.route('/admin/config/view_score_mode', methods=['GET', 'PUT'])
def admin_config_view_score_mode():
    """
    VIEW_SCORE_MODEの値を取得する(GET)、または、設定する(PUT)。
    """
    if request.method == 'GET':
        dat = {'view_score_mode': app.config['VIEW_SCORE_MODE']}
        return adc_response_json(dat)
    else:  # PUTの場合
        if not priv_admin():
            return adc_response('access forbidden. admin only', 403)
        i = request.json.get('view_score_mode')
        if i in (0, 1):
            app.config['VIEW_SCORE_MODE'] = bool(i)
            dat = {'view_score_mode': app.config['VIEW_SCORE_MODE']}
            return adc_response_json(dat)
        else:
            return adc_response('illeagal argument %s' % i, 400)

    
@app.route('/A', methods=['GET', 'DELETE'])
def admin_A_all():
    """
    データベースに登録されたすべての回答データの一覧リスト
    """
    if not priv_admin():
        return adc_response('access forbidden', 403)
    log_request(username())
    if request.method == 'GET':
        msg, data = cds.get_admin_A_all()
        dat = {'msg': msg, 'data': data}
        return adc_response_json(dat)
    else:
        # DELETE
        result = cds.get_or_delete_A_data(delete=True)
        print('result=', result)
        dat = {'msg': 'DELETE', 'result': result}
        return adc_response_json(dat)
        

@app.route('/A/<usernm>', methods=['GET'])
def admin_A_username(usernm):
    """
    回答データの一覧リストを返す
    """
    if not priv_admin():                    # 管理者ではない
        if not username_matched(usernm):    # ユーザ名が一致しない
            return adc_response('permission denied', 403)
    log_request(usernm)
    msg, anum_list = cds.get_user_A_all(usernm)
    return adc_response_json({'msg': msg,
                              'anum_list': anum_list})


@app.route('/A/<usernm>/Q', methods=['POST'])
def a_q_menu(usernm):
    if not authenticated():
        return adc_response('not login yet', 401)
    a_text   = request.json.get('A')
    ret, msg = post_A(usernm, a_text, request.form)
    code = 200 if ret else 403
    return adc_response_json({'msg': msg}, code)

@app.route('/A/<usernm>/Q/<int:a_num>', methods=['PUT', 'GET', 'DELETE'])
def a_put(usernm, a_num):
    """
    回答データを、登録する、取り出す、削除する
    """
    if not authenticated():
        return adc_response('not login yet', 401)
    if not priv_admin():                      # 管理者ではない
        if not username_matched(usernm):  # ユーザ名が一致しない
            return adc_response('permission denied', 403)
        if g.state != 'Aup':
            return adc_response('deadline passed', 503)
    log_request(usernm)
    if request.method=='PUT':
        # print('request.json=', request.json)
        atext = request.json.get('A')
        flag, msg = cds.put_A_data(a_num, usernm, atext)
        if flag:
            code = 200
        else:
            code = 403
        return adc_response_json({'msg': msg}, code)
    # GET, DELETEの場合
    if not priv_admin():                    # 管理者ではない
        if app.config['TEST_MODE']==False:  # 本番モード
            return adc_response('permission denied. GET, DELETE are allowed in test mode only', 403)
    delete = True if request.method=='DELETE' else False
    result = cds.get_or_delete_A_data(a_num=a_num, username=usernm, delete=delete)
    if len(result) == 0:
        return adc_response("answer data A%d not found" % a_num, 404)
    text = '\n'.join(result)
    return adc_response_json({'msg': text, 'result': result}) # このAPIよくない


@app.route('/A/<usernm>/Q/<int:a_num>/info', methods=['GET', 'PUT', 'DELETE'])
def a_info_put(usernm, a_num):
    """
    回答データの補足情報を、登録する、取り出す、削除する
    """
    if not authenticated():
        return adc_response('not login yet', 401)
    if not priv_admin():                        # 管理者ではない
        if not username_matched(usernm):        # ユーザ名が一致しない
            return adc_response('permission denied', 403)
    if not priv_admin():
        if request.methods != 'GET' and g.state != 'Aup':
            return adc_response('deadline passed', 503)
    log_request(usernm)
    if request.method == 'PUT':
        flag, msg = cds.put_A_info(a_num, usernm, request.json)
        if flag:
            code = 200
        else:
            code = 403
        return adc_response_json({'msg': msg}, code)
    else:  # GET or DELETE
        if a_num == 0:
            a_num = None
        if usernm == '*':
            usernm = None
        delete = True if request.method == 'DELETE' else False
        results = cds.get_or_delete_A_info(a_num=a_num, username=usernm, delete=delete)
        tmp = {'msg': request.method,  'results': results}
        return adc_response_json(tmp)


@app.route('/user/<usernm>/Q', methods=['GET'])
def get_user_q_list(usernm):
    """
    ユーザを指定して、問題データの一覧リストを返す
    """
    if not authenticated():
        return adc_response('not login yet', 401)
    if not priv_admin():  # 管理者以外の場合
        if not username_matched(usernm):  # ユーザ名チェック
            return adc_response('permission denied. admin or self-access only', 403)
    log_request(usernm)
    result = cds.get_user_Q_list(usernm)
    return adc_response_json(result)


@app.route('/user/<usernm>/Q/<int:q_num>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def user_q(usernm, q_num):
    """
    ユーザを指定して、問題データを、ダウンロード、アップロード、削除
    """
    if not priv_admin():  # 管理者以外の場合
        if not username_matched(usernm):  # ユーザ名チェック
            return adc_response('permission denied. admin only', 403)
        if q_num <= 0 or 4 <= q_num:  # 問題番号の範囲チェック
            return adc_response('Q number is out of range', 403)
        if g.state != 'Qup':
            return adc_response('deadline passed', 503)
    log_request(usernm)
    if request.method == 'GET':
        result = cds.get_user_Q_data(q_num, usernm)  # list
        return adc_response_Q_data(result)

    elif request.method == 'PUT':
        # print('PUT: request.json=', request.json)
        q_text   = request.json.get('Q')
        filename = request.json.get('Q_filename')
        flag, *args = cds.update_Q_data(q_num, q_text, author=usernm, filename=filename)
        if flag:
            msg, size, block_num, line_num = args
            msg2 = 'PUT %s: %s Q%d size %dx%d block_num %d line_num %d' % (msg, usernm, q_num, size[0], size[1], block_num, line_num)
            code = 200
        else:
            msg = args[0]
            msg2 = 'PUT ' + msg
            code = 403
        return adc_response(msg2, code)

    elif request.method == 'POST':
        # print('POST: request.json=', request.json)
        q_text   = request.json.get('Q')
        filename = request.json.get('Q_filename')
        flag, *args = cds.insert_Q_data(q_num, q_text, author=usernm, filename=filename)

        if flag:
            msg, size, block_num, line_num = args
            msg2 = 'POST %s: insert %s Q%d size %dx%d block_num %d line_num %d' % (msg, usernm, q_num, size[0], size[1], block_num, line_num)
            code = 200
        else:
            msg = args[0]
            msg2 = 'POST ' + msg
            code = 403
        return adc_response(msg2, code)

    elif request.method == 'DELETE':
        msg = cds.delete_user_Q_data(q_num, author=usernm)
        return adc_response(msg)


@app.route('/user/<usernm>/alive', methods=['PUT'])
def user_alive(usernm):
    """
    ユーザを指定して、生きていることを報告する
    """
    if not priv_admin():                        # 管理者ではない
        if not username_matched(usernm):      # ユーザ名が一致しない
            return adc_response('permission denied', 403)
    alive = request.json.get('alive')
    print('alive=', alive)
    cds.log(usernm, 'alive: %s' % json.dumps(alive))
    tmp = {'msg': 'OK', 'alive': alive}
    return adc_response_json(tmp)


@app.route('/user/<usernm>/log', methods=['GET','DELETE'])
def user_log(usernm):
    # ユーザを指定して、ログデータを返す
    return user_log_before(usernm, None, None)


@app.route('/user/<usernm>/log/<key>/<int:val>', methods=['GET','DELETE'])
def user_log_before(usernm, key, val):
    """
    ログデータを取得する。
    """
    if not priv_admin():                  # 管理者ではない
        if not username_matched(usernm):  # ユーザ名が一致しない
            return adc_response('permission denied', 403)
    log_request(username()) # やめたほうがいい？
    if key == 'days':
        td = datetime.timedelta(days=val)
    elif key == 'seconds':
        td = datetime.timedelta(seconds=val)
    elif key is None:
        td = None
    else:
        return adc_response('time format error', 404)
    if request.method == 'GET':
        delete = False
    else: # DELETE
        delete = True
        if not priv_admin():              # 管理者ではない
            return adc_response('permission denied', 403)
    msg = request.path
    results = cds.log_get_or_delete(username=usernm, when=td, delete=delete)
    tmp = {'msg': msg,  'results':results }
    return adc_response_json(tmp)


@app.route('/user/<usernm>/password', methods=['POST'])
def user_password(usernm):
    """
    パスワードを変更する。
    """
    if not authenticated():
        return adc_response('access forbidden', 403)
    if not priv_admin():                  # 管理者ではない
        if not username_matched(usernm):  # ユーザ名が一致しない
            return adc_response('permission denied', 403)
    res, msg = adcutil.adc_change_password(app.config['SALT'], usernm, app.config['USERS'], request.json, priv_admin())
    code = 200 if res else 403
    return adc_response(msg, code)


@app.route('/Q/<int:q_num>', methods=['GET'])
def q_get(q_num):
    if not authenticated():
        return adc_response('not login yet', 401)
    if not priv_admin():
        if g.state != 'Aup':
            return adc_response('deadline passed', 503)
    log_request(username())
    qdat = cds.get_Q_data(q_num)  # qdatはdict
    return adc_response_Q_data([qdat])


@app.route('/Q', methods=['GET'])
def q_get_list():
    if not authenticated():
        return adc_response('not login yet', 401)
    if not priv_admin():
        if g.state != 'Aup':
            return adc_response('deadline passed', 503)
    log_request(username())
    # msg = cds.get_Q_all()
    # qnum_list = [int(q[1:]) for q in msg.splitlines()]  # q='Q1'
    qla = cds.admin_Q_list_get()
    if qla is None:
        info = {'msg': 'Not found. Admin must run "adccli put-admin-q-list"',
                'qnum_list': [],
                'cols_list':  [],
                'rows_list':  [],
                'blocknum_list':  [],
                'linenum_list':  []}
    else:
        info = {'msg': qla['text_user'],
                'qnum_list': qla['qnum_list'],
                'cols_list': qla['cols_list'],
                'rows_list': qla['rows_list'],
                'blocknum_list': qla['blocknum_list'],
                'linenum_list': qla['linenum_list']}
    return adc_response_json(info)


@app.route('/Qcheck', methods=['POST'])
def q_check():
    """
    Qデータのみのチェックを行う。

    see also
    ========
    check_file()
    """
    print('q_check', request.json)
    if not authenticated():
        return adc_response('not login yet', 401)
    log_request(username())

    if request.json:
        qdata = request.json.get('Q')
    if 'qfile' in request.files:
        qdata = request.files['qfile'].read().decode('utf-8')
    try:
        if qdata:
            Q = adc2019.read_Q(qdata)
            return jsonify({'check_file': 'Q-ok'})
    except Exception as e:
        errinfo = ['ADC2020 rule violation'] + [str(i) for i in e.args]
        info = {'error': errinfo, 'stack_trace': traceback.format_exc()}
        return jsonify(info)
    

@app.route('/score/dump', methods=['GET'])
def score_dump():
    "スコア計算"
    if not authenticated():
        return adc_response('not login yet', 401)
    if not priv_admin():                    # 管理者ではない
        return adc_response('access forbidden', 403)
    log_request(username())
    import pickle
    import base64
    res = cds.calc_score_all()
    bin = pickle.dumps(res)
    txt = base64.b64encode(bin).decode('utf-8')
    return adc_response_json({'score': txt})
    

@app.route('/score', methods=['GET'])
def get_score():
    "スコア計算"
    if not authenticated():
        return adc_response('not login yet', 401)
    log_request(username())
    if app.config['VIEW_SCORE_MODE']:
        score_board, ok_point, q_point, bonus_point, q_factors, misc = cds.calc_score_all()
    else:
        score_board, ok_point, q_point, bonus_point, q_factors, misc = {}, {}, {}, {}, {}, {}
    dat = {'score_board': score_board,
           'ok_point': ok_point,
           'q_point': q_point,
           'bonus_point': bonus_point,
           'q_factors': q_factors,
           'misc': misc}
    return adc_response_json(dat)
    

@app.route('/info', methods=['GET'])
def get_info():
    return adc_response_json({'url':
                              {'client-app':
                               {'README': adcconfig.URL_CLIENT_APP_README}
                              }})


@app.route('/version', methods=['GET'])
def get_version():
    return adc_response_json({'version': adcconfig.YEAR})


@app.route('/%s/' % adcconfig.YEAR, methods=['GET'])
def root():
    if not authenticated():
        return adc_response('permission denied', 403)
    log_request(username())
    msg = r'Hello world\n'
    msg += r'Test mode: %s\n' % app.config['TEST_MODE']
    return adc_response(msg)


dummy_app = Flask('dummy')

@dummy_app.route('/', methods=['GET'])
def dummy_root():
    return redirect('/static/app/index.html')

@dummy_app.route('/2020', methods=['GET'])
def dummy_2019dir():
    return redirect('/static/app/index.html')

@dummy_app.route('/2020/', methods=['GET'])
def dummy_2019():
    return redirect('/static/app/index.html')


app.wsgi_app = DispatcherMiddleware(dummy_app, {app.config['APPLICATION_ROOT']: app.wsgi_app})

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--ip', type=str, default="127.0.0.1", help='ip address')
    parser.add_argument('--port', type=int, default=4280, help='port')
    parser.add_argument('--anonymous', action='store_true', help='if set, use AnonymousCredentials')
    args = parser.parse_args()

    app.run(host=args.ip, port=args.port, debug=True)

