module.exports =
  route:
  #  activate:(transition)->
    deactivate:(transition)-> #为了解除 scroll 的事件监听
      $(window).off("scroll")
      transition.next()
  data:->
    user_info:''
  created:->
    @getUserInfo(@$route.params.god_name)
  template: require('./template.html')
  components:
    'messages': require('../messages'),
    'user_info': require('../user_info'),
    'add_god': require('../add_god'),
  methods:
    getUserInfo:(user_name)->
      parm = JSON.stringify
        user_name:user_name
      $.ajax
        url: '/user_info'
        type: 'POST'
        data : parm
        success: (data, status, response) =>
          @user_info = data.user_info
