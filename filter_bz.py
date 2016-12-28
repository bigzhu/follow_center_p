#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
db 的过滤条件
'''


def filter(sql, where):
    sql = '''
        select * from (%s) s where %s
    ''' % (sql, where)
    return sql


def filterMyGod(sql, user_id):
    if user_id:
        where = '''
            s.id in(select god_id from follow_who where user_id=%s)
        ''' % user_id
        sql = filter(sql, where)
    return sql


def filterPublicGod(sql):
    where = '''
        s.is_public in (1, 2)
    '''
    sql = filter(sql, where)
    return sql


def filterPublicGodMessages(sql):
    where = '''
        lower(s.name) in (select lower(name) from god where is_public in (1,2) )
    '''
    sql = filter(sql, where)
    return sql


def filterAfterMessages(sql, after):
    if after:
        where = '''
            s.created_at > '%s'
        ''' % after
        sql = filter(sql, where)
    return sql


def filterFollowedMessages(sql, user_id):
    if user_id:
        where = '''
        lower(s.name) in (
            select lower(name) from god where id in(
                    select god_id from follow_who where user_id=%s
                )
        )
        ''' % user_id
        sql = filter(sql, where)
    return sql


def filterBlock(sql, user_id):
    # block
    if user_id:
        where = '''
            s.god_id not in (select god_id from block where user_id=%s)
        ''' % user_id
        sql = filter(sql, where)
    return sql


def filterSearchKey(sql, search_key):
    if search_key:
        where = '''
            upper(s.text) like '%%%s%%' or upper(s.content::text) like '%%%s%%'
            ''' % (search_key.upper(), search_key.upper())
        sql = filter(sql, where)
    return sql


def filterMTYpe(sql, m_type):
    if m_type:
        where = '''
            s.m_type = '%s'
        ''' % m_type
        sql = filter(sql, where)
    return sql


def filterBefore(sql, before):
    if before:
        where = '''
            s.created_at < '%s'
        ''' % before
        sql = filter(sql, where)
    return sql

if __name__ == '__main__':
    pass
