#require './app.less'
Vue = require './vue_local.coffee'
error = require 'lib/functions/error.coffee'
v_login_messages = new Vue
  created:->
    error.setOnErrorVm(@)
  data:->
    oauths:[
      {
        'name':'twitter'
        'show_name':'Twitter'
      }
      {
        'name':'github'
        'show_name':'GitHub'
      }
      {
        'name':'douban'
        'show_name':'豆瓣'
      }
    ]
  el:'#login_messages'
  components:
    'main-login': require('lib/components/main-login'),
    'messages': require('./components/messages'),
