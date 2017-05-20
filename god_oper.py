#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pg
import json


def getTheGodInfo(god_id, user_id):
    sql = '''
    select * from god where god_id=$god_id
    '''
    sql = addGodfollowed(sql, user_id)
    result = pg.query(sql, vars=locals())
    if (not result):
        raise Exception('未找到这个 god ' + god_id)
    return result[0]


def addGodfollowed(sql, user_id):
    '''
    关联以查出对某个用户, 他是否关注了这个 god
    '''
    if user_id:
        sql = '''
            select * from   (%s) ut left join
                (select god_id followed_god_id, 1 followed, stat_date followed_at from follow_who where user_id='%s') f
                on ut.god_id=f.followed_god_id
        ''' % (sql, user_id)
    return sql


def makeSureSocialUnique(type, name):
    '''
    create by bigzhu at 17/05/20 08:35:04 确保 Social 不重复
    '''
    sql = '''
    select * from god where %s ->>'name'::text = $name
    ''' % type
    if (pg.query(sql, vars=locals())):
        return None
    else:
        return json.dumps({'name': name})


def getFollowedGodCount(user_id):
    sql = '''
    select count(god_id) from follow_who where user_id=$user_id
    '''
    count = pg.query(sql, vars=locals())[0].count
    return count


if __name__ == '__main__':
    makeSureSocialUnique('twitter', 'bigzhu')
