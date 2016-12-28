#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
create by bigzhu at 15/07/04 22:25:30 取twitter的最新信息
modify by bigzhu at 15/07/17 16:49:58 添加pytz来修正crated_at的时区
modify by bigzhu at 15/07/17 17:08:38 存进去还是不对,手工来来修正吧
modify by bigzhu at 15/11/28 11:36:18 可以查某个用户
'''
import sys
sys.path.append("../lib_p_bz")

import sys
import oper
import time
from datetime import timedelta
import tweepy
import public_db
import pg
import json
import public_bz
import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/twitter.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    consumer_key = config.get('secret', 'consumer_key')
    consumer_secret = config.get('secret', 'consumer_secret')
    access_token = config.get('secret', 'access_token')
    access_token_secret = config.get('secret', 'access_token_secret')


def main(user, wait):
    '''
    create by bigzhu at 15/07/04 22:49:04
        用 https://api.twitter.com/1.1/statuses/user_timeline.json 可以取到某个用户的信息
        参看 https://dev.twitter.com/rest/reference/get/statuses/user_timeline
    modify by bigzhu at 15/07/04 22:53:09
        考虑使用 http://www.tweepy.org/ 来调用twitter api
    modify by bigzhu at 15/08/02 21:35:46 避免批量微信通知
    create by bigzhu at 16/04/30 09:56:02 不再取转发的消息
    '''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    try:
        twitter_user = api.get_user(screen_name=user.twitter)
        if twitter_user:
            twitter_user = saveUser(twitter_user)
        else:
            public_db.sendDelApply('twitter', user.name, user.twitter, 'User not found.')
            return
        public_tweets = api.user_timeline(screen_name=user.twitter, include_rts=False, exclude_replies=True)
        for tweet in public_tweets:
            tweet.created_at += timedelta(hours=8)
            saveMessage(twitter_user, user, tweet)
        oper.noMessageTooLong('twitter', user.twitter)
    except tweepy.error.TweepError:
        print 'screen_name=', user.twitter
        error_info = public_bz.getExpInfo()
        print error_info

        if 'User not found.' in error_info:
            public_db.sendDelApply('twitter', user.twitter, 'User not found.')
        if 'Rate limit exceeded' in error_info:  # 调用太多
            if wait:
                waitReset(user)
            else:
                raise Exception('Twitter api 的调用次数用完了，请等个10分钟再添加!')
            return 'Rate limit exceeded'
        if 'User has been suspended.' in error_info:  # 帐号被冻结了
            public_db.sendDelApply('twitter', user.twitter, 'User has been suspended.')
        if 'Not authorized.' in error_info:  # 私有
            public_db.sendDelApply('twitter', user.twitter, 'Not authorized.')
        if 'Sorry, that page does not exist.' in error_info:  # 没用户
            public_db.sendDelApply('twitter', user.twitter, 'Sorry, that page does not exist.')


def saveUser(twitter_user):
    social_user = public_bz.storage()
    social_user.type = 'twitter'
    social_user.name = twitter_user.screen_name
    social_user.count = twitter_user.followers_count
    social_user.avatar = twitter_user.profile_image_url_https.replace('_normal', '')
    social_user.description = twitter_user.description
    # 没有找到
    # social_user.sync_key = twitter_user.description

    pg.insertOrUpdate(pg, 'social_user', social_user, "lower(name)=lower('%s') and type='twitter' " % social_user.name)
    return social_user


def saveMessage(twitter_user, user, tweet):
    '''
    create by bigzhu at 15/07/10 14:39:48
        保存twitter
    create by bigzhu at 16/03/26 06:05:12 重构，改很多
    modify by bigzhu at 16/03/26 20:33:59 重构
        twitter_user 社交帐号信息
        user 本系统用户信息
        tweet 消息本身
    '''
    # if hasattr(tweet, 'author'): # 自增长用户，啧啧，会不停增加的吧
    #    saveUser(tweet.author)
    #    user_bz.insertOrUpdateUserByType(pg, 'twitter', tweet.author.screen_name)

    m = public_bz.storage()
    m.god_id = user.id
    m.user_name = user.name
    m.name = twitter_user.name
    # m.avatar = twitter_user.avatar.replace('_normal', '')

    m.id_str = tweet.id_str
    m.m_type = 'twitter'
    m.created_at = tweet.created_at
    m.content = None
    m.text = tweet.text
    if hasattr(tweet, 'extended_entities'):
        m.extended_entities = json.dumps(tweet.extended_entities)
        m.type = tweet.extended_entities['media'][0]['type']
    m.href = 'https://twitter.com/' + m.name + '/status/' + m.id_str
    id = pg.insertIfNotExist(pg, 'message', m, "id_str='%s' and m_type='twitter'" % tweet.id_str)
    if id is not None:
        print '%s new twitter message %s' % (m.name, m.id_str)
    return id


def getRemaining():
    '''
    create by bigzhu at 16/04/30 10:31:58 取重置时间和剩余调用次数
    '''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    rs = api.rate_limit_status()
    con = rs['resources']
    # reset = con['statuses']['/statuses/user_timeline']['reset']
    remaining = con['statuses']['/statuses/user_timeline']['remaining']
    return remaining


def waitReset(user):
    while True:
        try:
            remaining = getRemaining()
        except tweepy.error.TweepError:
            error_info = public_bz.getExpInfo()
            print error_info
            time.sleep(1200)
            continue
        print 'remaining:', remaining
        if remaining == 0:
            time.sleep(1200)
        else:
            main(user, wait=True)
            break


def run(god_name=None, wait=None):
    '''
    create by bigzhu at 16/05/30 13:26:38 取出所有的gods，同步
    '''
    sql = '''
    select * from god where twitter is not null and twitter != ''
    and id in (select god_id from follow_who)
    '''
    if god_name:
        sql += " and name='%s'" % god_name
    users = pg.query(sql)
    for user in users:
        # print 'checking %s %s' % (type, user[type])
        main(user, wait)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_name = (sys.argv[1])
        run(user_name)
        exit(0)

    while True:
        run(wait=True)
        time.sleep(2400)
