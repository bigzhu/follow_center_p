#!/usr/bin/env python
# -*- coding: utf-8 -*-


def addGodFollowedCount(sql):
    sql = '''
        select s.*, coalesce(c.count,0) as followed_count from   (%s) s left join (select count(id) as count,god_id from follow_who group by god_id) c on s.god_id=c.god_id
        ''' % sql
    return sql


def addGodRemark(sql):
    sql = '''
        select s.*, r.remark as admin_remark from   (%s) s left join (select remark, god_id from remark where user_id=1) r on s.god_id=r.god_id
        ''' % sql
    return sql
if __name__ == '__main__':
    pass
