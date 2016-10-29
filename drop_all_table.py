#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psycopg2
import sys

# Drop all tables from a given database
import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/db.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    host = config.get('db', 'host')
    port = config.get('db', 'port')
    the_db = config.get('db', 'db')
    user = config.get('db', 'user')
    pw = config.get('db', 'pw')

try:
    conn = psycopg2.connect("dbname='%s' user='%s' password='%s'" % (the_db, user, pw))
    conn.set_isolation_level(0)
except:
    print "Unable to connect to the database."

cur = conn.cursor()

try:
    cur.execute("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_schema,table_name")
    rows = cur.fetchall()
    for row in rows:
        print "dropping table: ", row[1]
        cur.execute("drop table " + row[1] + " cascade")
    cur.close()
    conn.close()
except:
    print "Error: ", sys.exc_info()[1]
