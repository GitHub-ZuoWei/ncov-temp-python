from flask import Flask, request, Response
from flask.views import MethodView
from common.db.MysqlDB import DBCreateSql
from flask_cors import *
from config import SOLR_ADDR
import json
import pysolr
from common.utils.util_response import return_response
from common.decorators.decors import jwt_token_requires
from common.utils.util_jwt import JwtUtils
from common.utils.util_str import date2str
from config import PDFS

app = Flask(__name__)
CORS(app)
pysolr_solr = pysolr.Solr(SOLR_ADDR)

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

        if not name:
            return Response(
                json.dumps({"retcode": 999999, "msg": "缺少參數name", "data": False}, ensure_ascii=False),
                status=500,
                content_type="application/json")
        db_sql = DBCreateSql()
        person_sql = """
                        SELECT * FROM person_info WHERE person_name = '{}'""".format(
            name)
        db_person_res = db_sql.find_all(person_sql)
        db_person_res = db_person_res[0]
        if not db_person_res:
            return Response(
                json.dumps({"retcode": 999999, "msg": "查無此人", "data": False}, ensure_ascii=False),
                status=500,
                content_type="application/json")

        base_info = {
            "name": name,
            "sex": '男' if db_person_res[2] == '1' else '女',
            "age": db_person_res[3],
            "address": db_person_res[6],
            "phone_number": db_person_res[7],
            "hospitalized_number": db_person_res[8]
        }

        tmp_file_sql = """
                                                                    SELECT person_name,file_path FROM file_record WHERE type = 2 AND person_name = '{}'
                                                                    """.format(name)

        db_tmp_file_res = db_sql.find_all(tmp_file_sql)

        tmp_img_list = list()
        for item in db_tmp_file_res:
            v_list = item[1].split("/")
            imgname = v_list[-1]
            imgurl = item[1]
            tmp_dict = {
                "imgname": imgname,
                "imgurl": 'static/' + imgurl
            }

            tmp_img_list.append(tmp_dict)

        file_sql = """
                                                        SELECT person_name,file_date,file_path FROM file_record WHERE type = 1 AND person_name = '{}'
                                                        """.format(name)

        db_file_res = db_sql.find_all(file_sql)
        if not db_file_res:
            res_dict = {"retcode": 200000, "msg": "success", "data": []}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')

        res_list = []
        time_dict = {}
        for file in db_file_res:
            if str(file[1]) in time_dict.keys():
                time_dict[str(file[1])].append(file[2])
            else:
                time_dict[str(file[1])] = [file[2]]
        total = len(time_dict.keys())
        for k, v in time_dict.items():
            abc = k.split(" ")
            t = abc[0]
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
                "start_time": t,
                "img_list": img_list
            }
            res_list.append(dict)

        dict = {"base_info": base_info, "tmp_img_list": tmp_img_list, "ct_img_list": res_list}
        res_dict = {"retcode": 200000, "msg": "success", "data": dict}
        return Response(json.dumps(res_dict, ensure_ascii=False), status=200, content_type='application/json')


