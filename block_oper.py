#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pg
import db_bz


def unblock(user_id, god_id, make_sure=True):
    count = pg.delete('block', where="user_id=$user_id and god_id=$god_id", vars=locals())
    if count != 1 and make_sure:
        raise Exception('没有正确的Unblcok, Unblock %s 人' % count)


def block(user_id, god_id, make_sure=True):
    '''
    屏蔽某人
    '''
    id = db_bz.insertIfNotExist(pg, 'block', {'user_id': user_id, 'god_id': god_id}, "user_id='%s' and god_id=%s" % (user_id, god_id))
    if id is None and make_sure:
        raise Exception('没有正确的Block, 似乎已经Block过了呢')

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
