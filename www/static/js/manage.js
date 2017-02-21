function initVM(data, table) {
    $('#manage-table').show();
    var vm = new Vue({
        el: '#exp',
        data: {
            table: table,
            items: data.items,
            page: data.page,
            models: {
                'users': {'name': '名字', 'email': '邮箱'},
                'blogs': {'name': '标题', 'user_name': '作者'},
                'comments': {'user_name': '作者', 'content': '内容'},
            }
        },
        computed:{
            fields:function(){
                return this.models[this.table];
            },
        },
        methods: {
            delete_item: function (item) {
                if(confirm('确定要删除“'+ (item.name || item.content) + '”？删除后不可恢复！')) {
                    postJSON('/api/2.0/' + this.table + '/' + item.id + 'delete', function(err, r){
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
    var table = location.pathname.split('/').pop();
    getJSON('/api/2.0/'+table, {
        page: {{ page.page_index }}
    }, function (err, results) {
        if (err) {
            return fatal(err);
        }
        $('#loading').hide();
        initVM(results, table);
    });
});
