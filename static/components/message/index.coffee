require './style.less'
#require '../user_info/style.less'
#compute = require '../../../spa/lib_bz/functions/compute.coffee'
url = require '../../../spa/lib_bz/functions/url.coffee'
String.prototype['autoLink'] = url.autoLink

module.exports =
  components:
    'god':require '../god2'
    'twitter': require('../twitter'),
    'github': require('../github'),
    'instagram': require('../instagram'),
    'tumblr': require('../tumblr'),
  directives:
    'time-len':require '../../../spa/lib_bz/directives/time-len'
  data:->
    god:
      user_name:''
      bio:''
  attached:->
    tool_tips_target = $(@$el).find('.show-god-info')
    popup_content = $(@$el).find('.ui.popup')
    #$(tool_tips_target).popup popup: $(popup_content)
    $(tool_tips_target).popup
      popup: $(popup_content)
      lastResort: true #能不能放下都显示
      position : 'bottom left'
      hoverable: true
      delay:
        show: 100
        hide: 500
      onShow:=>
        @getGodInfo()
    #tool_tips_target = $(@$el).find('.show-god-info')
    #$(tool_tips_target).qtip(
    #  content:
    #    text:(event, api)=>
    #      parm = JSON.stringify
    #        god_name: @message.user_name
    #      $.ajax
    #        url: '/god_info'
    #        type: 'POST'
    #        data : parm
    #        success: (data, status, response) =>
    #          @god = data.god_info
    #          api.set('content.text', $(@$el).find('.god-info'))
    #      return "<i class='fa fa-spin fa-spinner'></i> Loading..." # Set some initial text
    #  hide:
    #     fixed: true
    #     delay: 300
    #  style:
    #    classes:'qtip-light'
    #  position:
    #    my: 'top left',
    #    at: 'bottom right'
    #)
  template: require('./template.html')
  props: [ 'message']
  computed:#v-attr只接收变量,为了用proxy,这里要处理
    avatar:->
      if @message.m_type=='tumblr'
        url = "https://api.tumblr.com/v2/blog/#{@message.name}.tumblr.com/avatar/512"
        return url
      avatar = btoa(btoa(@message.avatar))
      return '/api_sp/'+avatar
  methods:
    getGodInfo:->
      if @god.user_name != ''
        return
      parm = JSON.stringify
        god_name: @message.user_name
      $.ajax
        url: '/god_info'
        type: 'POST'
        data : parm
        success: (data, status, response) =>
          @god = data.god_info

