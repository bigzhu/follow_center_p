#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pg
import json


def getTheGodInfoByName(god_name, user_id):
    result = pg.select('god', value='id', where={'name': god_name})
    if result:
        god_id = result[0].id
        return getTheGodInfo(god_id, user_id)
    else:
        raise Exception('god %s 不存在' % god_name)


def getTheGodInfo(god_id, user_id):
    sql = '''
    select * from god where god_id=$god_id
    '''
    sql = addGodfolloweInfoByUserId(sql)
    result = pg.query(sql, vars=locals())
    if (not result):
        raise Exception('未找到这个 god ' + god_id)
    return result[0]


def addGodfolloweInfoByUserId(sql):
    '''
    关联以查出对某个用户, 他是否关注了这个 god
    '''
    return '''
            select * from   (%s) ut left join
                (select god_id followed_god_id, 1 followed, stat_date followed_at from follow_who where user_id=$user_id) f
                on ut.god_id=f.followed_god_id
        ''' % sql


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
