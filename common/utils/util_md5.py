import hashlib
from config import MD5_SALT


class Md5Utils:
    def __init__(self, pwd, salt):
        self.pwd = pwd
        self.salt = salt

    def create_md5(self):
        m = hashlib.md5()
        m.update(bytes(self.pwd + self.salt, encoding="utf8"))
        return m.hexdigest()


if __name__ == '__main__':
    md5_util = Md5Utils('liuhanzhe', MD5_SALT)
    res = md5_util.create_md5()
    print(res)
