#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import public_bz
import wechat_bz
import public_db
from public_bz import storage
from pg import pg
import oper
import datetime
import time_bz
try:
    import wechat_sdk
    from wechat_sdk import WechatBasic
    from wechat_sdk.ext import WechatExt
except ImportError:
    print 'you need install wechat, please run:'
    print 'sudo pip install wechat-sdk'
    exit(1)
config = ConfigParser.ConfigParser()
with open('conf/wechat.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    appid = config.get('app', 'appid')
    appsecret = config.get('app', 'appsecret')
    token = config.get('app', 'token')
    user_name = config.get('app', 'user_name')
    password = config.get('app', 'password')


def sendArticle(openid, articles):
    '''
    发送信息 create by bigzhu at 15/07/24 09:35:31
    '''
    wechat = getWechat()
    try:
        wechat.send_article_message(openid, articles)
    except wechat_sdk.exceptions.OfficialAPIError:
        print 'openid=', openid, ' ', public_bz.getExpInfo()
    except Exception:
        print public_bz.getExpInfo()


def getNewWechatInfo():
    '''
    modify by bigzhu at 15/07/20 00:00:12 自动转化python的时间类型
    modify by bigzhu at 15/09/13 17:25:43 为了用订阅号给指定用户发消息，改用WechatExt
    '''
    wechat = WechatBasic(token=token, appid=appid, appsecret=appsecret)
    the_access_token = wechat.get_access_token()
    access_token = the_access_token['access_token']
    access_token_expires_at = the_access_token['access_token_expires_at']
    ticket_info = wechat.get_jsapi_ticket()
    jsapi_ticket = ticket_info['jsapi_ticket']
    jsapi_ticket_expires_at = ticket_info['jsapi_ticket_expires_at']

    access_token_expires_at = time_bz.timestampToDateTime(access_token_expires_at)
    jsapi_ticket_expires_at = time_bz.timestampToDateTime(jsapi_ticket_expires_at)

    return wechat, access_token, access_token_expires_at, jsapi_ticket, jsapi_ticket_expires_at


def getWechat():
    '''
    控制最新的wechat
    '''
    result = list(pg.select('wechat_dead_line'))
    if result:
        wechat_dead_line = result[0]
        now = datetime.datetime.now()
        if wechat_dead_line.access_token_expires_at is not None and now < wechat_dead_line.access_token_expires_at and now < wechat_dead_line.jsapi_ticket_expires_at:
            wechat = WechatBasic(jsapi_ticket=wechat_dead_line.jsapi_ticket,
                                 jsapi_ticket_expires_at=time_bz.datetimeToTimestamp(wechat_dead_line.jsapi_ticket_expires_at),
                                 access_token=wechat_dead_line.access_token,
                                 access_token_expires_at=time_bz.datetimeToTimestamp(wechat_dead_line.access_token_expires_at),
                                 token=token,
                                 appid=appid,
                                 appsecret=appsecret)
        else:
            wechat, access_token, access_token_expires_at, jsapi_ticket, jsapi_ticket_expires_at = getNewWechatInfo()
            pg.update('wechat_dead_line', where='1=1', access_token=access_token, access_token_expires_at=access_token_expires_at, jsapi_ticket=jsapi_ticket, jsapi_ticket_expires_at=jsapi_ticket_expires_at)
    else:
        wechat, access_token, access_token_expires_at, jsapi_ticket, jsapi_ticket_expires_at = getNewWechatInfo()

        pg.insert('wechat_dead_line', access_token=access_token, access_token_expires_at=access_token_expires_at, jsapi_ticket=jsapi_ticket, jsapi_ticket_expires_at=jsapi_ticket_expires_at)
    return wechat


def getNewWechatExtInfo():
    '''
    modify by bigzhu at 15/09/13 17:25:43 为了用订阅号给指定用户发消息，改用WechatExt
    '''
    wechat_ext = WechatExt(user_name, password,
                           appid=appid
                           )
    token_cookies = wechat_ext.get_token_cookies()
    pg.insertOrUpdate(pg, 'wechat_dead_line', token_cookies, where='1=1')
    return wechat_ext


def getWechatExt():
    '''
    判断wechat ext是否过期
    '''
    result = list(pg.select('wechat_dead_line'))
    if result:
        wechat_dead_line = result[0]
        wechat_ext = WechatExt(user_name, password,
                               appid=appid,
                               token=wechat_dead_line.token,
                               cookies=wechat_dead_line.cookies
                           )
    else:
        wechat_ext = getNewWechatExtInfo()
    return wechat_ext


def getQrUrl(wechat, user_name):
    '''
    create by bigzhu at 15/07/19 00:43:47 生成带用户名的二维码
    '''
    parm = {"action_name": "QR_LIMIT_STR_SCENE", "action_info": {"scene": {"scene_str": user_name}}}

    ticket = wechat.create_qrcode(parm)['ticket']
    url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" + ticket
    return url


def initSetting(settings):
    with open('wechat.ini', 'r') as cfg_file:
        config.readfp(cfg_file)
        settings["domain"] = config.get('app', 'domain')
        settings["appid"] = config.get('app', 'appid')
        settings["appsecret"] = config.get('app', 'appsecret')
        settings["token"] = config.get('app', 'token')

    settings["noncestr"] = public_bz.getProjectName()
    settings["subscribe"] = '/intro'
    settings["suburl"] = 'bird'  # 用来做用户回调的关键字,需要实现同名的set open_id 方法

    settings, wechat = wechat_bz.initWechat(settings)
    return settings, wechat


def saveUserInfo(wechat, openid):
    '''
    create by bigzhu at 15/07/19 01:47:09 顺便绑定用户
    '''
    # 检查用户是否存储了,没有的话存之
    wechat_user_info = public_db.getWechatUserByOpenid(openid)
    if wechat_user_info:
        pass
    else:
        wechat_user_info = wechat.get_user_info(openid)
        pg.insert('wechat_user', **wechat_user_info)


def bindUser(user_name, openid):
    count = pg.update('wechat_user', where="openid='%s'" % openid, user_name=user_name)
    if count != 1:
        raise Exception('绑定失败: count=%s, openid=%s' % (count, openid))


def sendTwitter(openid, tweet, screen_name, id):
    '''
    发送twitter的消息
    '''

    articles = []
    if hasattr(tweet, 'extended_entities') and tweet.extended_entities['media']:
        for media in tweet.extended_entities['media']:
            article = storage()
            article.picurl = "http://follow.center/ProxyHandler/%s" % media['media_url_https']
            article.url = "http://follow.center/message?t=twitter&id=%s" % id
            articles.append(article)
        if len(articles) == 1:
            articles[0].title = screen_name
        else:
            articles[0].title = screen_name + ': ' + tweet.text
        articles[0].description = tweet.text
    else:
        article = storage()
        article.title = screen_name
        article.url = "http://follow.center/message?t=twitter&id=%s" % id
        article.description = tweet.text
        articles = [article]
    sendArticle(openid, articles)


def sendGithub(openid, text, user_name, id):
    '''
    create by bigzhu at 15/07/22 15:05:01 发送github的消息
    '''
    articles = []
    article = storage()
    article.title = user_name
    article.url = "http://follow.center/message?t=github&id=%s" % id
    article.description = text
    articles = [article]
    sendArticle(openid, articles)


def sendInstagram(openid, text, img_url, user_name, id):
    '''
    create by bigzhu at 15/08/01 00:35:08
    modify by bigzhu at 15/08/01 00:57:28 不用代理,没被屏蔽
    '''
    article = storage()
    article.title = user_name
    article.picurl = 'http://follow.center/sp/' + oper.encodeUrl(img_url)
    article.url = "http://follow.center/message?t=instagram&id=%s" % id
    article.description = text
    articles = [article]
    sendArticle(openid, articles)
if __name__ == '__main__':
    # sendInstagram('oV9tmuDpkxJqabSWWHzrimVZeb0Q', 'test',
     #             'https://pbs.twimg.com/media/CL4f9axUYAApa9h.jpg',
     #             'test', 1)
    print getWechatExt()
