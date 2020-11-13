# -*- coding:utf-8 -*-
# Author      : suwei<suwei@yuchen.net.cn>
# Datetime    : 2019-11-02 19:55
# User        : suwei
# Product     : PyCharm
# Project     : DemoLearn
# File        : logger_model.py
# Description : 文件说明
import logging
from logging import handlers


class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, level='debug', when='D', backCount=90,
                 fmt='%(levelname)s: %(message)s; %(funcName)s() - %(pathname)s[line:%(lineno)d] - %(asctime)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别

        self.sh = logging.StreamHandler()  # 往屏幕上输出
        self.sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        self.logger.addHandler(self.sh)  # 把对象加到logger里

        self.th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                                    encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        # 实例化TimedRotatingFileHandler
        # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        self.th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(self.th)

    def release(self):
        try:
            self.logger.removeHandler(self.sh)
            self.logger.removeHandler(self.th)
        except Exception as e:
            print('log Handler remove：', e)

    # def __del__(self):
    #     self.release()
