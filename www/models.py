import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'
    user_id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    avatar = StringField(ddl='varchar(500)')
    admin = BooleanField()
    registerDate = FloatField(default=time.time)
    operateDate = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'
    blog_id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)
    updated_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'
    com_id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    content = TextField()
    created_at = FloatField(default=time.time)
    updated_at = FloatField(default=time.time)
