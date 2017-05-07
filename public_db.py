#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pg
import user_bz
import db_bz
import filter_bz
import add_bz
from webpy_db import SQLLiteral
user_oper = user_bz.UserOper(pg)


def wrapCount(sql):
    sql = '''
    select count(s.id) from (%s) s
    ''' % sql
    return sql


def queryUnreadCount(after, user_id=None):
    '''
    create by bigzhu at 16/12/14 17:14:49 取未读数
    '''
    sql = ' select * from all_message s '
    sql = filter_bz.filterFollowedMessages(sql, user_id)
    sql = filter_bz.filterAfterMessages(sql, after)
    sql = wrapCount(sql)
    # print sql

    return pg.query(sql)[0].count


def getSocialUser(name, type):
    '''
    create by bigzhu at 16/04/07 11:38:48 代替那些冗余的
    '''
    result = list(pg.select('social_user', where="lower(name)=lower('%s') and type='%s' " % (name, type)))
    count = len(result)
    if count > 1:
        raise Exception('social_user name=%s count=%s type=%s' % (name, count, type))
    if count == 1:
        return result[0]


def getLast(user_id):
    if user_id is None:
        return
    result = list(pg.select('last', where="user_id=%s" % user_id))
    if result:
        return result[0]


def delNoName(type, name):
    '''
    modify by bigzhu at 16/05/27 11:01:43 改为god
    '''
    sql = '''
    update god set %s=null where lower(%s)=lower('%s')
    ''' % (type, type, name)
    count = pg.query(sql)
    return count


def sendDelApply(type, god_name, social_name, reason=None):
    '''
    提交del申请，已有就+1
    '''
    data = {'type': type, 'god_name': god_name, 'social_name': social_name, 'reason': reason}
    table_name = 'apply_del'
    where = "lower(god_name)=lower('%s') and lower(social_name)=lower('%s') and type='%s'" % (god_name, social_name, type)
    id = db_bz.insertIfNotExist(pg, table_name, data, where)
    if id is None:
        pg.db.update(table_name, where=where, count=SQLLiteral('count+1'), stat=None)


def followedWho(user_id):
    sql = '''
        select god_id from follow_who where user_id=%s
    ''' % user_id
    return pg.query(sql)


def getWechatUserByOpenid(openid):
    '''
    create by bigzhu at 15/04/04 12:48:58 根据 openid 来查询微信用户
    '''
    return list(pg.select('wechat_user', where="openid='%s'" % openid))


def getMessage(id, user_id=None):
    '''
    create by bigzhu at 16/05/29 07:49:51 查看具体
    '''
    sql = '''
    select * from all_message m where id = %s
    ''' % id
    if user_id:
        sql = add_bz.messagesCollect(sql, user_id)
        sql = add_bz.messagesAnkiSave(sql, user_id)
    else:  # 不给看18+
        sql = '''
            select m.*, null as collect, null as collect_date
                from (%s) m
        ''' % sql
    return pg.query(sql)


def getCollectMessages(user_id):
    '''
    create by bigzhu at 16/05/29 07:30:11 just collect message
    '''
    sql = '''
    select * from all_message m
    '''
    sql = add_bz.messagesCollect(sql, user_id)
    sql = add_bz.messagesAnkiSave(sql, user_id)
    sql = '''
    select * from (%s) s
    where collect is not null
    ''' % sql
    # order by
    sql += ' order by collect_date desc '
    print sql
    return pg.query(sql)


def getNewMessages(user_id=None, after=None, limit=None, god_name=None, search_key=None, m_type=None):
    '''
    create by bigzhu at 16/05/28 22:01:58 查new的，根据mind图重构
    '''
    sql = '''
    select * from all_message m
    '''
    if user_id:
        sql = add_bz.messagesCollect(sql, user_id)
        sql = add_bz.messagesAnkiSave(sql, user_id)
    else:
        # 不给看18+
        sql = filter_bz.messageNot18(sql)
        # 只能看 public god 的 message
        sql = filter_bz.filterPublicGodMessages(sql)
    # 封住，以直接加where
    sql = ''' select * from (%s) s ''' % sql
    # 查比这个时间新的
    if after:
        sql += " where created_at > '%s' " % after
        # 再封
        sql = ''' select * from (%s) s ''' % sql
    # 互斥的filter_bz.filter
    if god_name:
        sql = filter_bz.messageThisGod(sql, god_name)
    elif search_key:
        # sql += " where upper(s.text) like '%%%s%%' or upper(s.content::text) like '%%%s%%' " % (search_key.upper(), search_key.upper())
        sql = filter_bz.filterSearchKey(sql, search_key)
    else:
        sql = filter_bz.filterFollowedMessages(sql, user_id)
    sql = filter_bz.messagesEffSocial(sql)

    if m_type:
        sql += " and s.m_type='%s' " % m_type
    # order by
    sql += ' order by created_at '
    # limit
    if limit is None and after is None:
        limit = 99
    sql += ' limit %s ' % limit
    print sql
    return pg.query(sql)


