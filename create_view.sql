

drop VIEW all_message;
 CREATE VIEW all_message AS


 SELECT m.id,
    m.user_id,
    m.god_id,
    m.god_name,
    m.name,
    m.id_str,
    m.m_type,
    m.created_at,
    m.content,
    m.text,
    m.extended_entities,
    m.href,
    m.type,
    g.cat,
    case 
        when m.m_type = 'twitter' then g.twitter-> 'avatar'
        when m.m_type = 'github' then g.github-> 'avatar'
        when m.m_type = 'instagram' then g.instagram-> 'avatar'
        when m.m_type = 'tumblr' then g.tumblr-> 'avatar'
        when m.m_type = 'facebook' then g.tumblr-> 'facebook'
    end as avatar
   FROM message m,
    god g
  WHERE m.god_name = g.name
  
  
 



