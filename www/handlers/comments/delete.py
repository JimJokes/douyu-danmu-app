from apis import APIResourceNotFoundError
from coroweb import post
from models import Comment
from utils import check_admin


@post('/api/comment/{com_id}/delete')
async def api_delete_comment(request, *, com_id):
    check_admin(request)
    comment = await Comment.find(com_id)
    if comment is None:
        raise APIResourceNotFoundError('Comment')
    await comment.remove()
    return dict(com_id=com_id)
