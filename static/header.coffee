require './header.less'
Vue = require './vue_local.coffee'

error = require 'lib/functions/error.coffee'
user_info = require 'lib/functions/user_info.coffee'
v_header = new Vue
  ready:->
    error.setOnErrorVm(@)
    @is_login = user_info.isLogin()
  data:->
    is_login:false
    search_value:''
  el:'#v_header'
  methods:
    search:->
      # 如果定义了 header_search 方法, 就不用默认的 google search 了
      #e.preventDefault()
      #if window.header_search
      #  window.header_search(@search_value)
      #  return
      host = window.location.hostname
      url = "https://www.google.com/search?q=site:"+host+" "+@search_value+"&gws_rd=ssl"
      window.open(url)
