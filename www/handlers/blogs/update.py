import time

from apis import APIValueError
from coroweb import get, post
from models import Blog
from utils import check_admin


@get('/manage/blog/edit')
async def edit_blog(*, blog_id):
    return {
        '__templating__': 'manage_blog_edit.html',
        'blog_id': blog_id,
        'action': '/api/blog/update/%s' % blog_id
    }


@post('/api/blog/update/{blog_id}')
async def api_update_blog(blog_id, request, *, title, summary, content):
    check_admin(request)
    blog = await Blog.find(blog_id)
    if not title or not title.trip():
        raise APIValueError('title', 'title cannot be empty.')
    if not summary or not summary.trip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.trip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.title = title.trip()
    blog.summary = summary.trip()
    blog.content = content.trip()
    blog.updated_at = time.time()
    await blog.update()
    return blog
