module.exports =
  template: require('./template.html')
  props: [ 'message']
  computed:
    repo_url:->
      repo_url = @message.content.repo.url.replace('api.github.com/repos', 'github.com')
      return repo_url
    repo_name:->
      return @message.content.repo.name
    repo_link:->
      repo_link = "<a href='#{@repo_url}' target='_blank'>#{@repo_name}</a>"
      return repo_link
    type:->
      return @message.content.type
    payload:->
      return @message.content.payload
    action:->
      return @payload.action
    commits:->
      return @payload.commits
    issue:->
      if _.has(@payload, 'issue')
        return @payload.issue
    issue_link:->
      if @issue
        issue_link = "<a target='_blank' href='#{@issue.html_url}' >#{@issue.title}</a>"
        return issue_link
    issue_content:->
      content = ''
      if @action
        content = "#{@action} #{@issue_link}"
        return content
    issue_comment_link:->
      if @issue
        if not @payload.comment
          return
        issue_comment_url = @payload.comment.html_url
        issue_comment_link = "<a target='_blank' href='#{issue_comment_url}' >#{@issue.title}</a>"
        return issue_comment_link
    issue_comment_body:->
      if _.has(@payload, 'comment')
        return @payload['comment']['body']
