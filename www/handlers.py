' url handlers '

import json, logging, hashlib

import time
from aiohttp import web

from coroweb import get, post
from apis import APIValueError, APIResourceNotFoundError, APIPermissionError, APIError

from models import User, Blog, Comment, next_id
from utils import get_page_index, user2cookie, COOKIE_NAME, RE_EMAIL, RE_SHA1, check_admin, Page


@get('/')
async def index(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(blog_id)')
    page = Page(num, page_index=page_index)
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.findAll(orderBy='blog_created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'blogs.html',
        'page': page,
        'blogs': blogs
    }


@get('/blog/{blog_id}')
async def get_blog(blog_id):
    blog = await Blog.find(blog_id)
    comments = await Comment.findAll('blog_id=?', [blog_id], orderBy='com_created_at desc')
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.user_id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.password = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@get('/manage/')
def manage():
    return 'redirect:/manage/comments'


@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'blog_id': '',
        'action': '/api/blog/create'
    }


@get('/blogs/edit')
def manage_edit_blog(*, blog_id):
    return {
        '__template__': 'manage_blog_edit.html',
        'blog_id': blog_id,
        'action': 'api/blogs/%s' % blog_id
    }


@post('/api/blogs/{blog_id}/comments')
async def api_create_comment(blog_id, request, *, comContent):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not comContent or not comContent.strip():
        raise APIValueError('content')
    blog = await Blog.find(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.blog_id, user_id=user.user_id, comContent=comContent.strip())
    await comment.save()
    return comment


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(user_id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/blogs/{blog_id}')
async def api_get_blog(*, blog_id):
    blog = await Blog.find(blog_id)
    return blog


@post('/api/blog/create')
async def api_create_blog(request, *, title, summary, blogContent):
    check_admin(request)
    if not title or not title.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not blogContent or not blogContent.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.user_id, title=title.strip(), summary=summary.strip(), blogContent=blogContent.strip())
    await blog.save()
    return blog


@post('/api/blogs/{blog_id}')
async def api_update_blog(blog_id, request, *, title, summary, blogContent):
    check_admin(request)
    blog = await Blog.find(blog_id)
    if not title or not title.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not blogContent or not blogContent.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.title = title.strip()
    blog.summary = summary.strip()
    blog.blogContent = blogContent.strip()
    blog.blog_updated_at = time.time()
    await blog.update()
    return blog


@get('/manage/{table}')
async def manage_table(table, *, page='1'):
    page_index = get_page_index(page)
    modules = {'users': User, 'blogs': Blog, 'comments': Comment}
    num = await modules[table].findNumber('count(id)')
    page = Page(num, page_index=page_index)
    if num == 0:
        items = []
    else:
        items = await modules[table].findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'manage.html',
        'page': page,
        'items': items
    }


@post('/api/{table}/{id}/delete')
async def api_delete_item(request, *, table, id):
    check_admin(request)
    modules = {'users': User, 'blogs': Blog, 'comments': Comment}
    item = await modules[table].find(id)
    await item.remove()
    return dict(id=id)


@get('/api/{table}')
async def api_table(table, *, page='1'):
    modules = {'users': User, 'blogs': Blog, 'comments': Comment}
    page_index = get_page_index(page)
    num = await modules[table].findNumber('count(id)')
    page = Page(num, page_index=page_index)
    if num == 0:
        return dict(page=page, items=())
    else:
        items = await modules[table].findAll(orderBy='created_at desc', limit=(page.offset, page.limit))
        if table == 'users':
            for item in items:
                item.passwd = '******'
        return dict(page=page, items=items)
