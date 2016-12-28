#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
create by bigzhu at 15/07/15 17:17:29 取github的动态
'''
import sys
sys.path.append("../lib_p_bz")

import requests
import sys
import pg
import oper
from oper import sync
import json
import time_bz
import time
import public_bz
import public_db
M_TYPE = 'tumblr'
API_KEY = 'w0qnSK6sUtFyapPHzZG7PjbTXbsYDoilrnmrblIbA56GTl0ULL'


def tumblrRealAvatar(url):
    '''
    create by bigzhu at 16/05/28 11:06:23 tumblr 用了 301 来转 avatar url,要再调一次
    '''
    r = requests.get(url)
    return r.url


def saveUser(user):
    social_user = public_bz.storage()
    social_user.type = 'tumblr'
    social_user.name = user['name']
    social_user.count = user.get('likes', -1)  # 有人会不分享likes数
    avatar_url = 'https://api.tumblr.com/v2/blog/%s.tumblr.com/avatar/512' % user['name']
    social_user.avatar = tumblrRealAvatar(avatar_url)
    social_user.description = user['description']
    social_user.sync_key = user['updated']

    pg.insertOrUpdate(pg, 'social_user', social_user, "lower(name)=lower('%s') and type='tumblr' " % social_user.name)
    return social_user


def saveMessage(tumblr_user, user, blog):
    m = public_bz.storage()
    m.god_id = user.id
    m.user_name = user.name
    m.name = tumblr_user['name']
    # m.avatar = tumblr_user['avatar']
    # m.avatar = avatar

    m.id_str = blog['id']
    m.m_type = 'tumblr'
    m.created_at = time_bz.timestampToDateTime(blog['timestamp'])
    type = blog.get('type')
    m.href = blog.get('short_url')
    m.type = type
    if type == 'text':
        m.title = blog.get('title')
        m.text = blog.get('body')
    if type == 'photo':
        m.text = blog.get('caption')
        m.extended_entities = json.dumps(blog.get('photos'))
    m.content = None

    id = pg.insertIfNotExist(pg, 'message', m, "id_str='%s' and m_type='tumblr' " % m.id_str)
    if id is None:
        pass
    else:
        print '%s new tumblr message %s' % (m.name, m.id_str)


def callGetMeidaApi(user_name, offset=0, limit=20):
    params = {'api_key': API_KEY,
              'offset': offset,
              'limit': limit,
              }
    url = '''http://api.tumblr.com/v2/blog/%s.tumblr.com/posts''' % user_name
    r = requests.get(url, params=params)
    if r.status_code == 200:
        try:
            medias = r.json()
            return medias
        except Exception:
            print 'r=', r
            print public_bz.getExpInfoAll()
            return
    elif r.status_code == 429:
        raise Exception('达到最大访问次数')
    else:
        print r.status_code


# def waitReset(user):
#     while True:
#         remaining = getRemaining()
#         print 'remaining:', remaining
#         if remaining == 0:
#             time.sleep(600)
#         else:
#             main(user, wait=True)
#             break


def main(user, wait):
    blogs = callGetMeidaApi(user_name=user.tumblr, limit=1)
    if blogs is None:
        public_db.sendDelApply('tumblr', user.name, user.tumblr, 'not have user')
    else:
        response = blogs['response']
        tumblr_user = response['blog']
        if oper.haveNew('tumblr', tumblr_user['name'], tumblr_user['updated']):
            # 只取最新的20条来保存
            blogs = callGetMeidaApi(user_name=user.tumblr, limit=20)['response']['posts']
            for message in blogs:
                saveMessage(tumblr_user, user, message)
        saveUser(tumblr_user)
        oper.noMessageTooLong(M_TYPE, user.tumblr)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_name = (sys.argv[1])
        sync('tumblr', main, user_name)
        exit(0)
    while True:
        try:
            sync('tumblr', main, must_followed=True)
        except requests.exceptions.ConnectionError:
            print public_bz.getExpInfoAll()
        except requests.exceptions.ChunkedEncodingError as e:
            print e
        except requests.exceptions.ReadTimeout as e:
            print e
        time.sleep(1200)
