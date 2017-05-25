#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db_bz import pg
import time_bz
import db_bz


def getLast(user_id):
    '''
    >>> getLast('1')
    <Storage...>
    '''
    if user_id is None:
        return
    result = pg.select('last', where={'user_id': user_id}).list()
    if result:
        return result[0]


def getLastTime(user_id):
    last = getLast(user_id)
    if last:
        return last.last_time
    else:  # 未登录 or 第一次进来
        return time_bz.getBeforeDay()


def saveLast(last_time, user_id):
    '''
    create by bigzhu at 15/08/16 16:22:39 保存最后一条的message
    '''
    id = pg.insertIfNotExist('last', {'user_id': user_id, 'last_time': last_time}, "user_id='%s'" % user_id)
    if id is None:
        count = pg.update('last', where="last_time< $last_time  and user_id=$user_id", last_time=last_time, vars=locals())
        return count
    return 1

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
