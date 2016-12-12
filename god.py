#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pg


def getFollowedGodCount(user_id):
    sql = '''
    select count(god_id) from follow_who where user_id=%s
    ''' % user_id
    count = pg.query(sql)[0].count
    return count


if __name__ == '__main__':
    pass
