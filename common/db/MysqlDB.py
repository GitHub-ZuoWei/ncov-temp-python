# -*- coding:utf-8 -*-
# Author      : suwei<suwei@yuchen.net.cn>
# Datetime    : 2019-11-06 17:14
# User        : suwei
# Product     : PyCharm
# Project     : EventAlgorithm
# File        : tool_mysql.py
# Description : MySQL数据库操作
import time

import pymysql

from config import MYSQL_CONF, log


class DBCreateSql:
    # 构造函数
    def __init__(self, sql_conf=MYSQL_CONF, log=log):
        # 加入日志
        self.log = log
        self.connectDatabase(sql_conf)

    # 连接数据库
    def connectDatabase(self, sql_conf):
        try:
            self.conn = pymysql.connect(sql_conf['ip'], sql_conf['user'], sql_conf['pwd'],
                                        sql_conf['db'], sql_conf['port'])
            self.cur = self.conn.cursor()
            self.log.info('sql connect success')
            return True
        except Exception as e:
            self.log.error(e)
            self.log.info('sql connect filed')
            return False

    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn:
            self.conn.close()
        if self.cur:
            self.cur.close()
        self.log.info('sql close success')
        return True

    # 查询操作
    def find_all(self, sql):
        try:
            self.cur.execute(sql)
            return self.cur.fetchall()
        except Exception as e:
            self.log.error(e)
            self.log.error("execute failed: " + sql)
            return None

    # 查询操作
    def find_one(self, sql):
        # 连接数据库
        try:
            self.cur.execute(sql)
            return self.cur.fetchone()
        except Exception as e:
            self.log.error(e)
            self.log.error("execute failed: " + sql)
            return None

    # 插入数据库 -- 直接插入
    def insert(self, table, keys, values):
        b = True
        try:
            sql = "insert into %s %s values %s" % (table, keys, values)
            self.cur.execute(sql)
        except Exception as e:
            b = False
            self.conn.rollback()
            self.log.info("sql exec error :%s" % sql)
            self.log.error(e)
        return b

    # 插入数据库，插入之前检查是否有重复
    def insert_res(self, table, keys, keys_list, values_list):
        select_v = ''
        for i in values_list:
            select_v += '"' + i + '",'
        select_v = select_v[:-1]

        where_v = ''
        for j in range(len(keys_list)):
            if j > 0:
                k = keys_list[j]
                v = values_list[j]
                v_rel = self.utils.change_str_sql(v)
                where_v += k + '="' + v_rel + '"' + ' and '
        where_v = where_v[:-4]
        sql = "insert into %s %s select %s from DUAL where not exists " \
              "(select 1 from %s where %s)" % (table, keys, select_v, table, where_v)
        print(sql)
        b = True
        try:
            # sql = "insert into %s %s values %s" % (table, keys, values)
            self.cur.execute(sql)
        except Exception as e:
            b = False
            self.conn.rollback()
            self.log.info("sql exec error:%s" % sql)
            self.log.error(e)
        return b

    # 执行sql语句; 参数：sql语句; 返回：无
    def execute_sql(self, sql):
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return self.cur.fetchall()
        except Exception as e:
            self.log.error("sql execute failed:" + sql)
            self.conn.rollback()
            return None

    def execute_sql_many(self, sql, values):
        try:
            self.cur.executemany(sql, values)
            self.conn.commit()
        except Exception as e:
            print(e)

    def _format_sql_sent(self, table, item_dict):
        keys = tuple(item_dict.keys())
        sql_insert = 'insert into ' + table + ' ' + str(keys) + " values (%s)" % ('%s,' * len(keys))[:-1]
        sql_insert = sql_insert.replace("'", '`')
        return sql_insert

    def insert_one(self, table, item_dict):
        try:
            print('--' * 8)
            print(item_dict)
            print('--' * 8)
            sql = self._format_sql_sent(table, item_dict)
            self.cur.execute(sql, tuple(item_dict.values()))
            self.conn.commit()
        except Exception as e:
            print(e)
            print(sql)
            self.conn.rollback()
            self.log.info("sql execute failed:%s" % str(e))

    def insert_many(self, table, item_dict_list):
        try:
            if item_dict_list:
                sql = self._format_sql_sent(table, item_dict_list[0])
                value_list = [tuple(x.values()) for x in item_dict_list]
                self.cur.executemany(sql, value_list)
                self.conn.commit()
            else:
                self.log.info('insert data is null')
        except Exception as e:
            print('insert data error')
            print(e)
            self.conn.rollback()
            print(sql)
            self.log.info("sql execute failed:%s" % str(e))
