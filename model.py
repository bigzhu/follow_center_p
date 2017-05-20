#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
初始化数据库
'''
import sys
sys.path.append("../lib_p_bz")

try:
    from playhouse.postgres_ext import PostgresqlExtDatabase
    from peewee import SQL
    from playhouse.postgres_ext import BinaryJSONField, JSONField
    from peewee import TextField, IntegerField, DateTimeField, BooleanField
except ImportError:
    print 'you need install peewee, please run:'
    print 'sudo pip install peewee'
    exit(1)

import ConfigParser
config = ConfigParser.ConfigParser()
with open('conf/db.ini', 'r') as cfg_file:
    config.readfp(cfg_file)
    host = config.get('db', 'host')
    port = config.get('db', 'port')
    db_name = config.get('db', 'db_name')
    user = config.get('db', 'user')
    password = config.get('db', 'password')

psql_db = PostgresqlExtDatabase(db_name, user=user, password=password, host=host, register_hstore=False)

import model_bz


class BaseModel(model_bz.base):

    class Meta:
        database = psql_db


class message(BaseModel):

    '''
    create by bigzhu at 16/03/25 14:52:27 冗余存放数据，提高效率
    '''
    god_id = IntegerField(null=True)  # 实际上是你要follow的用户的id
    god_name = TextField(null=True)  # 在本系统的主用户名
    name = TextField(null=True)  # 在社交帐号的名字
    # avatar = TextField(null=True)  # 发布者的头像

    id_str = TextField(null=True)  # 外部的id, 避免重复同步
    m_type = TextField()  # twitter or instagram or github
    created_at = DateTimeField()  # 在对应社交帐号真实的生成时间
    content = BinaryJSONField(null=True)  # 带结构的内容github
    text = TextField(null=True)  # 文本内容
    # title = TextField(null=True)  # tumblr text blog 的 title
    extended_entities = BinaryJSONField(null=True)  # 扩展内容,图片什么
    href = TextField(null=True)  # message 的link
    type = TextField(null=True)  # media type


class follow_who(BaseModel):

    '''
    create by bigzhu at 15/07/14 14:54:27 你要follow谁
    '''
    god_id = IntegerField()  # 实际上是你要follow的用户的id


class god(BaseModel):

    '''
    god 的信息 create by bigzhu at 16/05/24 10:01:39
    modify by bigzhu at 17/05/19 19:16:08 改为用 json 放社交信息
    '''
    name = TextField()  # 名字
    bio = TextField(null=True)  # 说明
    twitter = BinaryJSONField(null=True)  #
    github = BinaryJSONField(null=True)  #
    instagram = BinaryJSONField(null=True)  #
    tumblr = BinaryJSONField(null=True)  #
    facebook = BinaryJSONField(null=True)  #
    cat = TextField(null=True)  # 类别
    is_public = IntegerField(null=True, constraints=[SQL('DEFAULT 0')])  # 是不是可以看到的，如果是，那么cat不能改
    is_black = IntegerField(null=True, constraints=[SQL('DEFAULT 0')])  # 是否黑名单


class social_user(BaseModel):

    '''
    create by bigzhu at 16/03/26 05:45:33 社交帐号
    '''
    type = TextField()  # twitter or instagram or github
    name = TextField()
    count = IntegerField()  # 关注他的人数
    avatar = TextField(null=True)  # 发布者的头像
    description = TextField(null=True)  # 描述
    out_id = TextField(null=True)  # facebook要用这个来调api
    # 判断是否同步
    # instagram 已经取过的最后一个id
    # github etag
    # tumblr 时间戳
    sync_key = TextField(null=True)


class oauth_info(BaseModel):

    '''
    oauth_info 登录的用户信息
    '''
    out_id = TextField(null=True)  # 外部的id
    type = TextField()  # oauth 类型, twitter github
    name = TextField()
    avatar = TextField()  # 头像
    email = TextField(null=True)
    location = TextField(null=True)  # 归属地


class anki_save(BaseModel):

    '''
    标记是否发到anki
    '''
    message_id = IntegerField()


class anki(BaseModel):
    user_name = TextField()
    password = TextField()
    csrf_token = TextField(null=True)
    mid = TextField(null=True)
    cookie = TextField(null=True)


class block(BaseModel):
    god_id = IntegerField()


class apply_del(BaseModel):

    '''
    create by bigzhu at 16/08/19 10:39:42 申请删除没有用的社交帐号
    '''
    god_name = TextField()  # god name
    social_name = TextField()  # 社交帐号名
    type = TextField()  # 类别
    stat = IntegerField(null=True)  # 1 已删 0 不能删
    count = IntegerField(null=True, constraints=[SQL('DEFAULT 0')])  # 申请次数
    reason = TextField(null=True)  # 原因


class who_add_god(BaseModel):

    '''
    谁添加了哪个god
    '''
    god_id = IntegerField()
    cat = TextField()  # 类别


class remark(BaseModel):

    '''
    create by bigzhu at 16/06/06 10:37:47 给god添加备注
    '''
    god_id = IntegerField()
    remark = TextField()
    like = IntegerField(null=True)


class collect(BaseModel):

    '''
    收藏 create by bigzhu at 16/05/20 14:11:51
    '''
    message_id = IntegerField()


class wechat_dead_line(BaseModel):

    '''
    记录wechat的超时时间,以决定要不要新建
    modify by bigzhu at 15/09/13 17:49:27 加入对wechat_ext的支持
    '''
    jsapi_ticket = TextField(null=True)
    jsapi_ticket_expires_at = DateTimeField(null=True)
    access_token = TextField(null=True)
    access_token_expires_at = DateTimeField(null=True)
    token = TextField(null=True)
    cookies = TextField(null=True)


class wechat_user(BaseModel):

    '''
    create by bigzhu at 15/04/04 13:30:57 记录微信用户的信息
    '''

    subscribe = IntegerField()  # 用户是否订阅该公众号标识，值为0时，代表此用户没有关注该公众号，拉取不到其余信息。
    openid = TextField()  # 用户的标识，对当前公众号唯一
    nickname = TextField()  # 用户的昵称
    sex = IntegerField()  # 用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
    city = TextField()  # 用户所在城市
    country = TextField()  # 用户所在国家
    province = TextField()  # 用户所在省份
    language = TextField()  # 用户的语言，简体中文为zh_CN
    headimgurl = TextField(null=True)  # 用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
    subscribe_time = IntegerField()  # 用户关注时间，为时间戳。如果用户曾多次关注，则取最后关注时间
    unionid = TextField(null=True)  # 只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段。详见：获取用户个人信息（UnionID机制）
    remark = TextField()  # 不知道是什么
    groupid = IntegerField()  # 突然出现的
    user_name = TextField(null=True)  # 系统的用户名,用来绑定


class github_message(BaseModel):

    '''
    create by bigzhu at 15/07/15 17:57:00
    '''
    # id to id_str
    id_str = TextField(null=True)
    type = TextField(null=True)
    actor = IntegerField(null=True)  # trans to id
    repo = JSONField(null=True)
    payload = JSONField(null=True)
    public = BooleanField(null=True)
    created_at = DateTimeField(null=True)
    org = JSONField(null=True)
    content = BinaryJSONField(null=True)  # 整合的内容


class github_user(BaseModel):

    '''
    create by bigzhu at 15/07/15 18:02:15
    '''
    login = TextField(null=True)  # 用户名
    # id": 66433,
    avatar_url = TextField(null=True)  # 头像地址
    gravatar_id = TextField(null=True)
    # url = TextField(null=True) # api取用户信息的地址
    html_url = TextField(null=True)  # git项目地址
    # followers_url": "https://api.github.com/users/navy3/followers",
    # following_url": "https://api.github.com/users/navy3/following{/other_user}",
    # gists_url": "https://api.github.com/users/navy3/gists{/gist_id}",
    # starred_url": "https://api.github.com/users/navy3/starred{/owner}{/repo}",
    # subscriptions_url": "https://api.github.com/users/navy3/subscriptions",
    # organizations_url": "https://api.github.com/users/navy3/orgs",
    # repos_url": "https://api.github.com/users/navy3/repos",
    # events_url": "https://api.github.com/users/navy3/events{/privacy}",
    # received_events_url": "https://api.github.com/users/navy3/received_events",
    # type": "User",
    site_admin = BooleanField(null=True)
    name = TextField(null=True)
    company = TextField(null=True)
    blog = TextField(null=True)
    location = TextField(null=True)
    email = TextField(null=True)
    hireable = BooleanField(null=True)  # 被雇佣了么
    bio = TextField(null=True)  # 说明
    public_repos = IntegerField(null=True)  # 公开项目数
    public_gists = IntegerField(null=True)
    followers = IntegerField(null=True)
    following = IntegerField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)
    etag = TextField(null=True)


class last(BaseModel):

    '''
    记录上次看到的那条message
    create by bigzhu at 16/04/19 08:20:48 还是改为记录时间
    '''
    user_id = IntegerField()
    last_time = DateTimeField()
    # last_message_id = IntegerField()


class m(BaseModel):

    '''
    create by bigzhu at 15/12/09 15:33:04 直接存message
    '''
    id_str = TextField(null=True)  # 外部的id
    m_type = TextField()  # twitter or instagram or github
    m_user_id = TextField()  # 对应的社交帐号的user_id
    created_at = DateTimeField()
    content = BinaryJSONField(null=True)  # 带结构的内容github
    text = TextField(null=True)  # 文本内容
    extended_entities = BinaryJSONField(null=True)  # 扩展内容,图片什么
    href = TextField(null=True)  # message 的link
    type = TextField(null=True)  # media type


class user_info(model_bz.user_info):

    '''
    create by bigzhu at 15/08/19 09:27:08 增加18+
    '''
    porn = IntegerField()  # 1 荤的，0 素的
    tumblr = TextField()  # 汤不热


if __name__ == '__main__':
    # message.drop_table(True)
    message.create_table(True)
