import psycopg2
conn_string = "dbname='follow_center' user='follow_center' host='127.0.0.1' password='follow_center'"
print "Connecting to database\n->%s" % (conn_string)

conn = psycopg2.connect(conn_string)
print "connection succeeded"

cur = conn.cursor()

cur.execute("SELECT *  from messages")

records = cur.fetchone()
print records
cur.close()
