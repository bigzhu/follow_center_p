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
    db_name = config.get('db', 'db_name')
    user = config.get('db', 'user')
    password = config.get('db', 'password')

conn = psycopg2.connect(host=host, dbname=db_name, user=user, password=password)
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
