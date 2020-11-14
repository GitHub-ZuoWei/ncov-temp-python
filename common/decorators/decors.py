from functools import wraps
from flask import request, Response
import json

from common.utils.util_jwt import JwtUtils
from config import log


def jwt_token_requires(func):
    @wraps(func)
    def wapper(*args, **kwargs):
        try:
            log.info("jwt_token_requires")
            data = request.get_data()
            json_data = json.loads(data.decode('utf-8'))
        except Exception as e:
            res_dict = {"retcode": 999999, "msg": "json format error:  " + str(e), "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        token = json_data.get('token', None)
        if not token:
            res_dict = {"retcode": 999999, "msg": "need token,please login to get", "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
        jwt_utils = JwtUtils()
        is_jwt_token = jwt_utils.check(token)
        if is_jwt_token['status']:
            return func(*args, **kwargs)
        else:
            res_dict = {"retcode": 999999, "msg": is_jwt_token['error'], "data": False}
            return Response(json.dumps(res_dict, ensure_ascii=False), status=500, content_type='application/json')
    return wapper
