#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_bz import pg


def collect(message_id, user_id):
    '''
    create by bigzhu at 16/05/20 14:21:02 加入收藏
    >>> collect(1, 1)
    '''
    id = pg.insertIfNotExist('collect', {'user_id': user_id, 'message_id': message_id}, "user_id='%s' and message_id=%s" % (user_id, message_id))
    return id

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
