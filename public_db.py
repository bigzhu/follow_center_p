#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pg
import user_bz
import db_bz
from webpy_db import SQLLiteral
user_oper = user_bz.UserOper(pg)


def addBlockSql(sql, user_id):
    # block
    sql = '''
        select * from (%s) s where s.god_id not in (select god_id from block where user_id=%s)
    ''' % (sql, user_id)
    return sql


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


def sendDelApply(type, god_name, reason=None):
    '''
    提交del申请，已有就+1
    '''
    data = {'type': type, 'god_name': god_name, 'reason': reason}
    table_name = 'apply_del'
    where = "lower(god_name)=lower('%s') and type='%s'" % (god_name, type)
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
        sql = '''
            select m.*, c.message_id as collect, c.created_date as collect_date
                from (%s) m
            LEFT OUTER JOIN collect c
                ON m.id = c.message_id
                and c.user_id=%s
        ''' % (sql, user_id)
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
    # 关联collect表
    sql = '''
        select m.*, c.message_id as collect, c.created_date as collect_date
            from (%s) m
        LEFT OUTER JOIN collect c
            ON m.id = c.message_id
            and c.user_id=%s
    ''' % (sql, user_id)
    sql = '''
    select * from (%s) s
    where collect is not null
    ''' % sql
    # order by
    sql += ' order by collect_date desc '
    return pg.query(sql)


def getNewMessages(user_id=None, after=None, limit=None, god_name=None, search_key=None, m_type=None):
    '''
    create by bigzhu at 16/05/28 22:01:58 查new的，根据mind图重构
    '''
    sql = '''
    select * from all_message m
    '''
    # 关联collect表
    if user_id:
        sql = '''
            select m.*, c.message_id as collect, c.created_date as collect_date
                from (%s) m
            LEFT OUTER JOIN collect c
                ON m.id = c.message_id
                and c.user_id=%s
        ''' % (sql, user_id)
    else:
        # 不给看18+
        sql += " where lower(name) not in (select lower(name) from god where cat='18+') "
        # 只能看 public god 的 message
        sql += " and lower(name) in (select lower(name) from god where is_public=1) "
    # 封住，以直接加where
    sql = ''' select * from (%s) s ''' % sql
    # 查比这个时间新的
    if after:
        sql += " where created_at > '%s' " % after
        # 再封
        sql = ''' select * from (%s) s ''' % sql
    # 互斥的filter
    if god_name:
        sql += " where lower(s.user_name)=lower('%s') " % god_name
    elif search_key:
        # sql += " where upper(s.text) like '%%%s%%' or upper(s.content::text) like '%%%s%%' " % (search_key.upper(), search_key.upper())
        sql = filterSearchKey(sql, search_key)
    else:
        if user_id:
            sql += '''
            where lower(s.name) in (
                select lower(name) from god where id in(
                        select god_id from follow_who where user_id=%s
                    )
            )
            ''' % user_id

    if m_type:
        sql += " and s.m_type='%s' " % m_type
    # order by
    sql += ' order by created_at '
    # limit
    if limit is None and after is None:
        limit = 99
    sql += ' limit %s ' % limit
    # print sql
    return pg.query(sql)


def getOldMessages(before, user_id=None, limit=None, god_name=None, search_key=None, m_type=None):
    '''
    create by bigzhu at 16/05/29 08:06:28 查老的
    '''
    sql = '''
    select * from all_message m where 1=1
    '''
    # 关联collect表
    if user_id:
        sql = '''
            select m.*, c.message_id as collect, c.created_date as collect_date
                from (%s) m
            LEFT OUTER JOIN collect c
                ON m.id = c.message_id
                and c.user_id=%s
        ''' % (sql, user_id)
    else:  # 不给看18+
        sql += " and lower(name) not in (select lower(name) from god where cat='18+') "
    # 封住，以直接加where
    sql = ''' select * from (%s) s ''' % sql

    # 互斥的filter
    if god_name:
        sql += " where lower(s.name)=lower('%s') " % god_name
    elif search_key:
        sql = filterSearchKey(sql, search_key)
    else:
        if user_id:
            sql += '''
            where lower(s.name) in (
                select lower(name) from god where id in(
                        select god_id from follow_who where user_id=%s
                    )
            )
            ''' % user_id

    sql = filterMTYpe(sql, m_type)
    sql = filterBefore(sql, before)

    # order by
    if search_key is None:
        sql += ' order by created_at desc '
    # limit
    if limit is None:
        limit = 10
    sql += ' limit %s ' % limit
    print sql
    return pg.query(sql)


