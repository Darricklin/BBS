r'''
用户
    \
    多对多
    /
角色
    \
    多对多
    /
权限
'''

from django.db import models


class User(models.Model):
    SEX = (
        ('M', '男性'),
        ('F', '女性'),
        ('S', '保密'),
    )

    nickname = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=128)
    age = models.IntegerField(default=18)
    sex = models.CharField(max_length=8, choices=SEX)
    icon = models.ImageField()
    plt_icon = models.URLField(default='', verbose_name='第三方平台的头像 URL')

    @property
    def avatar(self):
        '''统一的头像地址'''
        return self.plt_icon if self.plt_icon else self.icon.url

    def roles(self):
        '''当前用户具有的所有角色'''
        relations = UserRoleRelation.objects.filter(uid=self.id).only('role_id')
        role_id_list = [r.role_id for r in relations]
        return Role.objects.filter(id__in=role_id_list)

    def has_perm(self, perm_name):
        '''检查是否具有某权限'''
        for role in self.roles():
            for perm in role.perms():
                if perm.name == perm_name:
                    return True
        return False


class UserRoleRelation(models.Model):
    '''用户和角色的关系表'''
    uid = models.IntegerField()
    role_id = models.IntegerField()

    @classmethod
    def add_role_for_user(cls, uid, role_id):
        cls.objects.create(uid=uid, role_id=role_id)

    @classmethod
    def del_role_from_user(cls, uid, role_id):
        cls.objects.get(uid=uid, role_id=role_id).delete()


class Role(models.Model):
    '''
    角色表

        admin   超级管理员
        manager 管理员
        user    普通用户
    '''
    name = models.CharField(max_length=16, unique=True)

    def perms(self):
        '''当前角色具有的所有权限'''
        relations = RolePermRelation.objects.filter(role_id=self.id).only('perm_id')
        perm_id_list = [r.perm_id for r in relations]
        return Permission.objects.filter(id__in=perm_id_list)


class RolePermRelation(models.Model):
    '''角色和权限的关系表'''
    role_id = models.IntegerField()
    perm_id = models.IntegerField()

    @classmethod
    def add_perm_for_role(cls, role_id, perm_id):
        cls.objects.create(role_id=role_id, perm_id=perm_id)

    @classmethod
    def del_perm_from_role(cls, role_id, perm_id):
        cls.objects.get(role_id=role_id, perm_id=perm_id).delete()


class Permission(models.Model):
    '''
    权限表

        add_post    添加帖子
        add_comment 添加评论
        add_manager 添加管理员
        del_post    删除帖子
        del_comment 删除评论
        del_manager 删除管理员
        del_user    删除用户
    '''
    name = models.CharField(max_length=16, unique=True)
