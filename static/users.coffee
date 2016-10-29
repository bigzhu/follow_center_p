Vue = require './vue_local.coffee'
v_users = new Vue
  created:->
    bz.setOnErrorVm(@)
  el:'#v_users'
