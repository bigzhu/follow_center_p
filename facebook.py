#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
'''
import sys
sys.path.append("../lib_p_bz")
import public_db

import datetime
import sys
import time
# from datetime import timedelta
import requests
requests.adapters.DEFAULT_RETRIES = 5
import pg
import json
import public_bz
import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/facebook.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    client_id = config.get('secret', 'client_id')
    client_secret = config.get('secret', 'client_secret')
    access_token = '%s|%s' % (client_id, client_secret)

TYPE = 'facebook'


def getFaceBookUserId(user_name):
    '''
    create by bigzhu at 16/06/10 14:07:01 facebook的所有操作都要以user-id来做
    '''
    params = {'access_token': access_token}
    url = "https://graph.facebook.com/%s" % user_name
    r = requests.get(url, params=params)
    r = r.json()
    return r.get('id')


def main(user):
    '''
    create by bigzhu at 16/06/10 14:01:16 facebook
    '''
    etag = None
    social_name = user['facebook']
    god_name = user['name']
    where = "type='facebook' and name='%s'" % social_name
    social_user = list(pg.db.select('social_user', where=where))
    if social_user:
        user_id = social_user[0].out_id
        etag = social_user[0].sync_key
    else:
        user_id = getFaceBookUserId(social_name)

    params = {'access_token': access_token,
              'fields': 'username,link,bio,picture,feed{created_time,full_picture,message,link,description}'}
    url = "https://graph.facebook.com/%s" % user_id

    headers = {'If-None-Match': etag}

    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        etag = r.headers['etag']
        r = r.json()
        r['user_id'] = user_id
        saveUser(r, etag)
        for message in r['feed']['data']:
            saveMessage(user, message)
    elif r.status_code == 304:
        pass
    elif r.status_code == 404:
        public_db.sendDelApply('facebook', god_name, social_name, '404')
    else:
        print r.status_code


def saveUser(user, etag):
    social_user = public_bz.storage()
    social_user.type = 'facebook'
    social_user.name = user['username']
    # facebook 取不到 friend count or followed count
    social_user.count = -1
    social_user.avatar = user['picture']['data']['url']
    social_user.description = user.get('bio')  # bio 可能没有
    social_user.sync_key = etag
    social_user.out_id = user['id']

    pg.insertOrUpdate(pg, 'social_user', social_user, "lower(name)=lower('%s') and type='facebook' " % social_user.name)
    return social_user


def saveMessage(user, message):
    '''
    '''
    message = public_bz.storage(message)
    m = public_bz.storage()
    m.god_id = user['id']
    m.user_name = user['name']
    m.name = user['facebook']

    m.m_type = 'facebook'
    m.id_str = message.id
    m.created_at = message.created_time
    m.content = json.dumps({'description': message.get('description')})
    m.text = message.get('message')
    m.extended_entities = json.dumps({'pictrue': message.get('full_picture')})
    # m.type =
    m.href = message.get('link')
    id = pg.insertIfNotExist(pg, 'message', m, "id_str='%s' and m_type='facebook'" % m.id_str)
    if id is not None:
        print '%s new facebook message %s' % (m.name, m.id_str)
    return id


def run(god_name=None):
    '''
    create by bigzhu at 16/05/30 13:26:38 取出所有的gods，同步
    '''
    sql = '''
    select * from god where facebook is not null and facebook != ''
    '''
    if god_name:
        sql += " and name='%s'" % god_name
    users = pg.query(sql)
    for user in users:
        main(user)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_name = (sys.argv[1])
        run(user_name)
        exit(0)
    while True:
        try:
            run()
        except Exception, e:
            print e
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(1200)
