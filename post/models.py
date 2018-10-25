from django.db import models

from user.models import User


class Post(models.Model):
    uid = models.IntegerField()
    title = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()

    class Meta:
        ordering = ['-created']

    @property
    def auth(self):
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(pk=self.uid)
        return self._auth

    def comments(self):
        '''帖子对应的所有评论'''
        return Comment.objects.filter(post_id=self.id)

    def tags(self):
        '''帖子对应的所有标签'''
        relations = PostTagRelation.objects.filter(post_id=self.id).only('tag_id')
        tag_id_list = [r.tag_id for r in relations]
        return Tag.objects.filter(id__in=tag_id_list)

    def update_tags(self, tag_names):
        '''更新帖子对应的标签'''
        exist_tags = set(self.tags())                   # 当前对应的所有的 tag
        updated_tags = set(Tag.ensure_tags(tag_names))  # 更新完以后的所有对应的 tag

        # 处理新增关系
        new_tags = updated_tags - exist_tags
        need_create_tid_list = [t.id for t in new_tags]  # 需要建立关联的 tag id 列表
        PostTagRelation.add_relations(self.id, need_create_tid_list)

        # 处理需要删除的关系
        old_tags = exist_tags - updated_tags
        need_delete_tid_list = [t.id for t in old_tags]  # 需要删除关联的 tag id 列表
        PostTagRelation.del_relations(self.id, need_delete_tid_list)


class Comment(models.Model):
    uid = models.IntegerField()
    post_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    class Meta:
        ordering = ['-created']

    @property
    def auth(self):
        if not hasattr(self, '_auth'):
            self._auth = User.objects.get(pk=self.uid)
        return self._auth

    @property
    def post(self):
        if not hasattr(self, '_post'):
            self._post = Post.objects.get(pk=self.post_id)
        return self._post


class Tag(models.Model):
    name = models.CharField(max_length=16, unique=True)

    @classmethod
    def ensure_tags(cls, tag_names):
        '''确保传入的 Tag 已存在，如果不存在直接创建出来'''
        # 过滤出已存在的 tag name
        exist_tags = cls.objects.filter(name__in=tag_names)
        exist_names = {t.name for t in exist_tags}

        # 创建不存在的 Tag
        not_exist_names = set(tag_names) - exist_names  # 过滤出不存在的 tag name
        need_create_tags = [Tag(name=name) for name in not_exist_names]
        cls.objects.bulk_create(need_create_tags)

        return cls.objects.filter(name__in=tag_names)


class PostTagRelation(models.Model):
    '''
    帖子 - 标签 的关系表

        服务器部署      linux
        服务器部署      nginx
        服务器部署      web
        Django的中间件  web
        Django的中间件  django
        Django的中间件  python
        Python的黑魔法  python
        Python的黑魔法  metaclass
        Flask的蓝图     flask
        Flask的蓝图     web
        Flask的蓝图     python
    '''
    post_id = models.IntegerField()
    tag_id = models.IntegerField()

    @classmethod
    def add_relations(cls, post_id, tag_id_list):
        '''批量增加帖子和标签的关系'''
        need_create = [cls(post_id=post_id, tag_id=tid)
                       for tid in tag_id_list]
        cls.objects.bulk_create(need_create)

    @classmethod
    def del_relations(cls, post_id, tag_id_list):
        '''批量删除帖子和标签的关系'''
        cls.objects.filter(post_id=post_id, tag_id__in=tag_id_list).delete()
