# !/usr/bin/env python
# encoding=utf-8
import db_bz


conf = db_bz.getDBConf()
pg = db_bz.PG(**conf)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
