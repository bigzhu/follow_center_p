require './style.less'

random = require '../../../spa/lib_bz/functions/random.coffee'
module.exports =
  components:
    'message': require('../message'),
  directives:
    'btn-loading': require('../../../spa/lib_bz/directives/btn-place-loading'),
  props: ['god_name']
  data:->
    filter_pic:false #是否要过滤出图片
    new_loading:false
    old_loading:false
    error_info:''
    messages:[]
    last_message:null
    cache_messages:[]
    info_header:''
    info:''
    show_info: false
  computed:
    #cache_messages:
    #  get:->
    #    if localStorage.cache_messages
    #      if JSON.parse(localStorage.cache_messages).length > 1000
    #        return []
    #      return JSON.parse(localStorage.cache_messages)
    #    else
    #      return []
    #  set:(values)->
    #    localStorage.cache_messages = JSON.stringify(values)
    last_message_id:
      get:->
        if localStorage.last_message_id
          return parseInt(localStorage.last_message_id)
        else
          return 0
      set:(value)->
        localStorage.last_message_id = value
  ready:->
    @bindScroll()
    @messages = @filterMessages(@cache_messages)
    @new()
  template: require('./template.html')
  methods:
    showNotFollowedAnyOne:->
      @info_header = "还未关注任何人呢!"
      @info = "随机列了一些消息，鼠标放到头像上来关注。"
      @show_info=true
    showNotHaveNew:->
      @info_header='消息全被你读完啦，厉害!'
      @info='点击按钮看看历史消息？'
      @show_info=true
    filterMessages:(in_messages)-> #过滤 messages
      messages = _.clone(in_messages)
      if @filter_pic #过滤图片
        messages = _.filter(messages,(d)->
          return d.extended_entities
        )
      if @god_name
        god_name= @god_name
        messages = _.filter(messages,(d)->
          return d.user_name.toUpperCase()==god_name.toUpperCase()
        )
      return messages
    toggleFilterPic:->
      if not @filter_pic
        @filter_pic = true
      else
        @filter_pic = false
      @messages = @filterMessages(@cache_messages)
    new:->
      if @new_loading
        return
      @new_loading=true
      if @god_name
        url='/god'
        parm = JSON.stringify
          god_name:@god_name
          limit:10
      else
        url='/api_new'
        parm = ''
      $.ajax
        url: url
        data : parm
        type: 'POST'
        success: (data, status, response) =>
          if data.info == 'not followed any one'
            @showNotFollowedAnyOne()
          if data.messages.length != 0
            cache_messages = _.uniq @cache_messages.concat(data.messages.reverse()), false, (item, key, a) ->
              item.id
            @messages = @filterMessages(cache_messages)
            @cache_messages = cache_messages

            if @god_name or @filter_pic #如果只看某人或者只看图，就不要设unread了
              null
            else
              @setTitleUnreadCount(data.messages.length)
          else
            if @messages.length == 0
              @showNotHaveNew()
            #没数据，取老的
            #if @messages.length == 0
            #  @old(true)
            #else
            #  #位置向上动一点，以便于还可以下拉更新
            #console.log 'scrollAnimate -100'
            _.delay(@scrollAnimate, 500, 500, '-=100')
          @new_loading=false
    scrollAnimate:(time, len)->
      $('html, body').animate({
          scrollTop: "#{len}"
       }, time)
      #_.delay(window.scrollBy, 500, 0, -100)
    scrollToLast:->
      id = "#id_#{@last_message_id}"
      #console.log $(id)

      if $(id).length == 1
        #console.log "scrollToLast #{id}"
        @scrollTo($(id))
        #console.log "scroll to #{id}"
    old:()->
      @show_info = false
      if @old_loading
        return
      @old_loading = true
      if @god_name
        url = '/god'
        parm = JSON.stringify
          offset:@cache_messages.length
          god_name:@god_name
      else
        url = '/old'
        parm = JSON.stringify
          offset:@cache_messages.length
      @old_loading=true
      $.ajax
        url: url
        type: 'POST'
        data : parm
        success: (data, status, response) =>
          cache_messages = _.uniq data.messages.reverse().concat(@cache_messages), false, (item, key, a) ->
            item.id
          @messages = @filterMessages(cache_messages)
          @cache_messages = cache_messages
          @old_loading=false
          #定位到上次那条
          el = @getLastMessageEl()
          if el != null
            _.delay(@scrollTo, 500, el, -50)
          else
            #初始一条都没有，直接拉到最下面就可以了
            _.delay(@scrolltoBottom, 500)
    scrolltoBottom:->
      y = $(document).height() - $(window).height() #减去屏幕高度
      y -= 100 #减少100，避免加载new
      window.scrollTo(0, y)
    getLastMessageEl:->
      if @$refs.c_messages.length != 0
        el = @$refs.c_messages[0].$el
      else
        el = null
      return el
    scrollTo:(target, offset=0)-># 定位到这个target, offset偏移量 
      y = $(target).offset().top
      y = y+ offset
      window.scrollTo(0, y)
    setTitleUnreadCount:(count)->#设置未读的条目数
      @unreadCount = count
      if count == 0
        document.title = "Follow Center"
      else
        document.title = "(#{count}) Follow Center"
    getUnreadCount:(message)->
      index = _.findIndex(@messages, (d)=>
               return d.id == message.id
             )
      return @messages.length-index-1
    saveLast:(last_message)->
      message_id = parseInt(last_message.id)
      if @filter_pic #单看图时不要记
        return
      if @last_message_id > message_id
        return
      @last_message_id = message_id

      parm = JSON.stringify
        last_message_id:message_id
      $.ajax
        url: '/api_save_last'
        type: 'POST'
        data : parm
        success: (data, status, response) =>
          #存储在本地，用来比较
          @last_message = last_message
          #改变message的颜色，标记为已读
          color = random.color()
          $('#id_'+message_id).addClass(color)
          if data.count == 1
            count = @getUnreadCount(last_message)
            @setTitleUnreadCount(count)
    bindScroll:->
      v = @
      messages_element = $(v.$el.parentElement)

      #messages_element = $(v.$el)
      top = messages_element.offset().top + 14#
      #main_container_margin = 12*3
      #top=top+main_container_margin
      

      $(window).scroll ->
        ##选出当前正在看的message
        messages_element.children('.ui.fluid.card').each ->
          #拉到上方再标记已读
          message_position = $(this).offset().top#message所在高度
          scroll_bottom = $(window).scrollTop() + $(window).height() #scroll bottom 露出来的高度

          #降低精度，以保证==能触发出发
          message_position = parseInt(message_position/50)
          scroll_bottom = parseInt(scroll_bottom/50)
          if message_position == scroll_bottom
            #从jquery对像又取到 vue 对象
            message = $(this)[0].__vue__.message
            #console.log message
            v.saveLast(message)
            return false


        #console.log "messages_element.height() + top=#{messages_element.height() + top}"
        #console.log "- $(this).scrollTop() - $(this).height()=#{- $(this).scrollTop() - $(this).height()}"

        if $(@).scrollTop() == 0 #滚动到最上面时，加载历史内容(不要这个了)
          null
        if messages_element.height() + top == $(this).scrollTop() + $(this).height() #当滚动到最底部时，加载最新内容
        #else if $(@).scrollTop() + $(@).height() == $(document).height()
          console.log 'to the bottom,call new'
          v.new()
          return

        
        #可能gods会比message长
        #sementic ui 里 messages_element 的 height 会被 gods 给撑开
        #只有找最后一个message
        bottom_message = $(messages_element).find(".ui.fluid.card").last()
        bottom_message_top = 0
        if bottom_message.offset()
          #bottom_message_top = Math.ceil((bottom_message.offset().top + bottom_message.height())/10)
          bottom_message_top = bottom_message.offset().top + bottom_message.height()
        #scroll_top = Math.ceil(($(this).scrollTop() + $(this).height()) /10)
        scroll_top = $(this).scrollTop() + $(this).height()

        if bottom_message_top != 0 and bottom_message_top<=scroll_top
          console.log 'short message to the bottom,call new'
          v.new()


