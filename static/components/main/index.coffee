require './style.less'
f_user_info = require '../../../spa/lib_bz/functions/user_info'

module.exports =
  route:
  #  activate:(transition)->
    deactivate:(transition)-> #为了解除 scroll 的事件监听
      $(window).off("scroll")
      transition.next()
  data:->
    user_info:null
  created:->
    #为了把this传进去
    f_user_info.checkNewUserInfo.call(@)
    #if localStorage.user_info
    #  JSON.parse(localStorage.user_info)
    #  @user_info=JSON.parse(localStorage.user_info)
  template: require('./template.html')
  components:
    'messages': require('../messages'),
    'user_info': require('../user_info'),
    'god_list': require('../god_list'),
    'add_god': require('../add_god'),
