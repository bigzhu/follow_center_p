#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
create by bigzhu at 15/07/04 22:25:30 取twitter的最新信息
modify by bigzhu at 15/07/17 16:49:58 添加pytz来修正crated_at的时区
modify by bigzhu at 15/07/17 17:08:38 存进去还是不对,手工来来修正吧
modify by bigzhu at 15/11/28 11:36:18 可以查某个用户
'''
import public
public.setLib()
import public_db
import sys
import time_bz
import requests
requests.adapters.DEFAULT_RETRIES = 5
import time
from public_bz import storage
import pg
import json
import public_bz
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup


M_TYPE = 'instagram'


def main(user):
    '''
    create by bigzhu at 16/06/12 16:19:09 api disabled
    '''
    name = user['instagram']
    etag = None

    where = "type='instagram' and name='%s'" % name
    social_user = list(pg.db.select('social_user', where=where))
    if social_user:
        etag = social_user[0].sync_key
    headers = {'If-None-Match': etag}
    url = "https://www.instagram.com/%s" % name

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        etag = r.headers.get('etag')
        soup = BeautifulSoup(r.text)
        scripts = soup.find_all("script", type="text/javascript")
        for script in scripts:
            if '_sharedData' in str(script):
                content = script.contents[0]
                content = content.replace('window._sharedData =', '')
                content = content.replace(';', '')
                content = json.loads(content)
                user_info = content['entry_data']['ProfilePage'][0]['user']

                saveUser(user_info, etag)
                if user_info['media'].get('nodes'):
                    for message in user_info['media']['nodes']:
                        saveMessage(user, message)
    elif r.status_code == 304:
        pass
    elif r.status_code == 404:
        # public_db.delNoName('instagram', name)
        public_db.sendDelApply('instagram', name, '404')
    else:
        print r.status_code
    # oper.noMessageTooLong(M_TYPE, user.instagram)


def saveUser(user, sync_key):
    social_user = public_bz.storage()
    social_user.type = 'instagram'
    social_user.name = user['username']
    social_user.count = user['followed_by']['count']
    social_user.avatar = user['profile_pic_url']
    social_user.description = user['biography']
    social_user.sync_key = sync_key
    pg.insertOrUpdate(pg, 'social_user', social_user, "lower(name)=lower('%s') and type='instagram' " % social_user.name)
    return social_user


def saveMessage(user, message):
    '''
    create by bigzhu at 16/04/06 19:46:10
    '''
    message = storage(message)

    m = public_bz.storage()
    m.god_id = user.id
    m.user_name = user.name
    m.name = user.instagram
    # m.avatar = message.user['profile_picture']
    m.m_type = 'instagram'

    m.id_str = message.id
    m.created_at = time_bz.timestampToDateTime(message.date)
    # m.content = json.dumps(message.comments, cls=public_bz.ExtEncoder)
    if message.get('caption'):
        m.text = message.caption
    else:
        m.text = None
    m.extended_entities = json.dumps({'url': message.display_src})
    m.href = 'https://www.instagram.com/p/%s/' % message.code
    if message.is_video:
        m.type = 'video'
    else:
        m.type = 'image'
    id = pg.insertIfNotExist(pg, 'message', m, "id_str='%s' and m_type='instagram'" % m.id_str)
    if id is not None:
        print '%s new instagram message %s' % (m.user_name, m.id_str)
    # 肯定会有一条重复
    # else:
    #    print '%s 重复记录 %s' % (m.user_name, m.id_str)
    return id


def run(god_name=None):
    '''
    '''
    sql = '''
    select * from god where instagram is not null and instagram != ''
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
        except ConnectionError as e:
            print e
        except ValueError as e:
            print e
        time.sleep(1200)
