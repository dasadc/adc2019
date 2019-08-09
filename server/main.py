# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 DA Symposium

"""
DAシンポジウム 2019
アルゴリズムデザインコンテスト

Q/A File Check service
"""

#from flask import Flask, request, redirect, session, escape, url_for, json, make_response, render_template, g, Markup
from flask import Flask, request, jsonify
import traceback
import adc2019

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

    

@app.route('/api/check_file', methods=['POST'])
def check_file():
    """
    1. a client posts Q-file and/or A-file
    2. server checks file(s)
    3. return check results.
    """
    pass


@app.route('/api/test_post', methods=['POST'])
def test_post():
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
        errinfo = ['ADC2019 rule violation'] + [str(i) for i in e.args]
        info = {'error': errinfo, 'stack_trace': traceback.format_exc()}
        return jsonify(info)

    return jsonify({'check_file': 'ok',
                    'value': 1234567,
                    'msg': '生麦生米生卵'})
    

@app.route('/api/test_get', methods=['GET'])
def test_get():
    """
    test GET method
    """
    #print('request=', request)
    return jsonify({'test': 'ok',
                    'value': 9876,
                    'msg': 'こんにちは世界'})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
