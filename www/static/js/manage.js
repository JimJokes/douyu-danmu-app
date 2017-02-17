function initVM(data) {
    $('#vm').show();
    var vm = new Vue({
        el: '#vm',
        data: {
            table: location.pathname.split('/').pop(),
            items: data.items,
            page: data.page,
            models: {
                'users': {'name': '名字', 'email': '邮箱'},
                'blogs': {'name': '标题', 'user_name': '作者'},
                'comments' {'user_name': '作者', 'content': '内容'},
            },
        },
        computed:{
            fields:function(){
                return this.models[this.table];
            }
        }
        method: {
            delete_item: function (item) {
                if(confirm('确定要删除“'+ item.name || item.content + '”？删除后不可恢复！')) {
                    postJSON('/api/' + this.table + '/' + item.id, function(err, r){
                        if (err){
                            return error(err);
                        }
                        refresh();
                    });
                }
            }
        }
    });
}
$(function() {
    getJSON('/api/'+ this.table,{
        page: {{ page.page_index }}
    }, function (err, results) {
        if (err) {
            return fatal(err);
        }
        $('#loading').hide();
        initVM(results);
    });
});