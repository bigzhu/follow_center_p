#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
from public_bz import storage


def getDBConf():
    '''
    >>> getDBConf()
    <Storage...>
    '''
    conf = storage()
    config = ConfigParser.ConfigParser()
    with open('conf/db.ini', 'r') as cfg_file:
        config.readfp(cfg_file)
        conf.host = config.get('db', 'host')
        conf.port = config.get('db', 'port')
        conf.db_name = config.get('db', 'db_name')
        conf.user = config.get('db', 'user')
        conf.password = config.get('db', 'password')
    return conf

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
