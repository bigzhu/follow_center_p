require './style.less'

error = require '../../../spa/lib_bz/functions/error.coffee'
toast = require '../../../spa/lib_bz/functions/toast.coffee'
top_toast = toast.getTopRightToast()

url = require '../../../spa/lib_bz/functions/url.coffee'
module.exports =
  components:
    'follow':require '../follow'
    'simditor':require '../../../spa/lib_bz/components/simditor'
  directives:
    disable: require '../../../spa/lib_bz/directives/disable'
  template: require('./template.html')
  props: [ 'user_info', 'is_my' ]
  computed:
    avatar:->
      if @user_info.picture
        return @user_info.picture
      else
        return '/static/images/avatar.svg'
  ready:->
    error.setOnErrorVm(@)
    $(@$el).find('.button').popup inline: true
  data:->
    loading: false
    disable_edit: true # 禁止编辑
    button_text:'修改资料'
  methods:
    autoInsert:(key, scheme='http://')-> # 协议可以配置
      if not @user_info[key]
        Vue.set(@user_info, key, scheme)
        #@user_info.$set(key, scheme)
    changeImg:->
      $('#profile-image-upload').click()
    previewImg:(e)->
      file = e.target.files[0]
      if not file
        return
      if file.size > (10 * 1024 * 1024)
        throw new Error("图片大小只能小于10m哦~")
      reader = new FileReader()
      reader.onload = (e)->
        $("#profile-image-upload").attr("src", e.target.result)
      reader.readAsDataURL(file)
      @uploadImage()
    uploadImage:->
      fd = new FormData()
      file = $("#profile-image-upload")[0].files[0]
      if file
        fd.append("img", file)
        $.ajax
          url: '/upload_image'
          type: 'POST'
          data : fd
          processData: false
          contentType: false
          success: (data, status, response) =>
            #为了兼容 simditor 这里的返回值不太一样
            @loading=false
            if not data.success
              throw new Error(data.msg)
            else
              top_toast["info"] "保存成功"
              @user_info.picture = data.file_path
              $("#profile-image").attr("src", @user_info.picture)
          error: (error_info)->
            @loading=false
            throw new Error(error_info)
    save:->
      if @disable_edit
        @disable_edit = false
        $(@$el).find(".basic.button").html('<i class="icon save"></i>保存')
      else
        @loading=false
        @disable_edit=true
        $(@$el).find(".basic.button").html('<i class="icon file text"></i>编辑')
        parm = JSON.stringify
          user_name:@user_info.user_name
          blog:@user_info.blog
          twitter:@user_info.twitter
          github:@user_info.github
          instagram:@user_info.instagram
          slogan:@user_info.bio
          picture:@user_info.picture
        #如果url path不同,则向对应后台url发请求,以应对重载又要留着原本profile的情况(follow_center)
        path = url.getUrlPath(1)
        $.ajax
          url: '/add'
          type: 'POST'
          data : parm
          success: (data, status, response) =>
            if data.error != '0'
              throw new Error(data.error)
            else
              top_toast["info"] "保存成功"
              if @is_my #如果改的是自已的，那么要吧localstorage的内容也要update
                localStorage.user_info = JSON.stringify(@user_info)
