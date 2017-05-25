#!/usr/bin/env python
# -*- coding: utf-8 -*-

import db_bz
from db_bz import pg


def unFollow(user_id, god_id):
    count = pg.delete('follow_who', where="user_id=$user_id and god_id=$god_id", vars=locals())
    if count != 1:
        raise Exception('没有正确的Unfollow, Unfollow %s 人' % count)


def follow(user_id, god_id, make_sure=True):
    '''
    create by bigzhu at 15/07/15 14:22:51
    modify by bigzhu at 15/07/15 15:00:28 如果不用告警,就不要make_sure
    '''
    id = pg.insertIfNotExist('follow_who', {'user_id': user_id, 'god_id': god_id}, "user_id='%s' and god_id=%s" % (user_id, god_id))
    if id is None and make_sure:
        raise Exception('没有正确的Follow, 似乎已经Follow过了呢')

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
