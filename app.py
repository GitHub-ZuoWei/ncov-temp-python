from flask import Flask, request, Response
from flask.views import MethodView
from common.db.MysqlDB import DBCreateSql
from flask_cors import *
import json

from common.decorators.decors import jwt_token_requires
from common.utils.util_jwt import JwtUtils
from common.utils.util_str import date2str
from config import PDFS

app = Flask(__name__)
CORS(app)


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
        page = json_data.get('page', 1)
        page_size = json_data.get('size', 10)
        name = json_data.get('name', None)
        type = json_data.get('type', None)
        start_time = json_data.get('start_time', None)
        end_time = json_data.get('end_time', None)

        db_sql = DBCreateSql()
        if type == 'ctreport':
            if start_time and end_time and name:
                file_sql = """
                            SELECT person_name,file_date,file_path FROM file_record WHERE person_name = '{}' AND type = 1 AND file_date > '{}' AND file_date < '{}'
                            """.format(name, start_time, end_time)
            elif start_time and end_time:
                file_sql = """
                                            SELECT person_name,file_date,file_path FROM file_record WHERE type = 1 AND file_date > '{}' AND file_date < '{}'
                                            """.format(start_time, end_time)
            elif name:
                file_sql = """
                                                            SELECT person_name,file_date,file_path FROM file_record WHERE type = 1 AND person_name = '{}'
                                                            """.format(name)
            else:
                file_sql = """
                                        SELECT person_name,file_date,file_path FROM file_record WHERE type = 1 """

            db_file_res = db_sql.find_all(file_sql)
            if not db_file_res:
                res_dict = {"retcode": 200000, "msg": "success", "data": []}
                return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')

            res_total = len(db_file_res)
            max_page, a = divmod(res_total, page)

            if page < 1 or page > max_page:
                res_dict = {"retcode": 999999, "msg": "page not found", "data": []}
                return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')

            start = (page - 1) * page_size
            end = page * page_size
            data = db_file_res[start:end]
            # data = db_file_res
            res_list = []
            time_dict = {}
            for file in data:
                if str(file[1]) in time_dict.keys():
                    time_dict[str(file[1])].append(file[2])
                else:
                    time_dict[str(file[1])] = [file[2]]
            total = len(time_dict.keys())
            for k, v in time_dict.items():
                img_list = list()
                for i in v:
                    v_list = i.split("/")
                    imgname = v_list[-1]
                    name = v_list[1]
                    imgurl = i
                    tmp_dict = {
                        "imgname": imgname,
                        "imgurl": 'static/' + imgurl
                    }
                    if len(img_list) > 3:
                        break
                    img_list.append(tmp_dict)

                dict = {
                    "name": name,
                    "start_time": k,
                    "img_list": img_list
                }
                res_list.append(dict)
        else:
            if name:
                file_sql = """
                                                        SELECT person_name,file_path FROM file_record WHERE person_name = '{}' AND type = 2""".format(
                    name)
            else:
                file_sql = """
                                                                    SELECT person_name,file_path FROM file_record WHERE type = 2"""

            db_file_res = db_sql.find_all(file_sql)

            if not db_file_res:
                res_dict = {"retcode": 200000, "msg": "success", "data": []}
                return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')

            total = len(db_file_res)
            max_page, a = divmod(total, page)

            if page < 1 or page > max_page:
                res_dict = {"retcode": 999999, "msg": "page not found", "data": []}
                return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')

            start = (page - 1) * page_size
            end = page * page_size
            data = db_file_res[start:end]
            # data = db_file_res
            res_list = []
            img_list = list()
            name_dict = {}
            for file in data:
                if str(file[0]) in name_dict.keys():
                    name_dict[file[0]].append(file[1])
                else:
                    name_dict[file[0]] = [file[1]]
            total = len(name_dict.keys())

            for k, v in name_dict.items():
                img_list = list()
                for i in v:
                    v_list = i.split("/")
                    imgname = v_list[-1]
                    name = v_list[1]
                    imgurl = i
                    tmp_dict = {
                        "imgname": imgname,
                        "imgurl": 'static/' + imgurl
                    }
                    if len(img_list) > 3:
                        break
                    img_list.append(tmp_dict)

                dict = {
                    "name": name,
                    "img_list": img_list
                }
                res_list.append(dict)

        data = {"total": total, "page": page, "size": page_size, "rows": res_list}
        res_dict = {"retcode": 200000, "msg": "success", "data": data}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


class CtDetails(MethodView):
    # decorators = [jwt_token_requires]

    def post(self):
        data = request.get_data()
        try:
            json_data = json.loads(data.decode('utf-8'))
        except Exception as e:
            res_dict = {"retcode": 999999, "msg": "json format error:  " + str(e), "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        name = json_data.get('name', None)
        start_time = json_data.get('start_time', None)

        if not name:
            return Response(
                json.dumps({"retcode": 999999, "msg": "缺少參數name", "data": False}, ensure_ascii=False),
                status=500,
                content_type="application/json")

        if not start_time:
            return Response(
                json.dumps({"retcode": 999999, "msg": "缺少參數start_time", "data": False}, ensure_ascii=False),
                status=500,
                content_type="application/json")

        db_sql = DBCreateSql()
        if start_time and name:
            file_detials_sql = """
                        SELECT file_path FROM file_record WHERE person_name = '{}' AND type = 1 AND file_date = '{}'""".format(
                name, start_time)
        db_file_detials_res = db_sql.find_all(file_detials_sql)

        if not db_file_detials_res:
            res_dict = {"retcode": 200000, "msg": "success", "data": []}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')

        file_time_sql = """
                                                                SELECT DISTINCT file_date FROM file_record WHERE person_name = '{}' AND type = 1""".format(
            name)
        db_file_time_res = db_sql.find_all(file_time_sql)
        time_list = []
        for i in db_file_time_res:
            abc = str(i[0]).split(" ")
            time_list.append(abc[0])

        img_list = list()
        for item in db_file_detials_res:
            v_list = item[0].split("/")
            imgname = v_list[-1]
            name = v_list[1]
            imgurl = item[0]
            tmp_dict = {
                "imgname": imgname,
                "imgurl": 'static/' + imgurl
            }

            img_list.append(tmp_dict)

        dict = {
            "img_list": img_list,
            "time_list": time_list
        }

        res_dict = {"retcode": 200000, "msg": "success", "data": dict}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


class UserDetailBaseCtTemp(MethodView):
    # decorators = [jwt_token_requires]

    def post(self):
        data = request.get_data()
        try:
            json_data = json.loads(data.decode('utf-8'))
        except Exception as e:
            res_dict = {"retcode": 999999, "msg": "json format error:  " + str(e), "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        name = json_data.get('name', None)
        start_time = json_data.get('start_time', None)
        dict = {}
        res_dict = {"retcode": 200000, "msg": "success", "data": dict}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


app.add_url_rule('/user/login', view_func=Login.as_view('login'))
app.add_url_rule('/test_token', view_func=TestToken.as_view('test_token'))
app.add_url_rule('/ct/list', view_func=CtList.as_view('ct_list'))
app.add_url_rule('/ct/disease/list', view_func=CtDetails.as_view('ct_detail'))
app.add_url_rule('/user/detail/base_ct_temp', view_func=UserDetailBaseCtTemp.as_view('user_detail'))


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777, use_reloader=False)
