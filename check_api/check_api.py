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


def reporter(station, subject, reporter, msg):
    '''
    this is a sendmail call function
    sta_info    station information
    report      senduser
    msg         error message
    '''
    st_list = []
    first_rep_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if len(redisClient().hgetall('interval')) > 0:
        for st, timestr in redisClient().hgetall('interval').items():
            st_list.append(st)
            if station not in st_list:
                redisClient().hset('interval', station, first_rep_time)
            interval = (datetime.now() -
                        datetime.strptime(timestr,
                                          '%Y-%m-%d %H:%M:%S')).seconds / 60  # minutes
            if interval > config.rate:
                pass
            else:
                sendemail(subject, reporter, subject + "\nurl: " + msg + "\nat: " +
                          first_rep_time)  # add timestemp
                logging.error(subject + ": " + msg)
    else:
        redisClient().hset('interval', station, first_rep_time)
        sendemail(subject, reporter, subject + "\nurl: " + msg + "\nat: " +
                  first_rep_time)  # add timestemp
        logging.error(subject + ": " + msg)


def errorHandling(station, url, err):
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
        reporter(station, "[%s]:%s" % (station, str(err)), "check api", url)
        redisClient().delete(station)  # 达到报警条件，发送完报警之后，需要对redis中的信息进行重置
        # redisClient().rpush("retrystation_list",station)
        # 将需要重新检测的车站信息放入redis中
        redisClient().hset("retrystation_list", station, url)


def checking(station, url, isretry=False):
    '''
    this is checking function
    need two parameters
    station:    is station name
    url:          is station threeparty api url
    '''
    response_code = dict()
    try:
        response = urllib2.urlopen(url)
        response_code[url] = response.getcode()
        if isretry:
            reporter(station, "[%s]:%s" %
                     (station, "is recovered!"), "check api", url)
            # 重新检测发现没有问题的车站将从redis移除
            redisClient().hdel("retrystation_list", station)
            redisClient().hdel("interval", station)
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
    retry_list = redisClient().hgetall("retrystation_list").items()
    if config.useUrls is True:
        station = config.station_name
        for url in config.urls:
            checking(station, url)

        if redisClient().hlen("retrystation_list") > 0:
            for re_station, re_url in retry_list:
                checking(re_station, re_url, isretry=True)
    else:
        for station, url in config.stationUrlMapping.items():
            checking(station, url)

        if redisClient().hlen("retrystation_list") > 0:
            for re_station, re_url in retry_list:
                checking(re_station, re_url, isretry=True)


if __name__ == "__main__":
    check_api()
