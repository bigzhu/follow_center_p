#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
soup = BeautifulSoup('<img width="600" height="400"/><img/><img/><img width="600" height="400"/>')
for img in soup.find_all('img'):
    img['class'] = 'ui image'
    del img['width']
    del img['height']
print str(soup)

if __name__ == '__main__':
    pass
