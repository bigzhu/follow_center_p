#!/usr/bin/env python
# -*- coding: utf-8 -*-


def messagesAnkiSave(sql, user_id):
    if user_id:
        sql = '''
            select m.*, c.message_id as anki, c.created_date as anki_date
                from (%s) m
            LEFT OUTER JOIN anki_save c
                ON m.id = c.message_id
                and c.user_id=%s
        ''' % (sql, user_id)
    return sql


def messagesCollect(sql, user_id):
    if user_id:
        sql = '''
            select m.*, c.message_id as collect, c.created_date as collect_date
                from (%s) m
            LEFT OUTER JOIN collect c
                ON m.id = c.message_id
                and c.user_id=%s
        ''' % (sql, user_id)
    return sql


def addGodFollowedCount(sql):
    sql = '''
        select s.*, coalesce(c.count,0) as followed_count from   (%s) s left join (select count(id) as count,god_id from follow_who group by god_id) c on s.god_id=c.god_id
        ''' % sql
    return sql


def godAdminRemark(sql):
    sql = '''
        select s.*, r.remark as admin_remark from   (%s) s left join (select remark, god_id from remark where user_id=1) r on s.god_id=r.god_id
        ''' % sql
    return sql


def godUserRemark(sql, user_id):
    sql = '''
        select s.*, r.remark from   (%s) s left join (select remark, god_id from remark where user_id=%s) r on s.god_id=r.god_id
        ''' % (sql, user_id)
    return sql


def godfollowed(sql, user_id):
    sql = '''
        select * from   (%s) ut left join
            (select god_id followed_god_id, 1 followed, stat_date followed_at from follow_who where user_id=%s) f
            on ut.god_id=f.followed_god_id
    ''' % (sql, user_id)
    return sql
if __name__ == '__main__':
    pass
