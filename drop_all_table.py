#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import sys

# Drop all tables from a given database

import db_conf
conf = db_conf.getDBConf()


def main():
    conn = psycopg2.connect(host=conf.host, dbname=conf.db_name, user=conf.user, password=conf.password)
    conn.set_isolation_level(0)

    cur = conn.cursor()

    try:
        cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
        rows = cur.fetchall()
        for row in rows:
            print "dropping table: ", row[1]
            # cur.execute("drop table " + row[1] + " cascade")
        cur.close()
        conn.close()
    except:
        print "Error: ", sys.exc_info()[1]

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
