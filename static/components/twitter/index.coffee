require './style.less'
compute = require '../../../spa/lib_bz/functions/compute.coffee'
#url = require '../../../spa/lib_bz/functions/url.coffee'
#String.prototype['autoLink'] = url.autoLink

module.exports =
  template: require('./template.html')
  props: [ 'message' ]
  data:->
    show_follow:false
  computed:
    medias:->
      if @message.extended_entities
        return _.map(@message.extended_entities.media, (d)->
          img_url = '/api_sp/'+btoa(btoa(d.media_url_https))
          #img_height = d.sizes.large.h
          #img_width = d.sizes.large.w
          
          #twitter  的large是骗人的
          img_height = d.sizes.medium.h
          img_width = d.sizes.medium.w

          height = compute.getFitHeightForSemantic(img_height, img_width)
          #console.log height
          #console.log img_height
          if height > img_height #如果高度足够，就用原始大小
            height = img_height

          t =
            img_url: img_url
            height: height
          return t
          )
    text:->
      # return @message.text.autoLink({ target: "_blank", rel: "外部链接,请谨慎打开"})
      return @message.text
