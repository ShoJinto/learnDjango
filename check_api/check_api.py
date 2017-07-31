#!/usr/bin/env python
#coding:utf-8

import urllib2 
from urllib2 import HTTPError,URLError

# from urllib2 import request
# from urllib.error import HTTPError,URLError

import smtplib
from email.mime.text import MIMEText
from email.header import Header

import logging
from os import path,makedirs

import redis
from redis.exceptions import RedisError

import config


def redisClient(host,port):
    '''
    redis object 返回redis实例
    host    :redis server host
    port    :redis server port
    '''
    try:
        pool= redis.ConnectionPool(host=host,port=port)
        r=redis.Redis(connection_pool=pool)
        return r
    except RedisError as err:
        logging.error("Redis error: "+str(err))


#logger setting
if path.exists(config.logpath) != True: makedirs(config.logpath,existk=True)
logger=logging.basicConfig(
    filename=config.logpath+"check_api.log",
    format="%(asctime)s -%(name)s-%(levelname)s-%(module)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p",
    level=logging.DEBUG
    )
    

def sendemail(submsg,frommsg,msg):
    '''
    need three parameters
    submsg:     subject string
    frommsg:    email from where
    msg:        email content
    '''        
    message=MIMEText(msg,"plain","utf-8") # 设置邮件内容
    message['From']=Header(frommsg)
    message['To']=Header("mm-ops","utf-8")
    
    subject=submsg
    message['Subject']=Header(subject,'utf-8')
    
    try:
        smtpObj=smtplib.SMTP()
        smtpObj.connect(config.mail_host,25)
        smtpObj.login(config.mail_user,config.mail_pass)
        smtpObj.sendmail(config.sender, config.receivers, message.as_string())
        logging.info("send warning message successfully")
    except smtplib.SMTPException as err:
        logging.error("send warning message failed "+str(err))
    except Exception as err:
        logging.error("send warning message failed "+str(err))

   
def reporter(sta_info,report,msg):
    '''
    this is a sendmail call function
    sta_info    statation information
    report      senduser
    msg         error message
    '''
    logging.error(sta_info+": "+msg)
    sendemail(sta_info,report,sta_info+": "+msg)
    
def errorHandling(statation,url,err):
    '''
    将经过检查有误的站点和错误次数作为reids的key和value进行存放，并设置key的超时时间。这样就达到了在规定时间内如果错误次数超过规定次数就进行报警的目的
    '''
    #如果该站点是第一次被检测出有问题，说明redis中根本就没有该站点的任何信息，这个if not ... else 是对错误次数进行初始化
    if not redisClient(config.redis_host, config.redis_port).get(statation):
        er_count=0
    else:
        er_count=redisClient(config.redis_host, config.redis_port).get(statation)   
                 
    redisClient(config.redis_host, config.redis_port).set(statation, int(er_count)+1, ex=config.interval)
    
    if er_count>=config.count:
        reporter("[%s]:%s" % (statation,url), "check api", str(err))
        redisClient(config.redis_host, config.redis_port).delete(statation) #达到报警条件，发送完报警之后，需要对redis中的信息进行重置

def checking(statation,url):
    '''
    this is checking function
    need two parameters
    statation:    is statation name
    url:          is statation threeparty api url
    '''
    response_code=dict()
    try:
        response=urllib2.urlopen(url)
        response_code[url]=response.getcode()
        logging.info("[%s]:%s is ok!" % (statation,url))
    except HTTPError as err:
        errorHandling(statation, url, err)
    except URLError as err:
        errorHandling(statation, url, err)
    except Exception as err:
        errorHandling(statation, url, err)
        
def check_api():
    '''
    this is check api heath function
    '''  
    statation=config.statation_name  
    if config.useUrls == True: 
        for url in config.urls:
            checking(statation,url)
    else:
        for statation, url in config.statationUrlMapping.items():
            checking(statation,url)


if __name__=="__main__":
    check_api()
