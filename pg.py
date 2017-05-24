# !/usr/bin/env python
# encoding=utf-8
from db_bz import PG
import db_conf


conf = db_conf.getDBConf()
pg = PG(**conf)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