# 首页搜索
class IndexSearch(MethodView):
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
        key_words = json_data.get('keywords', None)
        person_name = json_data.get('personName', None)
        type = json_data.get('type', None)
        start_time = json_data.get('startTime', None)
        end_time = json_data.get('endTime', None)
        select_type = json_data.get('selectType', None)
        if not page or not size:
            page = 1
            size = 30
        # solr 查询条件
        solr_query = ''
        if person_name:
            solr_query += 'person_name:' + person_name
        if key_words:
            if solr_query:
                solr_query += ' && (person_name:' + key_words + ' || content:' + key_words + ')'
            else:
                solr_query += '(person_name:' + key_words + ' || content:' + key_words + ')'
        if type:
            if solr_query:
                if type == '化验单':
                    type = '报告单'
                if type == '核酸检测':
                    type = '核酸扩增荧光定量检测报告单'
                solr_query += ' && (category:"' + '报告单' + type + '" || type:"' + type + '")'
            else:
                solr_query += ' (category:"' + type + '" || type:"' + type + '")'
        if start_time and end_time:
            if solr_query:
                solr_query += ' && start_time:[' + start_time + ' TO ' + end_time + ']'
            else:
                solr_query += 'start_time:[' + start_time + ' TO ' + end_time + ']'

        print(solr_query)

        # 判断查询类型   人物详情页接口
        if select_type == 1:
            person_info_data_one = pysolr_solr.search(solr_query, **{'start': (int(page) - 1) * size, 'rows': size,
                                                                 'fq': '-category:"报告单"',
                                                                 'sort': 'start_time desc', })
            person_info_data_two = pysolr_solr.search(solr_query, **{'start': (int(page) - 1) * size, 'rows': size,
                                                                 'fq': 'category:"报告单"',
                                                                 'sort': 'start_time desc', })

        search_data = pysolr_solr.search(solr_query, **{'start': (int(page) - 1) * size, 'rows': size,
                                                        'sort': 'start_time desc', })

        # 侧边 分类
        sidebar_type_data_one = pysolr_solr.search(solr_query,
                                                   **{'rows': '30', 'sort': 'start_time desc', 'facet': 'on',
                                                      'facet.field': 'category'})
        sidebar_type_data_two = pysolr_solr.search(solr_query,
                                                   **{'rows': '30', 'sort': 'start_time desc', 'facet': 'on',
                                                      'facet.field': 'type'})
        sidebar_type_data = {}
        category_data = sidebar_type_data_one.facets['facet_fields']['category']
        for index, item in enumerate(category_data):
            if index % 2 == 0:
                if index == len(category_data) - 1:
                    break
                sidebar_type_data[category_data[index]] = category_data[index + 1]
        category_data = sidebar_type_data_two.facets['facet_fields']['type']
        for index, item in enumerate(category_data):
            if item == '核酸扩增荧光定量检测报告单':
                if index % 2 == 0:
                    if index == len(category_data) - 1:
                        break
                    sidebar_type_data["核酸检测"] = category_data[index + 1]
        sort_type = dict(sorted(sidebar_type_data.items(), key=lambda x: x[1], reverse=True))
        type_data = []
        for item in sort_type:
            type_data.append({"name": "化验单" if item == '报告单' else item, "value": sort_type[item]})

        # 侧边 关键词
        sidebar_keywords_data = pysolr_solr.search(solr_query,
                                                   **{'rows': '30', 'sort': 'start_time desc', 'facet': 'on',
                                                      'facet.field': 'content'})
        content_data = []
        category_data = sidebar_keywords_data.facets['facet_fields']['content']
        for index, item in enumerate(category_data):
            temp_person_data = {}
            if len(str(item)) > 1:
                if index % 2 == 0:
                    if index == len(category_data) - 1:
                        break
                    temp_person_data['name'] = category_data[index]
                    temp_person_data['value'] = category_data[index + 1]
                if temp_person_data:
                    content_data.append(temp_person_data)

        # 侧边 相关患者
        sidebar_person_data = pysolr_solr.search(solr_query,
                                                 **{'rows': '30', 'sort': 'start_time desc', 'facet': 'on',
                                                    'facet.field': 'person_name'})
        person_data = []
        category_data = sidebar_person_data.facets['facet_fields']['person_name']
        for index, item in enumerate(category_data):
            temp_person_data = {}
            if index % 2 == 0:
                if index == len(category_data) - 1:
                    break
                temp_person_data['name'] = category_data[index]
                temp_person_data['value'] = category_data[index + 1]
            if temp_person_data:
                person_data.append(temp_person_data)

        search_data.raw_response["response"]['page'] = page
        search_data.raw_response["response"]['size'] = size
        search_data.raw_response["response"]['sidebarType'] = type_data
        search_data.raw_response["response"]['sidebarKeywords'] = content_data
        search_data.raw_response["response"]['sidebarPerson'] = person_data
        del search_data.raw_response["response"]['start']
        if not select_type:
            return return_response(search_data.raw_response["response"], 200)
        else:
            del person_info_data_one.raw_response["response"]['numFound']
            person_info_data_one.raw_response["response"]['page'] = page
            person_info_data_one.raw_response["response"]['size'] = size
            person_info_data_one.raw_response["response"]['sidebarType'] = type_data
            person_info_data_one.raw_response["response"]['sidebarKeywords'] = content_data
            person_info_data_one.raw_response["response"]['docsTwo'] = person_info_data_two.raw_response["response"]["docs"]
            return return_response(person_info_data_one.raw_response["response"], 200)

app.add_url_rule('/user/login', view_func=Login.as_view('login'))
app.add_url_rule('/test_token', view_func=TestToken.as_view('test_token'))
app.add_url_rule('/ct/list', view_func=CtList.as_view('ct_list'))
app.add_url_rule('/ct/disease/list', view_func=CtDetails.as_view('ct_detail'))
app.add_url_rule('/user/detail/base_ct_temp', view_func=UserDetailBaseCtTemp.as_view('user_detail'))

app.add_url_rule('/search/all', view_func=IndexSearch.as_view('index_search'))


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777, use_reloader=False)