def filterSearchKey(sql, search_key):
    if search_key:
        sql = '''
            select * from (%s) s where upper(s.text) like '%%%s%%' or upper(s.content::text) like '%%%s%%'
            ''' % (sql, search_key.upper(), search_key.upper())
    return sql


def filterMTYpe(sql, m_type):
    if m_type:
        sql = '''
            select * from (%s) s where s.m_type = '%s'
        ''' % (sql, m_type)
    return sql


def filterBefore(sql, before):
    if before:
        sql = '''
            select * from (%s) s where s.created_at < '%s'
        ''' % (sql, before)
    return sql


def getGodInfoFollow(user_id=None, god_name=None, recommand=False, is_my=None, cat=None, is_public=None, limit=None, before=None):
    '''
    modify by bigzhu at 15/08/06 17:05:22 可以根据god_name来取
    modify by bigzhu at 15/08/28 17:09:31 推荐模式就是只查随机5个
    modify by bigzhu at 15/08/28 17:30:38 没有社交帐号的不要查出来
    modify by bigzhu at 16/03/24 21:46:07 可以只查我关注的
    modify by bigzhu at 16/05/24 23:21:36 关联到god表,可以只查某种类别
    modify by bigzhu at 16/05/27 22:16:30 没人关注的也查出来
    modify by bigzhu at 16/06/21 12:15:24 add xmind, 整理了sql
    '''
    sql = '''
    select  g.id as god_id,
            g.stat_date as u_stat_date,
    * from god g
        where
            not ((tumblr is null or tumblr='') and (twitter is null or twitter='') and (github is null or github='') and (instagram is null or instagram=''))
    '''

    sql = '''
        select s.*, coalesce(c.count,0) as followed_count from   (%s) s left join (select count(id) as count,god_id from follow_who group by god_id) c on s.god_id=c.god_id
        ''' % sql

    # 只查有人关注的
    # sql = '''
    #     select * from (%s) s  where s.id in (select god_id from follow_who)
    # ''' % sql

    sql = '''
        select s.*, r.remark as admin_remark from   (%s) s left join (select remark, god_id from remark where user_id=1) r on s.god_id=r.god_id
        ''' % sql
    if user_id:
        # followed info
        sql = '''
            select * from   (%s) ut left join (select god_id followed_god_id, 1 followed, stat_date followed_at from follow_who where user_id=%s) f on ut.god_id=f.followed_god_id
            order by ut.u_stat_date desc
        ''' % (sql, user_id)
        sql = addBlockSql(sql, user_id)
        # remark info
        sql = '''
            select s.*, r.remark from   (%s) s left join (select remark, god_id from remark where user_id=%s) r on s.god_id=r.god_id
            ''' % (sql, user_id)
        if recommand:
            sql = '''
            select * from (%s) s where s.followed=0 or s.followed is null
            ''' % sql
            if not cat:
                sql = '''
                select * from (%s) s  where s.cat not in('18+')
                ''' % sql
        if is_my:
            sql = '''
            select * from (%s) s  where s.followed=1
            ''' % sql
    else:
        if recommand:
            sql = '''
            select * from (%s) s  where s.cat not in('18+')
            ''' % sql

    if cat:
        sql = '''
        select * from (%s) s where lower(cat)=lower('%s')
        ''' % (sql, cat)
    if god_name:
        sql = '''
        select * from (%s) s where lower(name)=lower('%s')
        ''' % (sql, god_name)
    if is_public:
        sql = '''
        select * from (%s) s where is_public = 1
        ''' % sql
        # if user_id:
        #     sql = '''
        #     select * from (%s) s where  is_public = 1 or s.god_id in (select god_id from who_add_god where user_id=%s)
        #     ''' % (sql, user_id)
        # else:
        #     sql = '''
        #     select * from (%s) s where is_public = 1
        #     ''' % sql

    # sql += "  order by followed_count desc "
    if before:
        sql = '''
        select * from (%s) s where created_date < '%s'
        ''' % (sql, before)
    sql += "  order by created_date desc "
    if limit:
        sql += ' limit %s ' % limit
    print sql
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