def getOldMessages(before, user_id=None, limit=None, god_name=None, search_key=None, m_type=None):
    '''
    create by bigzhu at 16/05/29 08:06:28 查老的
    '''
    sql = '''
    select * from all_message
    '''
    if user_id:
        sql = add_bz.messagesCollect(sql, user_id)
        sql = add_bz.messagesAnkiSave(sql, user_id)
    else:  # 不给看18+
        sql = filter_bz.messageNot18(sql)
    # 封住，以直接加where
    sql = ''' select * from (%s) s ''' % sql

    # 互斥的filter_bz.filter
    if god_name:
        sql = filter_bz.messageThisGod(sql, god_name)
    elif search_key:
        sql = filter_bz.filterSearchKey(sql, search_key)
    else:
        sql = filter_bz.filterFollowedMessages(sql, user_id)
    sql = filter_bz.filterMTYpe(sql, m_type)
    sql = filter_bz.filterBefore(sql, before)

    # order by
    if search_key is None:
        sql += ' order by created_at desc '
    # limit
    if limit is None:
        limit = 10
    sql += ' limit %s ' % limit
    print sql
    return pg.query(sql)


def getGodInfoFollow(user_id=None, god_name=None, recommand=False, is_my=None, cat=None, is_public=None, limit=None, before=None, blocked=None):
    '''
    modify by bigzhu at 15/08/06 17:05:22 可以根据god_name来取
    modify by bigzhu at 15/08/28 17:09:31 推荐模式就是只查随机5个
    modify by bigzhu at 15/08/28 17:30:38 没有社交帐号的不要查出来
    modify by bigzhu at 16/03/24 21:46:07 可以只查我关注的
    modify by bigzhu at 16/05/24 23:21:36 关联到god表,可以只查某种类别
    modify by bigzhu at 16/05/27 22:16:30 没人关注的也查出来
    modify by bigzhu at 16/06/21 12:15:24 add xmind, 整理了sql
    modify by bigzhu at 17/01/13 10:51:33 juest select blocked god
    '''
    sql = '''
    select  g.id as god_id,
            g.stat_date as u_stat_date,
    * from god g
    '''
    sql = filter_bz.filterHaveSocialGod(sql)
    sql = add_bz.addGodFollowedCount(sql)
    sql = add_bz.godAdminRemark(sql)

    # 只查有人关注的
    # sql = '''
    #     select * from (%s) s  where s.id in (select god_id from follow_who)
    # ''' % sql

    if user_id:
        # followed info
        sql = add_bz.godfollowed(sql, user_id)
        if (blocked):
            sql = filter_bz.godBlock(sql, user_id)
        else:
            sql = filter_bz.godNotBlock(sql, user_id)
        sql = add_bz.godUserRemark(sql, user_id)
        if recommand:
            sql = '''
            select * from (%s) s where s.followed=0 or s.followed is null
            ''' % sql
            if not cat:
                sql = filter_bz.messageNot18(sql)
        if is_my:
            sql = '''
            select * from (%s) s  where s.followed=1
            ''' % sql
    else:
        if recommand:
            sql = filter_bz.messageNot18(sql)

    if cat:
        sql = '''
        select * from (%s) s where lower(cat)=lower('%s')
        ''' % (sql, cat)
    if god_name:
        sql = '''
        select * from (%s) s where lower(name)=lower('%s')
        ''' % (sql, god_name)
    if is_public:
        sql = filter_bz.filterPublicGod(sql)
    if before:
        sql = '''
        select * from (%s) s where created_date < '%s'
        ''' % (sql, before)
    sql += "  order by created_date desc "
    if limit:
        sql += ' limit %s ' % limit
    # print sql
    return pg.query(sql)


def getUserInfoByName(user_name):
    user_info = user_oper.getUserInfo(user_name=user_name)
    if user_info:
        user_info = user_info[0]
    else:
        user_info = user_oper.getEmptyUserInfo()
        if user_name != '-1':
            user_info.user_name = user_name
    return user_info

if __name__ == '__main__':
    pass
