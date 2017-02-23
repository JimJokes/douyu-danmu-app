var vm = new Vue({
    el: '#exp',
    data: {
        table: location.pathname.split('/').pop(),
        items: [],
        page: null,
        has_previous: null,
        page_index: null,
        has_next: null,
        page_count: null,
        models: {
            'users': {'name': '名字', 'email': '邮箱'},
            'blogs': {'name': '标题', 'user_name': '作者'},
            'comments': {'user_name': '作者', 'content': '内容'},
        }
    },
    mounted:function(){
        this.get_item();
    },
    computed:{
        fields:function(){
            return this.models[this.table];
        },
    },
    methods: {
        get_item: function() {
            var self = this;
            getJSON('/api/2.0/'+this.table, {
                page: location.search.split('=')[1]
            }, function (err, data) {
                if (err) {
                    return fatal(err);
                }
            $('#loading').hide();
            self.items = data.items;
            self.page = data.page;
            self.page_index = data.page.page_index;
            self.has_previous = data.page.has_previous;
            self.has_next = data.page.has_next;
            self.page_count = data.page.page_count;
            $('#manage-table').show();
        });
        },
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