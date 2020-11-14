import datetime

import jwt

from config import JWT_SALT, JWT_TIMEOUT


class JwtUtils:
    def create(self):
        headers = {
            'typ': 'jwt',
            'alg': 'HS256'
        }
        payload = {}
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_TIMEOUT)
        return jwt.encode(payload=payload, key=JWT_SALT, algorithm="HS256", headers=headers).decode('utf-8')

    def check(self, token):
        result = {'status': False, 'data': None, 'error': None}
        try:
            verified_payload = jwt.decode(token, JWT_SALT, True)
            result['status'] = True
            result['data'] = verified_payload
        except jwt.exceptions.ExpiredSignatureError:
            result['error'] = 'token已失效'
        except jwt.DecodeError:
            result['error'] = 'token认证失败'
        except jwt.InvalidTokenError:
            result['error'] = '非法的token'
        return result
