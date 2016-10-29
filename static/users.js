(function() {
  $(function() {
    var v_users;
    return v_users = new Vue({
      created: function() {
        return bz.setOnErrorVm(this);
      },
      el: '#v_users'
    });
  });

}).call(this);
