from apis import APIValueError
from coroweb import post, get
from models import Blog
from utils import check_admin


@get('/manage/blog/create')
async def create_blog():
    return {
        '__templating__': 'manage_blog_edit.html',
        'blog_id': '',
        'action': '/api/blog/create'
    }


@post('/api/blog/create')
async def api_create_blog(request, *, title, summary, content):
    check_admin(request)
    if not title or not title.trip():
        raise APIValueError('title', 'title cannot be empty.')
    if not summary or not summary.trip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.trip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.user_id, title=title.trip(), summary=summary.trip(), content=content.trip())
    await Blog.save()
    return blog
