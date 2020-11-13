from flask import Flask, request, Response
from flask.views import MethodView
from common.db.MysqlDB import DBCreateSql
import sys
import json
import os
import time
import re
import pysolr
import requests
import datetime
from jwt import exceptions
import jwt

from config import JWT_SALT

app = Flask(__name__)


class JwtCreate(MethodView):

    def get(self):
        pass

    def post(self):
        data = request.get_data()

        json_data = json.loads(data.decode('utf-8'))
        payload = json_data.get('payload', None)
        timeout = json_data.get('timeout', 1)
        headers = {
            'typ': 'jwt',
            'alg': 'HS256'
        }
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
        result = jwt.encode(payload=payload, key=JWT_SALT, algorithm="HS256", headers=headers).decode('utf-8')

        res_dict = {"retcode": 200000, "msg": "success", "data": result}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


class JwtCheck(MethodView):

    def get(self):
        pass

    def post(self):
        data = request.get_data()

        token = json.loads(data.decode('utf-8'))
        res_list = []
        result = {'status': False, 'data': None, 'error': None}
        try:
            verified_payload = jwt.decode(token, JWT_SALT, True)
            result['status'] = True
            result['data'] = verified_payload
        except exceptions.ExpiredSignatureError:
            result['error'] = 'token已失效'
        except jwt.DecodeError:
            result['error'] = 'token认证失败'
        except jwt.InvalidTokenError:
            result['error'] = '非法的token'
        return result

        res_dict = {"retcode": 200000, "msg": "success", "data": res_list}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


app.add_url_rule('/jwt_create', view_func=JwtCreate.as_view('jwt_create'))
app.add_url_rule('/jwt_check', view_func=JwtCheck.as_view('jwt_check'))


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777, use_reloader=False)
