compute = require '../../../spa/lib_bz/functions/compute.coffee'

#url = require '../../../spa/lib_bz/functions/url.coffee'
#String.prototype['autoLink'] = url.autoLink

module.exports =
  template: require('./template.html')
  props: [ 'message' ]
  computed:#v-attr只接收变量,为了用proxy,这里要处理
    avatar:->
      url = "https://api.tumblr.com/v2/blog/#{@message.name}.tumblr.com/avatar/512"
      return url
    medias:->
      if @message.extended_entities
        return _.map(@message.extended_entities, (d)->
          img_url = '/api_sp/'+btoa(btoa(d.original_size.url))
          img_url = d.original_size.url
          img_height = d.original_size.height
          img_width = d.original_size.width
          caption = d.caption

          height = compute.getFitHeightForSemantic(img_height, img_width)

          t =
            img_url: img_url
            height: height
            caption: caption
          return t
          )
    text:->
      if @message.text != null
        #return @message.text.autoLink({ target: "_blank", rel: "外部链接,请谨慎打开"})
        return @message.text
