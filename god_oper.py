#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pg
import json


def delNoName(type, god_name):
    '''
    modify by bigzhu at 16/05/27 11:01:43 删除没有的社交
    >>> delNoName('instagram', 'bigzhu')
    del ...
    1
    '''
    values = {type: json.dumps({'name': ''})}
    count = pg.update('god', where={'name': god_name}, **values)
    print 'del %s %s' % (type, god_name)
    return count


def checkOtherNameSocialNameUnique(god_name, social_name, type):
    '''
    create by bigzhu at 17/05/21 16:39:02 检查其他的god下是否已有相同名字的 social

    >>> checkOtherNameSocialNameUnique('bigzhu', 'bigzhu', 'twitter')
    >>> checkOtherNameSocialNameUnique('bigzhu2', 'bigzhu', 'twitter')
    Traceback (most recent call last):
        ...
    Exception: 已有别人绑定了 twitter bigzhu, 修改失败
    '''
    sql = '''
    select * from god where name <> $god_name and  %s ->>'name'::text = $social_name
    ''' % type
    if (pg.query(sql, vars=locals())):
        raise Exception('已有别人绑定了 %s %s, 修改失败' % (type, social_name))


def getTheGodInfoByName(god_name, user_id):
    result = pg.select('god', what='id', where={'name': god_name})
    if result:
        god_id = result[0].id
        return getTheGodInfo(god_id, user_id)
    else:
        raise Exception('god %s 不存在' % god_name)


def getTheGodInfo(god_id, user_id):
    '''
    >>> getTheGodInfo(1, '1')
    <Storage...>
    '''
    sql = '''
    select id as god_id, * from god where id=$god_id
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

    >>> makeSureSocialUnique('twitter', 'bigzhu')
    >>> makeSureSocialUnique('twitter', 'bigzhu1')
    '{"name": "bigzhu1"}'
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
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
