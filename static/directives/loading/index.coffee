require './style.less'
module.exports =
  bind: ->
  update: (new_value, old_value) ->
    target = "body"
    color = "#040000"
    if  @vm.$data.loading_target
      target = @vm.$data.loading_target
    if @arg
      color = @arg
    html = require('./template.html')
    if new_value
      $(target).append html
    else
      $(target).find('.highwe-loading').remove()
    return
  unbind: ->
