#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("../lib_p_bz")

import json
import public_bz
import sys
from oper import sync

import datetime
import db_bz
import time_bz
import tornado.ioloop
import tornado.web
import tornado_bz
from tornado_bz import UserInfoHandler
from tornado_bz import BaseHandler
# from webpy_db import SQLLiteral

import oper
import pg
import filter_bz
import public_db
import proxy
import web_bz
from public_bz import storage
from bs4 import BeautifulSoup
import god
import anki

reload(sys)
sys.setdefaultencoding('utf-8')

OK = '0'
import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/twitter.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    consumer_key = config.get('secret', 'consumer_key')
    consumer_secret = config.get('secret', 'consumer_secret')
    access_token = config.get('secret', 'access_token')
    access_token_secret = config.get('secret', 'access_token_secret')


class api_login_anki(tornado_bz.UserInfoHandler):

    '''
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        anki_info = storage()
        anki_info.user_name = data['user_name']
        anki_info.password = data['password']
        anki_info.user_id = self.current_user
        db_bz.insertOrUpdate(pg, 'anki', anki_info, "user_id=%s" % anki_info.user_id)
        anki.getMidAndCsrfTokenHolder(anki_info.user_id, reset_cookie=True)
        self.write(json.dumps(self.data))


class api_anki(tornado_bz.UserInfoHandler):

    '''
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        front = data['front']
        anki.addCard(front, self.current_user)
        self.write(json.dumps({'error': '0'}))

    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def get(self):
        self.set_header("Content-Type", "application/json")
        sql = 'select user_name, password from anki where user_id=%s' % self.current_user
        datas = self.pg.query(sql)
        if datas:
            data = datas[0]
        else:
            data = None
        self.write(json.dumps({'error': '0', 'anki': data}, cls=public_bz.ExtEncoder))


class api_public_gods(BaseHandler):

    '''
    create by bigzhu at 16/12/11 22:32:39 公开推荐的god
    '''

    @tornado_bz.handleError
    def get(self, parm):

        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        cat = parm.get('cat')
        before = parm.get('before')
        limit = parm.get('limit')

        if before:
            before = time_bz.timestampToDateTime(before, True)

        gods = oper.getGods(self.current_user, cat=cat, is_public=True, limit=limit, before=before)

        self.write(json.dumps({'error': '0', 'gods': gods}, cls=public_bz.ExtEncoder))


class api_block(tornado_bz.UserInfoHandler):

    '''
    '''
    @tornado_bz.handleError
    def get(self, parm):
        self.set_header("Content-Type", "application/json")

        parm = json.loads(parm)
        count = parm.get('count', None)
        # is_public = parm.get('is_public', None)
        user_id = self.current_user

        if count:  # 只查总数
            sql = ''' select count(id) from block where user_id=%s''' % user_id
            self.data.count = self.pg.query(sql)[0].count

        self.write(json.dumps(self.data, cls=public_bz.ExtEncoder))

    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        god_id = data['god_id']
        oper.block(self.current_user, god_id)
        self.write(json.dumps({'error': '0'}))

    @tornado_bz.mustLoginApi
    @tornado_bz.handleError
    def delete(self, id):
        self.set_header("Content-Type", "application/json")
        oper.unblock(self.current_user, id)
        self.write(json.dumps(self.data))


class web_socket(web_bz.web_socket):
    pass


class api_rich_text(web_bz.rich_text):
    pass


class biography(BaseHandler):

    '''
    create by bigzhu at 16/09/04 18:03:31
    传记
    '''

    def get(self, id=None):
        if id is None:
            sql = '''
            select * from rich_text order by created_date desc limit 100
            '''
            biographys = list(pg.query(sql))
            self.render('../dist/biography.html', biographys=biographys)
        else:
            sql = '''
            select * from rich_text where id=%s
            ''' % id
            biographys = list(pg.query(sql))
            if biographys:
                biography = biographys[0]
                # 让img能响应式
                soup = BeautifulSoup(biography.text)
                for img in soup.find_all('img'):
                    img['class'] = 'ui image'
                    del img['width']
                    del img['height']
                biography.text = str(soup)
            god = {'img': ''}
            self.render('../dist/biography_detail.html', biography=biography, god=god)


