#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
create by bigzhu at 15/07/15 17:17:29 取github的动态
'''
import sys
sys.path.append("../lib_p_bz")

import datetime
import requests
from oper import sync
import oper
import pg
import sys
from datetime import timedelta
import db_bz
from public_bz import storage
import public_db
import json
import time_bz
import time
import public_bz

import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/github.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    client_id = config.get('secret', 'client_id')
    client_secret = config.get('secret', 'client_secret')
params = {'client_id': client_id, 'client_secret': client_secret}


def main(user, wait):
    '''
    create by bigzhu at 15/07/15 17:54:08 取github
    modify by bigzhu at 15/07/22 16:20:42 时间同样要加入8小时,否则不正确
    '''
    etag = oper.getSyncKey('github', user.github)
    print 'check ', user.github
    headers = {'If-None-Match': etag}
    try:
        r = requests.get('https://api.github.com/users/%s/events' % user.github, headers=headers, params=params)
    except requests.exceptions.ConnectionError:
        print public_bz.getExpInfoAll()
        return
    if r.status_code == 200:
        messages = r.json()
        if not messages:
            # 没有这个github用户, 删除
            public_db.sendDelApply('github', user.name, user.github, 'not have user')
            return
        actor = messages[0]['actor']
        # actor不定是作者名字，有可能org才是
        if actor['login'].lower() == user.github.lower():
            the_user = actor
        else:
            org = messages[0]['org']
            if org['login'].lower() == user.github.lower():
                # the_user = org
                # 如果是org，那么url不同
                # the_user['url'] = "https://api.github.com/users/" + user.github

                # 对org用户不同步,当作没有github处理，否则杂乱信息太多
                public_db.sendDelApply('github', user.name, user.github, 'is org user')
                return
            else:
                raise "in this github can't find user_name=%s" % user.github

        user_request = requests.get(the_user['url'], params=params)
        if user_request.status_code == 200:
            github_user = storage(user_request.json())
        else:
            print 'get user info error', user_request.status_code
            return
        etag = r.headers['etag']
        limit = r.headers['X-RateLimit-Remaining']
        if limit == '0':
            return

        for message in r.json():
            message = storage(message)
            saveMessage(message, user)
        saveUser(github_user, etag)
        oper.noMessageTooLong('github', user.github)
    if r.status_code == 404:
        public_db.sendDelApply('github', user.name, user.github, '404')


def saveMessage(message, user):
    '''
    create by bigzhu at 15/07/16 09:44:39 为了抽取数据方便,合并数据到 content 里
    '''
    content = storage()
    content.type = message.type
    content.repo = message.repo
    content.payload = message.payload
    content = json.dumps(content)

    m = public_bz.storage()
    m.god_id = user.id
    m.user_name = user.name
    m.name = message.actor['login']
    # m.avatar = message.actor['avatar_url']

    m.id_str = message['id']
    m.m_type = 'github'
    m.created_at = time_bz.unicodeToDateTIme(message.created_at)
    m.created_at += timedelta(hours=8)
    m.content = content
    m.text = None
    m.href = None
    id = db_bz.insertIfNotExist(pg, 'message', m, "id_str='%s' and m_type='github'" % m.id_str)
    if id is not None:
        print '%s new message github %s' % (m.name, m.id_str)
    return id


def saveUser(user, sync_key):
    social_user = public_bz.storage()
    social_user.type = 'github'

    try:
        social_user.name = user.login
    except Exception as e:
        print e
        print user
    social_user.count = user.following
    social_user.avatar = user.avatar_url
    social_user.description = user.bio
    social_user.sync_key = sync_key

    pg.insertOrUpdate(pg, 'social_user', social_user, "lower(name)=lower('%s') and type='github' " % social_user.name)
    return social_user


if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_name = (sys.argv[1])
        sync('github', main, user_name)
        exit(0)
    while True:
        sync('github', main, must_followed=False)
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(1200)
