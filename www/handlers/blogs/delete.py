from apis import APIResourceNotFoundError
from coroweb import post
from models import Blog
from utils import check_admin


@post('/api/blog/{blog_id}/delete')
async def api_delete_blog(request, *, blog_id):
    check_admin(request)
    blog = await Blog.find(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    await blog.remove()
    return dict(blog_id=blog_id)
