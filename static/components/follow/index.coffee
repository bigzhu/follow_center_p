#require './style.less'

toast = require '../../../spa/lib_bz/functions/toast.coffee'
top_toast = toast.getTopRightToast()

module.exports =
  template: require('./template.html')
  props: [ 'followed', 'god_id']
  data:->
    btn_loading:false
  ready:->
    @$watch 'followed',->
      if @followed == 1
        @showFollow()
      else
        @showUnfollow()
    if @followed == 1
      @showFollow()
    else
      @showUnfollow()
  methods:
    showFollow:->
      target = @$el
      $(target).text('Following')
      $(target).removeClass('basic').addClass('orange')
    showUnfollow:->
      target = @$el
      $(target).html('<i class="add icon"></i>Follow ')
      $(target).removeClass('orange').addClass('basic')
    toggleFollow:->
      if @btn_loading
        return
      @btn_loading = true
      target = @$el
      if @followed == 1
        @showUnfollow()
        @followed = 0
        parm = JSON.stringify
          god_id:@god_id
        $.ajax
          url: '/unfollow'
          type: 'POST'
          data : parm
          success: (data, status, response) =>
            @btn_loading=false
            if data.error != '0'
              throw new Error(data.error)
            else
              top_toast.info "Unfollow 成功"
      else
        @showFollow()
        @followed = 1
        parm = JSON.stringify
          god_id:@god_id
        $.ajax
          url: '/follow'
          type: 'POST'
          data : parm
          success: (data, status, response) =>
            @btn_loading=false
            if data.error != '0'
              #如果是要登录,那么跳转到登录
              if data.error == 'must login'
                window.location.href = "/login"
              else
                throw new Error(data.error)
            else
              top_toast.info "Follow 成功"
  directives:
    'btn-loading': require('../../../spa/lib_bz/directives/btn-place-loading')
