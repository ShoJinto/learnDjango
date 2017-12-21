#!/usr/bin/env python
# coding:utf-8

import urllib2
from urllib2 import HTTPError, URLError

from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.header import Header

import logging
from os import path, makedirs

import redis
from redis.exceptions import RedisError

import config


def redisClient(host=config.redis_host, port=config.redis_port):
    '''
    redis object 返回redis实例
    host    :redis server host
    port    :redis server port
    '''
    try:
        pool = redis.ConnectionPool(host=host, port=port)
        r = redis.Redis(connection_pool=pool)
        return r
    except RedisError as err:
        logging.error("Redis error: " + str(err))


# logger setting
if path.exists(config.logpath) is not True:
    makedirs(config.logpath)
logger = logging.basicConfig(
    filename=config.logpath + "check_api.log",
    format="%(asctime)s -%(name)s-%(levelname)s-%(module)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p",
    level=logging.DEBUG
)


def sendemail(submsg, frommsg, msg):
    '''
    need three parameters
    submsg:     subject string
    frommsg:    email from where
    msg:        email content
    '''
    message = MIMEText(msg, "plain", "utf-8")  # 设置邮件内容
    message['From'] = Header(frommsg)
    message['To'] = Header("mm-ops", "utf-8")

    subject = submsg
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(config.mail_host, 25)
        smtpObj.login(config.mail_user, config.mail_pass)
        smtpObj.sendmail(config.sender, config.receivers, message.as_string())
        logging.info("send warning message successfully")
    except smtplib.SMTPException as err:
        logging.error("send warning message failed " + str(err))
    except Exception as err:
        logging.error("send warning message failed " + str(err))


def reporter(station, subject, reporter, msg, status_code=None):
    '''
    this is a sendmail call function
    station     station name
    sta_info    station information
    report      senduser
    msg         error message
    1. 将第一次发送报警邮件的时间写入redis，再次发送报警邮件的时候将会检查两个时间的差值，
    如果超过config.rate这顶的分钟数就不进行报警邮件发送
    2. 该站点报警邮件被忽略时，将会收到一封被忽略的邮件
    '''
    rep_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status_code is None:
        status_code = 400
    if status_code < 400:
        sendemail(subject, reporter, subject + "\nurl: " + msg + "\nat: " +
                  rep_time)  # add timestemp
        logging.info(subject + ": " + msg)
        return None

    for st, opt in redisClient().hgetall('retry_list').items():
        if st == station:
            opt = eval(opt)  # str to dict using eval
            try:
                first_rep_time = opt['first_rep_time']
            except KeyError:
                opt['first_rep_time'] = rep_time
                redisClient().hset('retry_list', station, opt)
                first_rep_time = opt['first_rep_time']

            interval = (datetime.now() -
                        datetime.strptime(first_rep_time,
                                          '%Y-%m-%d %H:%M:%S')).seconds / 60  # minutes
            if interval > config.rate:
                try:
                    # 判断该站点是否发送过忽略报警邮件
                    # 如果发生异常说明没有发送过忽略邮件
                    # 发送过忽略报警邮件的站点将不发送被忽略邮件
                    is_send_notify = opt['is_send_notify']
                    if is_send_notify:
                        pass
                except KeyError:
                    sendemail(subject, reporter,
                              "%s\nurl:%s warnning more than %s hours was ignored\nat: %s"
                              % (subject, msg, interval / 60, rep_time))
                    opt['is_send_notify'] = True
                    redisClient().hset('retry_list', station, opt)
            else:
                sendemail(subject, reporter, subject + "\nurl: " + msg + "\nat: " +
                          rep_time)  # add timestemp
                logging.error(subject + ": " + msg)


def errorHandling(station, url, err, status_code=None):
    '''
    将经过检查有误的站点和错误次数作为reids的key和value进行存放，并设置key的超时时间。
    这样就达到了在规定时间内如果错误次数超过规定次数就进行报警的目的
    '''
    # 如果该站点是第一次被检测出有问题，说明redis中根本就没有该站点的任何信息，这个if not ... else 是对错误次数进行初始化
    if not redisClient().get(station):
        er_count = 0
        redisClient().set(
            station, int(er_count) + 1, ex=config.interval)
    else:
        # 由于从redis中get到的value是str类型所以需要进行数据类型转换
        er_count = int(redisClient().get(station))
        ttl = redisClient().ttl(
            station)  # 获取redis中问题站点错误次数过期时间，用于刷新超时时间
        redisClient().set(station, int(er_count) + 1, ex=ttl)

    if er_count > config.count:
        # 将需要重新检测的车站信息放入redis中
        try:
            # 检测重试列表中是否存在数据，如果产生异常说明列表中不存在该站点
            redisClient().hgetall('retry_list')[station]
            pass
        except KeyError:
            redisClient().hset("retry_list", station, {'url': url})
        reporter(station, "[%s]:%s" % (station, str(err)),
                 "check api", url, status_code)
        redisClient().delete(station)  # 达到报警条件，发送完报警之后，需要对redis中的信息进行重置


def checking(station, url, isretry=False):
    '''
    this is checking function
    need two parameters
    station:    is station name
    url:          is station threeparty api url
    '''
    try:
        response = urllib2.urlopen(url)
        status_code = response.getcode()
        if isretry:
            # 发送故障恢复邮件
            reporter(station, "[%s]:%s" %
                     (station, "is recovered!"), "check api",
                     url, status_code=status_code)
            # 重新检测发现没有问题的车站将从redis移除,重置状态信息
            redisClient().hdel("retry_list", station)
        else:
            logging.info("[%s]:%s is ok!" % (station, url))
    except HTTPError as err:
        errorHandling(station, url, err)
    except URLError as err:
        errorHandling(station, url, err)


def check_api():
    '''
    this is check api heath function
    '''
    retry_list = redisClient().hgetall("retry_list").items()
    if config.useUrls is True:
        station = config.station_name
        for url in config.urls:
            checking(station, url)

        if redisClient().hlen("retry_list") > 0:
            for re_station, opt in retry_list:
                re_url = eval(opt)['url']
                checking(re_station, re_url, isretry=True)
    else:
        for station, url in config.stationUrlMapping.items():
            checking(station, url)

        if redisClient().hlen("retry_list") > 0:
            for re_station, opt in retry_list:
                re_url = eval(opt)['url']
                checking(re_station, re_url, isretry=True)


if __name__ == "__main__":
    check_api()