class api_file_upload(web_bz.file_upload):
    pass


class api_registered(BaseHandler):

    @tornado_bz.handleError
    def get(self):
        self.set_header("Content-Type", "application/json")
        sql = '''
            select count(id) as count from user_info
        '''
        datas = self.pg.db.query(sql)
        registered_count = datas[0].count
        self.write(json.dumps({'error': '0', 'registered_count': registered_count}, cls=public_bz.ExtEncoder))


class api_remark(BaseHandler):

    '''
    create by bigzhu at 16/06/06 15:26:07 对god的备注
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        god_id = data['god_id']
        remark = data['remark']
        where = 'user_id=%s and god_id=%s' % (self.current_user, god_id)
        values = storage()
        values.user_id = self.current_user
        values.remark = remark
        values.god_id = god_id
        db_bz.insertOrUpdate(self.pg, 'remark', values, where)
        self.write(json.dumps({'error': '0'}))


class api_cat(BaseHandler):

    @tornado_bz.handleError
    def get(self, parm):
        self.set_header("Content-Type", "application/json")

        parm = json.loads(parm)
        is_my = parm.get('is_my', None)
        # is_public = parm.get('is_public', None)
        user_id = self.current_user
        sql = '''
        select * from god
        '''

        sql = filter_bz.filterHaveSocialGod(sql)
        if is_my:
            sql = filter_bz.filterMyGod(sql, user_id)
        else:
            sql = filter_bz.filterPublicGod(sql)
            sql = filter_bz.filter18God(sql)

        sql = '''
            select count(id) count,cat from (%s) s group by cat order by count desc,cat
        ''' % sql
        print sql
        cats = list(self.pg.db.query(sql))
        self.write(json.dumps({'error': '0', 'cats': cats}, cls=public_bz.ExtEncoder))


class api_collect(BaseHandler):

    '''
    create by bigzhu at 16/05/20 14:17:20 收藏
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(self.request.body)
        message_id = parm['message_id']
        oper.collect(message_id, self.current_user)
        self.write(json.dumps({'error': '0'}))

    @tornado_bz.mustLoginApi
    @tornado_bz.handleError
    def delete(self, id):
        self.set_header("Content-Type", "application/json")
        count = pg.delete('collect', where="user_id=%s and message_id=%s" % (self.current_user, id))
        if count != 1:
            raise Exception('没有正确的uncollect, uncollect %s 条' % count)
        self.write(json.dumps({'error': '0'}))

    @tornado_bz.mustLoginApi
    @tornado_bz.handleError
    def get(self):
        self.set_header("Content-Type", "application/json")
        messages = public_db.getCollectMessages(user_id=self.current_user)
        self.write(json.dumps({'error': '0', 'messages': messages}, cls=public_bz.ExtEncoder))


class api_social(BaseHandler):

    @tornado_bz.handleError
    def get(self, parm):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        name = parm['name']
        type = parm['type']
        info = public_db.getSocialUser(name, type)
        if not info:  # 已有就直接返回了
            if type == 'twitter':
                import twitter
                twitter.getTwitterUser(name, name)
            if type == 'github':
                import github
                sync(type, github.main, name)
            if type == 'instagram':
                import reptile_instagram
                reptile_instagram.run(name)
            if type == 'tumblr':
                import tumblr
                sync(type, tumblr.main, name)
            if type == 'facebook':
                import facebook
                facebook.run(name)

            info = public_db.getSocialUser(name, type)
        self.write(json.dumps({'error': '0', 'info': info}, cls=public_bz.ExtEncoder))


class api_logout(BaseHandler):

    @tornado_bz.handleError
    def get(self):
        self.clear_cookie(name='user_id')
        self.redirect("/")


