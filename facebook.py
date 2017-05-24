#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
'''
import sys
sys.path.append("../lib_p_bz")

import datetime
import sys
import time
# from datetime import timedelta
import requests
import god_oper
requests.adapters.DEFAULT_RETRIES = 5
from db_bz import pg
import json
import public_bz
import social_sync
import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/facebook.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    client_id = config.get('secret', 'client_id')
    client_secret = config.get('secret', 'client_secret')
    access_token = '%s|%s' % (client_id, client_secret)

TYPE = 'facebook'


def getFaceBookUserId(facebook_name):
    '''
    create by bigzhu at 16/06/10 14:07:01 facebook的所有操作都要以user-id来做
    '''
    params = {'access_token': access_token}
    url = "https://graph.facebook.com/%s" % facebook_name
    r = requests.get(url, params=params)
    r = r.json()
    return r.get('id')


def getFacebookUser(facebook_name, god_name):
    '''
    只是给添加时候用
    '''

    user_id = getFaceBookUserId(facebook_name)
    params = {'access_token': access_token,
              'fields': 'username,link,bio,picture'}
    url = "https://graph.facebook.com/%s" % user_id
    r = requests.get(url, params=params)
    if r.status_code == 200:
        r = r.json()
        r['user_id'] = user_id
        saveUser(god_name, facebook_name, r, None)
    elif r.status_code == 404:
        # public_db.sendDelApply('facebook', god_name, facebook_name, '404')
        god_oper.delNoName('facebook', god_name)

    else:
        print r.status_code


def main(god):
    '''
    create by bigzhu at 16/06/10 14:01:16 facebook
    '''
    god_name = god['name']
    facebook_name = god['facebook']['name']
    god_id = god.id

    etag = god['facebook'].get('sync_key')
    user_id = god['facebook'].get('out_id')

    if etag:
        pass
    else:
        user_id = getFaceBookUserId(facebook_name)

    params = {'access_token': access_token,
              'fields': 'username,link,bio,picture,feed{created_time,full_picture,message,link,description,type,source}'}
    url = "https://graph.facebook.com/%s" % user_id

    headers = {'If-None-Match': etag}

    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        etag = r.headers['etag']
        r = r.json()
        r['user_id'] = user_id
        saveUser(god_name, facebook_name, r, etag)
        for message in r['feed']['data']:
            saveMessage(god_name, facebook_name, god_id, message)
    elif r.status_code == 304:
        pass
    elif r.status_code == 404:
        # public_db.sendDelApply('facebook', god_name, facebook_name, '404')
        god_oper.delNoName('facebook', god_name)
    else:
        print r.status_code


def saveUser(god_name, facebook_name, user, etag):
    social_user = public_bz.storage()
    social_user.type = 'facebook'
    # social_user.name = user['username']
    social_user.name = facebook_name
    # facebook 取不到 friend count or followed count
    social_user.count = -1
    social_user.avatar = user['picture']['data']['url']
    social_user.description = user.get('bio')  # bio 可能没有
    if etag is not None:
        social_user.sync_key = etag
    social_user.out_id = user['id']

    pg.update('god', where={'name': god_name}, facebook=json.dumps(social_user))
    return social_user


def saveMessage(god_name, facebook_name, god_id, message):
    '''
    '''
    message = public_bz.storage(message)
    m = public_bz.storage()
    m.god_id = god_id
    m.god_name = god_name
    m.name = facebook_name

    m.m_type = 'facebook'
    m.id_str = message.id
    m.created_at = message.created_time
    m.content = json.dumps({'description': message.get('description')})
    m.text = message.get('message')
    m.extended_entities = json.dumps({'pictrue': message.get('full_picture'), 'source': message.get('source')})
    m.type = message.get('type')
    m.href = message.get('link')
    id = pg.insertIfNotExist(pg, 'message', m, "id_str='%s' and m_type='facebook'" % m.id_str)
    if id is not None:
        print '%s new facebook message %s' % (m.name, m.id_str)
    return id


def loop(god_name=None):
    '''
    create by bigzhu at 16/05/30 13:26:38 取出所有的gods，同步
    '''
    gods = social_sync.getSocialGods('facebook', god_name)
    for god in gods:

        main(god)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        god_name = (sys.argv[1])
        loop(god_name)
        exit(0)
    while True:
        loop()
        # try:
        #     loop()
        # except Exception as e:
        #     print e
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(1200)
