from flask import Flask, request, Response
from flask.views import MethodView
from common.db.MysqlDB import DBCreateSql

import json

from common.decorators.decors import jwt_token_requires
from common.utils.util_jwt import JwtUtils
from common.utils.util_str import date2str

app = Flask(__name__)


class Login(MethodView):

    def post(self):
        data = request.get_data()

        try:
            json_data = json.loads(data.decode('utf-8'))
        except Exception as e:
            res_dict = {"retcode": 999999, "msg": "json format error:  " + str(e), "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')

        if not isinstance(json_data, dict):
            res_dict = {"retcode": 999999, "msg": "參數data數據格式有誤", "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')

        uname = json_data.get('username', None)

        user_pwd = json_data.get('password', None)
        db_sql = DBCreateSql()
        user_sql = """
            SELECT password FROM sys_user WHERE username = '{}'
            """.format(uname)
        db_res_user = db_sql.find_all(user_sql)
        if not db_res_user:
            res_dict = {"retcode": 999999, "msg": "此用戶不存在", "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        else:
            md5_password = db_res_user[0][0]
            if md5_password == user_pwd:
                jwt_utils = JwtUtils()
                jwt_token = jwt_utils.create()
                data = {"token": jwt_token}
                res_dict = {"retcode": 200000, "msg": " login success", "data": data}
                return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')
            else:
                res_dict = {"retcode": 999999, "msg": "用戶名或密碼錯誤", "data": False}
                return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')


class TestToken(MethodView):
    decorators = [jwt_token_requires]

    def post(self):
        data = request.get_data()

        try:
            json_data = json.loads(data.decode('utf-8'))
        except Exception as e:
            res_dict = {"retcode": 999999, "msg": "json format error:  " + str(e), "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        test = json_data.get('test', None)
        data = {"test": test}
        res_dict = {"retcode": 200000, "msg": "success", "data": data}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


class CtList(MethodView):
    # decorators = [jwt_token_requires]

    def post(self):
        data = request.get_data()

        try:
            json_data = json.loads(data.decode('utf-8'))
        except Exception as e:
            res_dict = {"retcode": 999999, "msg": "json format error:  " + str(e), "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        page = json_data.get('page', None)
        size = json_data.get('size', None)
        name = json_data.get('name', None)
        type = json_data.get('type', None)
        start_time = json_data.get('start_time', None)
        end_time = json_data.get('end_time', None)
        db_sql = DBCreateSql()
        file_sql = """
                    SELECT person_name,file_date,file_path FROM file_record WHERE person_name = '{}' AND file_date > '{}' AND file_date < '{}'
                    """.format(name, start_time, end_time)
        db_file_res = db_sql.find_all(file_sql)
        if not db_file_res:
            res_dict = {"retcode": 200000, "msg": "success", "data": []}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')
        res_list = []
        for file in db_file_res:
            name = file[0]
            file_date = date2str(file[1])
            file_path = file[2]
            tmp_dict = {"name": name, "file_date": file_date, "file_path": file_path}
            res_list.append(tmp_dict)
        data = {"res_list": res_list}
        res_dict = {"retcode": 200000, "msg": "success", "data": data}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


app.add_url_rule('/user/login', view_func=Login.as_view('login'))
app.add_url_rule('/test_token', view_func=TestToken.as_view('test_token'))
app.add_url_rule('/ct/list', view_func=CtList.as_view('ct_list'))


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777, use_reloader=False)
