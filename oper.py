#!/usr/bin/env python
# -*- coding: utf-8 -*-
import db_bz
import pg
import public_db
import base64
import datetime
import time_bz


def black(user_id, god_id, god_name, make_sure=True):
    '''
    黑化某人
    '''
    id = db_bz.insertIfNotExist(pg, 'black', {'user_id': user_id, 'god_id': god_id, 'god_name': god_name}, "god_name=%s and god_id=%s" % (god_name, god_id))
    if id is None and make_sure:
        raise Exception('没有正确的black, 似乎已经black过了呢')


def block(user_id, god_id, make_sure=True):
    '''
    屏蔽某人
    '''
    id = db_bz.insertIfNotExist(pg, 'block', {'user_id': user_id, 'god_id': god_id}, "user_id=%s and god_id=%s" % (user_id, god_id))
    if id is None and make_sure:
        raise Exception('没有正确的Block, 似乎已经Block过了呢')


def checkSocialData(data, type):
    name = data.get(type)
    god_name = data.get('name')
    if name:
        god_info = checkSocialExists(type, name, god_name)
        if god_info:
            raise Exception('系统已有同名的%s帐号:%s，位于用户%s下' % (type, name, god_info[0].name))


def cleanSocialData(data, type):
    '''
    create by bigzhu at 16/04/26 10:43:04 用于add god 时，存在就清除对应的 data.name, 避免出现加了别人的social
    '''
    name = data.get(type)
    god_name = data.get('name')
    if name:
        user_info = checkSocialExists(type, name, god_name)
        if user_info:
            del data[type]


def checkSocialExists(type, name, user_name):
    sql = '''
        select * from god where %s='%s' and name != '%s'
    ''' % (type, name, user_name)
    god = list(pg.query(sql))
    return god


def noMessageTooLong(m_type, name):
    sql = '''
    select * from message where m_type='%s' and name='%s' order by created_at desc limit 1
    ''' % (m_type, name)
    # last_message = public_db.getNewMessages(god_name=name, m_type=m_type, limit=1)
    last_message = pg.db.query(sql)
    if last_message:
        last_message_time = last_message[0].created_at
        if (datetime.datetime.now() - last_message_time).days >= 180:
            print 'no message too long'
            public_db.delNoName(m_type, name)


def getSyncKey(type, name):
    '''
    create by bigzhu at 16/04/05 10:32:02 取出key来取最新数据
    '''
    where = "name='%s' and type ='%s'" % (name, type)
    result = list(pg.select('social_user', where=where))
    if result:
        return result[0].sync_key


def haveNew(type, name, sync_key):
    '''
    查看social_user, 判断是否新

    '''
    where = "name='%s' and type ='%s'" % (name, type)
    result = list(pg.select('social_user', where=where))
    if result:
        if result[0].sync_key == str(sync_key):
            # print ' no new data'
            return False
        else:
            print 'old:', result[0].sync_key
            print 'new:', sync_key
    return True


def sync(type, main, god_name=None, wait=None, must_followed=None):
    '''
    create by bigzhu at 16/03/26 18:58:06 同步的公用
    create by bigzhu at 16/05/01 09:04:36 只查有人关注的出来
    modify by bigzhu at 16/05/27 10:58:00 所有都查，因为要先查了再follow
    modify by bigzhu at 16/05/27 10:59:24 改为查 god 表
    modify by bigzhu at 16/05/27 14:13:11 有的时候不用wait remain
    modify by bigzhu at 16/05/30 14:33:59 要有人关注的再sync
    modify by bigzhu at 16/05/30 17:12:36 加入参数
    '''
    where = '''
        %s is not null and %s!=''

    ''' % (type, type)
    if must_followed:
        where += " and id in (select god_id from follow_who) "
    if god_name:
        where += " and name='%s'" % god_name
    users = pg.select('god', what='*', where=where)
    for user in users:
        # print 'checking %s %s' % (type, user[type])
        main(user, wait)


def getGodSocialInfo(god):
    '''
    create by bigzhu at 15/11/27 10:37:14 取社交信息
    modify by bigzhu at 16/04/07 11:41:45 改为从 social_user查
    modify by bigzhu at 16/06/11 22:35:41 add facebook
    '''
    god.twitter_user = public_db.getSocialUser(god.twitter, 'twitter')
    god.github_user = public_db.getSocialUser(god.github, 'github')
    god.instagram_user = public_db.getSocialUser(god.instagram, 'instagram')
    god.tumblr_user = public_db.getSocialUser(god.tumblr, 'tumblr')
    god.facebook_user = public_db.getSocialUser(god.facebook, 'facebook')
    return god


