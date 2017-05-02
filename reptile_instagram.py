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
import public_db
import sys
import datetime
import time_bz
import requests
import filter_bz
requests.adapters.DEFAULT_RETRIES = 5
import time
from public_bz import storage
import pg
import json
import public_bz
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

from socket import error as SocketError
import errno

M_TYPE = 'instagram'


def getVideoUrl(url):
    '''
    从 video 类型的网址中得到真实的 mp4 url 地址
    '''
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        videos = soup.find_all('meta', property='og:video')
        if (videos):
            return videos[0]['content']
    else:
        raise Exception('getVideoUrl 异常: %s' % r.status_code)


def main(ins_name, user_name, god_id):
    '''
    create by bigzhu at 16/06/12 16:19:09 api disabled
    '''

    etag = None

    where = "type='instagram' and name='%s'" % ins_name
    social_user = list(pg.db.select('social_user', where=where))
    if social_user:
        etag = social_user[0].sync_key
    headers = {'If-None-Match': etag}
    url = "https://www.instagram.com/%s" % ins_name

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
                        saveMessage(ins_name, user_name, god_id, message)
    elif r.status_code == 304:
        pass
    elif r.status_code == 404:
        public_db.sendDelApply('instagram', user_name, ins_name, '404')
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


def saveMessage(ins_name, user_name, god_id, message):
    '''
    create by bigzhu at 16/04/06 19:46:10
    '''
    message = storage(message)

    m = public_bz.storage()
    m.god_id = god_id
    m.user_name = user_name.lower()
    m.name = ins_name
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
        video_url = getVideoUrl(m.href)
        m.extended_entities = json.dumps({'url': message.display_src, 'video_url': video_url})
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
    sql = filter_bz.filterNotBlackGod(sql)
    users = pg.query(sql)
    for user in users:
        ins_name = user['instagram']
        user_name = user['name']
        main(ins_name, user_name, user.id)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        user_name = (sys.argv[1])
        run(user_name)
        exit(0)
    while True:
        try:
            run()
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            print e
        except ConnectionError as e:
            print e
        except ValueError as e:
            print e
        except requests.exceptions.ChunkedEncodingError as e:
            print e
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time.sleep(1200)
