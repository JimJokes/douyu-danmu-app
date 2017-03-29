from apis import APIPermissionError, APIValueError, APIResourceNotFoundError
from coroweb import post
from models import Blog, Comment


@post('/api/blog/{blog_id}/comment')
async def api_create_comment(blog_id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = await Blog.find(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.blog_id, user_id=user.user_id, content=content.strip())
    await comment.save()
    return comment
