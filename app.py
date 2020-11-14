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

app.add_url_rule('/search/all', view_func=IndexSearch.as_view('index_search'))


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7777, use_reloader=False)
