#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db_bz import pg


def insertTest():
    '''
    >>> insertTest()
    '''
    id = pg.insert('test', test=1)
    if id is None:
        raise Exception('fuck')

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
