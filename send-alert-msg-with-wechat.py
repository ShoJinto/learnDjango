#!~/venv/bin/python
# -*-coding:utf8 -*-
# filename: send-alert-msg-with-wechat.py
# by: jtxiao
#

'''
help:
send zabbix alert message with wechat public number.
test on zabbix 3.0.10
command:
> pip install virtualenv
> virtualenv venv
> . venv/bin/activate
> pip install requests redis
'''

import sys
import requests
import json, urllib3
import redis
import logging

urllib3.disable_warnings()

APPID = 'your appid'
APPSECRET = 'your appsecret'

RECEVER = ['openid1', 'openid2']

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

# log
logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)

# StreamHandler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(level=logging.DEBUG)
logger.addHandler(stream_handler)

# FileHandler
handler = logging.FileHandler('wechat.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_access_token(appid, appsecret, retry=False):
    '''
    根据微信公帐号关于access_token的相关要求和规定，此处引入redis用于鉴别access_token是否过期
    :param appid:
    :param appsecret:
    :return: ACCESS_TOKEN
    '''
    get_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(
        appid, appsecret)
    r = redis.Redis(host='localhost', port=6379, db=2)
    ACCESS_TOKEN = r.get('WX_ACCESS_TOKEN')

    if ACCESS_TOKEN is not None and retry is False:
        logger.info('token from redis')
        return ACCESS_TOKEN
    elif retry or ACCESS_TOKEN is None:
        token_entity = json.loads(requests.get(get_token_url).content)
        ACCESS_TOKEN = str(token_entity['access_token'])
        TOKEN_EXPIES = int(token_entity['expires_in'])
        r.set('WX_ACCESS_TOKEN', ACCESS_TOKEN, ex=TOKEN_EXPIES)
        logger.info('token from weixin, retry:%s', retry)
        return ACCESS_TOKEN


def send_message(access_token, recever, msg):
    for openid in recever:
        '''批量发送消息'''
        get_send_msg_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={0}'.format(access_token)
        msg_template = '{"touser":"%s","msgtype":"text","text":{"content":"%s"}}' % (openid, msg)
        r = requests.post(get_send_msg_url, data=msg_template)
        return r.json()


if __name__ == '__main__':
    try:
        if len(sys.argv) > 4 and len(sys.argv) == 0:
            print 'Please usage:%s <%s> <%s>' % (sys.argv[0], 'subject', 'content')
        else:
            Recever = sys.argv[1]			#{ALERT.SENDTO}
            Subject = sys.argv[2]			#{ALERT.SUBJECT}
            Content = sys.argv[3]			#{ALERT.MESSAGES}
            MSG = Subject + '\n' + Content

            ACCESS_TOKEN = get_access_token(appid=APPID, appsecret=APPSECRET)
            status = send_message(access_token=ACCESS_TOKEN, recever=RECEVER, msg=MSG)
            logger.info(status)

            if status['errcode'] != 0:
                ACCESS_TOKEN = get_access_token(appid=APPID, appsecret=APPSECRET, retry=True)
                status = send_message(access_token=ACCESS_TOKEN, recever=RECEVER, msg=MSG)
                logger.info('retry result:', status)
    except Exception as e:
        if e.message.find('index'):
            print 'Please usage:%s <%s> <%s> <%s>' % (sys.argv[0], 'sendto', 'subject', 'content')
        else:
            logger.error('Error:', exc_info=True)
