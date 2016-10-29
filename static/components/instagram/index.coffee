compute = require '../../../spa/lib_bz/functions/compute.coffee'
module.exports =
  template: require('./template.html')
  props: [ 'message' ]
  computed:
    img_url:->
      img_url = btoa(btoa(@message.extended_entities.url))
      return '/api_sp/'+img_url
    height:->
      #max_width = $(@$el).width() #没有办法取到，因为还没有渲染出来
      img_height = @message.extended_entities.height
      img_width = @message.extended_entities.width
      real_height = compute.getFitHeightForSemantic(img_height, img_width)
      return real_height
