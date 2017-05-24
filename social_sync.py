#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pg import pg


def getSocialGods(type, god_name=None):
    '''
    create by bigzhu at 17/05/21 18:11:06 获取有某个社交数据的 gods

    >>> getSocialGods('twitter')
    <utils.IterBetter instance at ...>
    '''

    sql = '''
    select * from god where %s is not null and %s->'name' <> to_jsonb(''::text)
    ''' % (type, type)
    if god_name:
        sql += " and name='%s'" % god_name
    return pg.query(sql)

if __name__ == '__main__':
    getSocialGods('twitter')
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
