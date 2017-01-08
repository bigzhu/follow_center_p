#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import oper_bz
deck = 'Default'


def getCookies(username, password):
    url = 'https://ankiweb.net/account/login'
    login_info = {'submitted': '1', 'username': username, 'password': password}
    r = requests.post(url, data=login_info)
    return r.cookies


def addCard(front):
    cookies = getCookies('vermiliondun@gmail.com', 'z129854')
    url = 'https://ankiweb.net/edit/save'
    front = oper_bz.relativePathToAbsolute(front, 'https://follow.center')
    data = [[front, ''], '']
    data = json.dumps(data)
    save_info = {'data': data, 'mid': '1479215711126', 'deck': deck}
    r = requests.post(url, cookies=cookies, data=save_info)
    if r.text != '1':
        raise Exception('error: %s' % r.text)

if __name__ == '__main__':
    pass
