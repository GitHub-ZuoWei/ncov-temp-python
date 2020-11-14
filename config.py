import os
from common.utils.util_logger import Logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOLR_CONF = {
    'ip': '192.168.10.213',
    'port': 8983,
    'db': 'solr',
    'table': 'medical'
}

SOLR_ADDR = 'http://{}:{}/{}/{}'.format(SOLR_CONF['ip'], str(SOLR_CONF['port']), SOLR_CONF['db'], SOLR_CONF['table'])

MYSQL_CONF = {
    'ip': '192.168.10.222',
    'port': 3306,
    'user': 'root',
    'pwd': '123456',
    'db': 'medical'
}

log_path = BASE_DIR + '/log/ncov.log'

util_log = Logger(log_path)
log = util_log.logger

JWT_SALT = 'iv%x6xo7l7_u9bf_u!9#g#m*)*'

JWT_TIMEOUT = 100

MD5_SALT = 'ncoc_python'

DOCS_PATH = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'common'), 'docs')

PDFS = '/mnt/hgfs/vmshare/ncov_pdfs'