def isHaveGoodSocial(god):
    count = 0
    if god.twitter_user:
        count += god.twitter_user.count
    if god.github_user:
        count += god.github_user.count
    if god.instagram_user:
        count += god.instagram_user.count
    if god.tumblr_user:
        count += god.tumblr_user.count
    if count > 3000:
        return True
    else:
        return False


def getGods(user_id=None, recommand=False, is_my=None, cat=None, is_public=None, limit=None, before=None):
    '''
    create by bigzhu at 15/07/12 23:43:54 显示所有的大神, 关联twitter
    modify by bigzhu at 15/07/17 15:20:26 关联其他的,包括 github
    modify by bigzhu at 15/08/28 17:05:54 可以查出没关注的,和随机的
    modify by bigzhu at 16/01/27 17:15:15 过滤出满足条件的
    modify by bigzhu at 16/04/11 11:47:54 查看我的关注时候，不要限定关注数
    modify by bigzhu at 16/05/27 21:52:06 让所有god都能看到
    '''
    gods = list(public_db.getGodInfoFollow(user_id=user_id, recommand=recommand, is_my=is_my, cat=cat, is_public=is_public, limit=limit, before=before))
    # have_social_gods = []
    for god in gods:
        god = getGodSocialInfo(god)
    return gods


def getGodInfo(god_name, user_id=None, is_public=None):
    '''
    create by bigzhu at 15/11/27 10:31:48 查某个god
    '''

    gods = list(public_db.getGodInfoFollow(user_id, god_name=god_name, is_public=is_public))
    if gods:
        god = gods[0]
    else:
        raise Exception('god not exists')
    god = getGodSocialInfo(god)
    return god


def saveLast(last_time, user_id):
    '''
    create by bigzhu at 15/08/16 16:22:39 保存最后一条的message
    '''
    id = db_bz.insertIfNotExist(pg, 'last', {'user_id': user_id, 'last_time': last_time}, "user_id=%s" % user_id)
    if id is None:
        count = pg.update('last', where="last_time< '%s'  and user_id=%s" % (last_time, user_id), last_time=last_time)
        return count
    return 1


def getLast(user_id):
    '''
    create by bigzhu at 16/02/22 23:34:00 查出上一次的id，并决定 limit 和info
    modify by bigzhu at 16/04/19 10:02:40 不要干多余的事
    '''
    if user_id is None:
        return None
    last = public_db.getLast(user_id)
    last = list(pg.select('last', where="user_id=%s" % user_id))
    if last:
        return last[0]


def getLastTime(user_id):
    last = getLast(user_id)
    if last:
        return last.last_time
    else:  # 未登录 or 第一次进来
        return time_bz.getBeforeDay()


def getUnreadCount(user_id):
    after = getLastTime(user_id)
    print after
    return public_db.queryUnreadCount(after, user_id)


def collect(message_id, user_id):
    '''
    create by bigzhu at 16/05/20 14:21:02 加入收藏
    '''
    id = db_bz.insertIfNotExist(pg, 'collect', {'user_id': user_id, 'message_id': message_id}, "user_id=%s and message_id=%s" % (user_id, message_id))
    return id


def follow(user_id, god_id, make_sure=True):
    '''
    create by bigzhu at 15/07/15 14:22:51
    modify by bigzhu at 15/07/15 15:00:28 如果不用告警,就不要make_sure
    '''
    id = db_bz.insertIfNotExist(pg, 'follow_who', {'user_id': user_id, 'god_id': god_id}, "user_id=%s and god_id=%s" % (user_id, god_id))
    if id is None and make_sure:
        raise Exception('没有正确的Follow, 似乎已经Follow过了呢')


def getMessages(limit=None, current_user=None, god_name=None, offset=None, last_message_id=None):
    '''
    create by bigzhu at 15/08/03 13:24:39 分页方式取messages
    '''
    anchor = ''
    if limit is None:
        limit = 20
        more = 40
    messages = list(public_db.getMessages(current_user, limit=limit, god_name=god_name, offset=offset, last_message_id=last_message_id))
    if messages:
        anchor_message = messages[-1]
        anchor = '%s_%s' % (anchor_message.m_type, anchor_message.id)
        more = int(limit) + 20
    return messages, more, anchor


def encodeUrl(url):
    '''
    create by bigzhu at 15/08/07 10:37:21 加密url
    modify by bigzhu at 15/08/08 19:47:32 加密时会带上换行,要去了, 否则微信会打不开
    '''
    return base64.encodestring(base64.encodestring(url).replace('\n', '')).replace('\n', '')


def decodeUrl(url):
    return base64.decodestring(base64.decodestring(url))

if __name__ == '__main__':
    print getMessages(limit=1, god_name='bigzhu')
    pass
