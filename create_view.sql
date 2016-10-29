insert into message (id, created_date, stat_date, god_id, user_name, 
       name, avatar, id_str, m_type, created_at, content, text, extended_entities, 
       href, type)

SELECT id, created_date, stat_date, god_id, user_name, 
       name, avatar, id_str, m_type, created_at, content, text, extended_entities, 
       href, type
  FROM messages_old;
------
drop MATERIALIZED VIEW messages;
 CREATE MATERIALIZED VIEW messages AS
 select * from (
     select
    m.created_date,
    m.stat_date,
    m.id_str,

         ui.id as god_id,
         ui.user_name,
         m.id,
         m.m_type,
         m.created_at,
         u.screen_name as name,
         u.profile_image_url_https as avatar,
         null as content,
         m.text,
         m.extended_entities,
         m.href,
         null as type
             from m, twitter_user u, user_info ui
             where m.m_type='twitter' 
             and m.m_user_id=u.id_str
             and lower(u.screen_name) = lower(ui.twitter)
         union
     select
    m.created_date,
    m.stat_date,
    m.id_str,
         ui.id as god_id,
         ui.user_name,
         m.id,
         m.m_type,
         m.created_at,
         u.login as name,
         u.avatar_url as avatar,
         m.content,
         null as text,
         null as extended_entities,
         null as href,
         null as type
             from m, github_user u, user_info ui
             where m.m_type='github' 
             and m.m_user_id=u.id::text
             and lower(u.login) = lower(ui.github)
         union
     select
    m.created_date,
    m.stat_date,
    m.id_str,
         ui.id as god_id,
         ui.user_name,
         m.id,
         m.m_type,
         m.created_at,
         u.username as name,
         u.profile_picture as avatar,
         m.content,
         m.text,
         m.extended_entities,
         m.href,
         m.type
             from m, instagram_user u, user_info ui
             where m.m_type='instagram' 
             and m.m_user_id=u.id_str
             and lower(u.username) = lower(ui.instagram)
         union
       select 
    m.created_date,
    m.stat_date,
    m.id_str,
         ui.id as god_id,
         ui.user_name,
         m.id,
         m.m_type,
         m.created_at,
         u.name,
         '' as avatar,
         null as content,
         m.text,
         m.extended_entities,
         m.href,
         m.type
         from m, tumblr_user u, user_info ui
         where m.m_type='tumblr' 
         and lower(m.m_user_id)=lower(u.name)
         and lower(u.name)=lower(ui.tumblr)
         
         ) as t order by created_at desc;

-----------------------------------------------------------------------------------------------------------------------------------------------------
drop MATERIALIZED VIEW messages;
 CREATE MATERIALIZED VIEW messages AS
 select * ,ROW_NUMBER() OVER(ORDER BY Id) row_num from (
     select
         ui.id as god_id,
         ui.user_name,
         m.id,
         'twitter' as m_type,
         m.created_at,
         u.screen_name as name,
         u.profile_image_url_https as avatar,
         null as content,
         m.text,
         m.extended_entities,
         'https://twitter.com/'||u.screen_name||'/status/'||m.id_str as href,
         null as type
             from twitter_message m, twitter_user u, user_info ui
             where m.t_user_id=u.id_str
             and lower(u.screen_name) = lower(ui.twitter)
         union
     select
         ui.id as god_id,
         ui.user_name,
         m.id,
         'github' as m_type,
         m.created_at,
         u.login as name,
         u.avatar_url as avatar,
         m.content,
         null as text,
         null as extended_entities,
         null as href,
         null as type
             from github_message m, github_user u, user_info ui
             where m.actor=u.id
             and lower(u.login) = lower(ui.github)
         union
     select
         ui.id as god_id,
         ui.user_name,
         m.id,
         'instagram' as m_type,
         m.created_time as created_at,
         u.username as name,
         u.profile_picture as avatar,
         m.comments as content,
         (m.caption->>'text')::text as text,
         m.standard_resolution as extended_entities,
         m.link as href,
         m.type as type
             from instagram_media m, instagram_user u, user_info ui
             where m.user_id_str=u.id_str
             and lower(u.username) = lower(ui.instagram)
         union
       select 
         ui.id as god_id,
         ui.user_name,
         m.id,
         'tumblr' as m_type,
         m.created_date as created_at,
         u.name,
         '' as avatar,
         null as content,
         m.caption as text,
         m.photos as extended_entities,
         m.short_url as href,
         m.type as type
         from tumblr_blog m, tumblr_user u, user_info ui
         where lower(m.user_name)=lower(u.name)
         and lower(u.name)=lower(ui.tumblr)
         
         ) as t order by created_at desc;

drop VIEW god_info;
 CREATE VIEW god_info AS
    select u.*, COALESCE(NULLIF(u.slogan,''), NULLIF(tw.description,''), NULLIF(i.bio,''), NULLIF(g.bio,''), NULLIF(tu.description,'')) as bio from user_info u 
    LEFT OUTER JOIN twitter_user tw 
    	ON u.user_name = tw.screen_name
    LEFT OUTER JOIN instagram_user i 
    	ON u.user_name = i.username
    LEFT OUTER JOIN github_user g 
    	ON u.user_name = g.login	
    LEFT OUTER JOIN tumblr_user tu
    	ON u.user_name = tu.name


drop VIEW all_message;
 CREATE VIEW all_message AS
select m.*, s.avatar from message m, social_user s
where m.user_name = s.name
and m.m_type = s.type