class api_not_my_gods(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 16/03/24 23:19:19
    '''
    @tornado_bz.handleError
    def get(self, parm):

        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        cat = parm['cat']

        recommand = None
        if cat == 'recommand':
            cat = None
            recommand = True
        if self.current_user:
            if cat == 'all':  # 特殊处理，显示所有我没关注的god
                gods = oper.getGods(self.current_user, recommand=recommand)
            else:
                gods = oper.getGods(self.current_user, cat=cat, recommand=recommand, is_public=True)
        else:
            gods = oper.getGods(cat=cat, recommand=recommand, is_public=True)
        self.write(json.dumps({'error': '0', 'gods': gods}, cls=public_bz.ExtEncoder))


class api_my_gods(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 16/03/24 14:22:54
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def get(self, parm):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        cat = parm.get('cat')
        blocked = parm.get('blocked')
        gods = oper.getGods(self.current_user, is_my=True, cat=cat, blocked=blocked)
        self.write(json.dumps({'error': '0', 'gods': gods}, cls=public_bz.ExtEncoder))


class api_gods(BaseHandler):

    '''
    create by bigzhu at 16/08/22 20:56:25
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def get(self, parm):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        cat = parm.get('cat')
        is_my = parm.get('is_my')
        blocked = parm.get('blocked')
        gods = oper.getGods(cat=cat, is_my=is_my, blocked=blocked, user_id=self.current_user)
        self.write(json.dumps({'error': '0', 'gods': gods}, cls=public_bz.ExtEncoder))


class api_follow(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/07/14 17:11:45 follow
    '''
    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        god_id = data['god_id']
        user_id = self.current_user
        oper.follow(user_id, god_id)
        oper.unblock(user_id, god_id, False)
        self.write(json.dumps(self.data))

    @tornado_bz.mustLoginApi
    @tornado_bz.handleError
    def delete(self, id):
        self.set_header("Content-Type", "application/json")
        count = pg.delete('follow_who', where="user_id=%s and god_id=%s" % (self.current_user, id))
        if count != 1:
            raise Exception('没有正确的Unfollow, Unfollow %s 人' % count)
        self.write(json.dumps({'error': '0'}))


class api_apply_del(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 16/08/22 15:07:42 处理apply_del
    '''

    @tornado_bz.mustLoginApi
    @tornado_bz.handleError
    def get(self):
        self.set_header("Content-Type", "application/json")
        sql = '''
        select * from apply_del where stat is null order by created_date desc
        '''
        apply_dels = self.pg.query(sql)
        self.write(json.dumps({'error': '0', 'apply_dels': apply_dels}, cls=public_bz.ExtEncoder))

    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def put(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        social_name = data['social_name']
        if social_name == '' or social_name is None:
            raise Exception('必须有god名字才能修改')
        type = data['type']
        if type == '' or type is None:
            raise Exception('必须有type才能修改')

        count = public_db.delNoName(type, social_name)
        # if count != 1:
        #     raise Exception("修改失败 type:%s social_name: %s count: %s" % (type, social_name, count))

        sql = ''' update apply_del set stat=1 where social_name='%s' and type='%s' and stat is null''' % (social_name, type)
        count = self.pg.query(sql)
        if count != 1:
            raise Exception("修改失败" + count)

        self.write(json.dumps({'error': '0', 'count': count}, cls=public_bz.ExtEncoder))

    @tornado_bz.mustLoginApi
    @tornado_bz.handleError
    def delete(self, id):
        self.set_header("Content-Type", "application/json")
        count = pg.delete('apply_del', where="id=%s" % id)
        if count != 1:
            raise Exception('没有正确的reject del apply, reject %s 人' % count)
        self.write(json.dumps({'error': '0'}))


class api_god(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 16/03/09 11:00:52 要跟踪的人
    '''

    @tornado_bz.handleError
    def get(self, parm):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        god_name = parm['god_name']
        god_info = oper.getGodInfo(god_name, self.current_user)
        self.write(json.dumps({'error': '0', 'god_info': god_info}, cls=public_bz.ExtEncoder))

    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def post(self):
        '''
        modify by bigzhu at 16/04/26 10:48:43 已经存在时不要update
        modify by bigzhu at 16/06/18 11:36:12 如果是public的，不要update cat
        modify by bigzhu at 16/06/25 07:48:51 cat = recommand 时, 改为大杂烩
        '''

        self.set_header("Content-Type", "application/json")
        user_id = self.current_user
        data = json.loads(self.request.body)
        name = data['name']
        cat = data.get('cat', '大杂烩')
        data = {
            'name': name,
            'cat': cat,
            'twitter': name,
            'github': name,
            'instagram': name,
            'tumblr': name,
        }
        # 去了social中有相同名字的
        oper.cleanSocialData(data, 'twitter')
        oper.cleanSocialData(data, 'github')
        oper.cleanSocialData(data, 'instagram')
        oper.cleanSocialData(data, 'tumblr')

        god_id = db_bz.insertIfNotExist(pg, 'god', data, "lower(name)=lower('%s')" % name)

        where = "name='%s'" % name
        god_info = self.pg.select('god', where=where)[0]
        god_id = god_info.id
        if god_info.is_black == 1:
            raise Exception('%s这是一个黑名名帐号,不添加!' % name)

        # if god_info.cat != cat:
        #     where += " and is_public != 1"
        #     self.pg.update('god', where=where, cat=cat, stat_date=SQLLiteral('NOW()'), user_id=self.current_user)
        # 加入自已的
        values = storage()
        values.god_id = god_id
        values.cat = cat
        values.user_id = self.current_user
        where = "user_id=%s and god_id=%s" % (values.user_id, values.god_id)
        db_bz.insertOrUpdate(self.pg, 'who_add_god', values, where)

        oper.follow(self.current_user, god_id, make_sure=False)

        god_info = oper.getGodInfo(name, user_id=user_id)

        self.write(json.dumps({'error': '0', 'god_info': god_info}, cls=public_bz.ExtEncoder))

    @tornado_bz.handleError
    @tornado_bz.mustLoginApi
    def put(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        name = data['name']
        if name == '' or name is None:
            raise Exception('必须有名字才能修改')

        oper.checkSocialData(data, 'twitter')
        oper.checkSocialData(data, 'github')
        oper.checkSocialData(data, 'tumblr')
        oper.checkSocialData(data, 'instagram')

        where = " name='%s'" % name
        count = self.pg.update("god", where=where, **data)
        if count != 1:
            raise Exception("修改失败" + count)

        self.write(json.dumps({'error': '0', 'count': count}, cls=public_bz.ExtEncoder))


class api_get_user_info(web_bz.get_user_info):
    pass


class api_login(web_bz.api_login):
    pass


class signup(web_bz.signup):
    pass


class ProxyHandler(proxy.ProxyHandler):
    pass


class api_sp(proxy.ProxyHandler):

    '''
    create by bigzhu at 15/08/05 22:52:44 加密方式传递url
    '''

    def get(self, secret):
        url = oper.decodeUrl(secret)
        print ('proxy ', url)
        if self.settings["disable_sp"]:
            url = 'http://cdn.v2ex.co/avatar/43dd/49b4/1066_large.png?m=1430489276'
        return super(api_sp, self).get(url)


class api_github(web_bz.github):

    '''
    github 登录
    '''

    def initialize(self):
        web_bz.github.initialize(self)

        client_id = 'ee3c1a6f0c56345df334'
        client_secret = '365f15ac030aeab6188749602810f099c7953eb6'
        self.settings['github_oauth'] = {'client_secret': client_secret,
                                         'client_id': client_id,
                                         'redirect_uri': 'http://follow.center/api_github'}
        self.merge = True


class api_twitter(web_bz.twitter):

    '''
    twitter 登录
    '''

    def initialize(self):
        # twitter
        web_bz.twitter.initialize(self)

        self.settings["twitter_consumer_key"] = consumer_key
        self.settings["twitter_consumer_secret"] = consumer_secret
        self.merge = True


class api_douban(web_bz.douban):

    def initialize(self):
        web_bz.douban.initialize(self)
        self.settings["douban_api_key"] = '05e0604f2b78f83011a120ed826ae890'
        self.settings["douban_api_secret"] = '037c6cf87565a90d'
        self.settings["redirect_uri"] = 'http://follow.center/api_douban'
        self.merge = True


class api_facebook(web_bz.facebook):

    def initialize(self):
        web_bz.facebook.initialize(self)
        self.settings["facebook_api_key"] = '1181207665262692'
        self.settings["facebook_secret"] = 'c0478bd3f100528989ce90ba5c1e8713'
        self.settings["facebook_redirect_uri"] = 'http://follow.center/api_facebook'


class api_qq(web_bz.qq):

    def initialize(self):
        web_bz.qq.initialize(self)
        self.settings["qq_api_key"] = '101318491'
        self.settings["qq_api_secret"] = '5e8062b4dab5d750aadccc3490c75199'
        self.settings["qq_redirect_uri"] = 'https://follow.center/api_qq'


class main(UserInfoHandler):

    '''
    首页
    create by bigzhu at 15/07/11 16:21:16
    '''

    @tornado_bz.mustLogin
    def get(self, limit=None):
        # self.render(tornado_bz.getTName(self, 'app'))
        self.redirect('/app/')


class api_last(tornado_bz.UserInfoHandler):

    def put(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        last_time = int(data.get('last_time'))
        last_time = time_bz.timestampToDateTime(last_time, True)
        # last_message_id = data.get('message_id')
        user_id = self.current_user

        if user_id is None:
            pass
        else:
            oper.saveLast(last_time, user_id)
        data = storage()
        data.error = OK
        data.unread_message_count = oper.getUnreadCount(user_id)

        self.write(json.dumps(data, cls=public_bz.ExtEncoder))


class messages_app(tornado_bz.UserInfoHandler):

    '''
    '''

    def get(self):
        self.render(tornado_bz.getTName(self))


class api_message(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 16/04/24 11:31:30 操作某个特定message
    '''

    @tornado_bz.handleError
    def get(self, parm=None):

        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        id = parm['id']

        messages = public_db.getMessage(id=id, user_id=self.current_user)
        if messages:
            message = messages[0]
        else:
            raise Exception('没有这条信息')

        self.write(json.dumps({'error': '0', 'message': message}, cls=public_bz.ExtEncoder))


class api_new(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/08/17 11:12:24 查看我订阅了的message，要定位到上一次看的那条
    modify by bigzhu at 15/11/17 16:22:05 最多查1000出来
    modify by bigzhu at 15/11/17 19:18:25 不要在这里限制条目数
    modify by bigzhu at 16/02/21 10:02:25 改为get
    modify by bigzhu at 16/04/29 14:54:37 支持关键字查找
    modify by bigzhu at 16/05/28 23:10:05 重构
    '''

    def get(self, parm=None):

        starttime = datetime.datetime.now()
        self.set_header("Content-Type", "application/json")
        after = None
        limit = None
        search_key = None
        god_name = None
        if parm:
            parm = json.loads(parm)
            after = parm.get('after')  # 晚于这个时间的
            limit = parm.get('limit')
            search_key = parm.get('search_key')
            god_name = parm.get('god_name')  # 只查这个god

        user_id = self.current_user
        if after:
            after = time_bz.timestampToDateTime(after, True)
        elif search_key is None and god_name is None:  # 这些条件查询不能卡上次看到那条的时间
            after = oper.getLastTime(user_id)

        messages = public_db.getNewMessages(user_id=user_id, after=after, limit=limit, god_name=god_name, search_key=search_key)
        data = storage()
        data.error = OK
        data.messages = messages
        data.unread_message_count = oper.getUnreadCount(user_id)
        if (len(messages) == 0):
            if (user_id):
                data.followed_god_count = god.getFollowedGodCount(user_id)
            else:
                data.followed_god_count = 0

        endtime = datetime.datetime.now()

        print 'api_new cost'
        print (endtime - starttime).seconds
        self.write(json.dumps(data, cls=public_bz.ExtEncoder))


class api_old(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/08/17 11:06:40 用来查all的更多,不需要定位
    modify by bigzhu at 16/02/22 09:40:49 按参数来判断
    '''

    def get(self, parm=None):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        before = parm['before']
        god_name = parm.get('god_name')
        search_key = parm.get('search_key')
        limit = parm.get('limit')
        if limit is None:
            limit = 10
        before = time_bz.timestampToDateTime(before, True)
        messages = public_db.getOldMessages(before=before, search_key=search_key, god_name=god_name, limit=limit, user_id=self.current_user)
        self.write(json.dumps({'error': '0', 'messages': messages}, cls=public_bz.ExtEncoder))


class api_big_gods(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/08/28 17:04:40 随机推荐5个没关注的人
    '''

    def get(self):
        self.set_header("Content-Type", "application/json")
        gods = oper.getGods(self.current_user, recommand=True)
        self.write(json.dumps({'error': '0', 'gods': gods}, cls=public_bz.ExtEncoder))


class api_god_info(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/11/27 10:29:35 查出这个god的信息
    '''

    @tornado_bz.handleError
    def get(self, parm):
        self.set_header("Content-Type", "application/json")
        parm = json.loads(parm)
        god_name = parm.get('god_name')

        god_info = oper.getGodInfo(god_name, self.current_user)
        self.write(json.dumps({'error': '0', 'god_info': god_info}, cls=public_bz.ExtEncoder))


class user_info(tornado_bz.UserInfoHandler):

    def post(self):
        self.set_header("Content-Type", "application/json")
        data = json.loads(self.request.body)
        god_name = data.get('user_name', None)

        god_info = list(public_db.getGodInfoFollow(self.current_user, god_name))
        if god_info:
            god_info = god_info[0]
        self.write(json.dumps({'error': '0', 'user_info': god_info}, cls=public_bz.ExtEncoder))


class Changelog(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/07/19 22:15:13
    '''

    def get(self):
        self.render(tornado_bz.getTName(self))


class message(tornado_bz.UserInfoHandler):

    '''
    某条信息
    create by bigzhu at 15/07/19 15:27:45
    '''

    def get(self):
        type = self.get_argument('t', None, True)
        id = self.get_argument('id', None, True)
        messages = public_db.getMessages(type=type, id=id)
        self.render(tornado_bz.getTName(self, "main"), messages=messages)


class users(tornado_bz.UserInfoHandler):

    '''
    create by bigzhu at 15/07/12 23:43:54 显示所有的大神, 关联twitter
    modify by bigzhu at 15/07/17 15:20:26 关联其他的,包括 github
    '''

    def get(self):
        # users = public_db.getUserInfoTwitterUser(self.current_user)
        gods = oper.getGods(self.current_user)
        self.render(self.template, users=gods)


class NoCacheHtmlStaticFileHandler(tornado.web.StaticFileHandler):

    def set_extra_headers(self, path):
        if path == '':
            # self.set_header("Cache-control", "no-cache")
            self.set_header("Cache-control", "no-store, no-cache, must-revalidate, max-age=0")

if __name__ == "__main__":

    debug = None
    if len(sys.argv) == 3:
        port = int(sys.argv[1])
        debug = sys.argv[2]
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 9000
    print (port)

    web_class = tornado_bz.getAllWebBzRequestHandlers()
    web_class.update(globals().copy())

    url_map = tornado_bz.getURLMap(web_class)
    # 机器人
    # url_map.append((r'/robots.txt()', tornado.web.StaticFileHandler, {'path': "./static/robots.txt"}))
    # sitemap
    # url_map.append((r'/sitemap.xml()', tornado.web.StaticFileHandler, {'path': "./static/sitemap.xml"}))

    url_map.append((r"/app/(.*)", NoCacheHtmlStaticFileHandler, {"path": "../", "default_filename": "index.html"}))
    url_map.append((r'/web_socket', web_socket))
    url_map.append((r'/biography.html', biography))
    url_map.append((r'/', main))
    # url_map.append((r'/static/(.*)', tornado.web.StaticFileHandler, {'path': "./static"}))

    settings = tornado_bz.getSettings()
    settings["pg"] = pg
    if debug:
        settings["disable_sp"] = True
    else:
        settings["disable_sp"] = None
    settings["login_url"] = "/app/login.html"
    # settings, wechat = wechat_oper.initSetting(settings)
    application = tornado.web.Application(url_map, **settings)

    application.listen(port)
    ioloop = tornado.ioloop.IOLoop().instance()

    tornado.autoreload.start(ioloop)
    ioloop.start()
