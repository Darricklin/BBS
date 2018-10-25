from math import ceil

from django.core.cache import cache
from django.shortcuts import render, redirect

from common import rds
from post.models import Post
from post.models import Comment
from post.models import Tag
from post.helper import page_cache
from post.helper import get_top_n
from user.helper import login_required
from user.helper import need_perm


@login_required
@need_perm('add_post')
def create_post(request):
    if request.method == 'POST':
        uid = request.session['uid']
        title = request.POST.get('title')
        content = request.POST.get('content')
        post = Post.objects.create(uid=uid, title=title, content=content)
        return redirect('/post/read/?post_id=%d' % post.id)
    else:
        return render(request, 'create_post.html')


@login_required
def edit_post(request):
    if request.method == 'POST':
        post_id = int(request.POST.get('post_id'))
        post = Post.objects.get(pk=post_id)

        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.save()

        str_tags = request.POST.get('tags')
        tag_names = [t.strip() for t in str_tags.title().replace('，', ',').split(',')]
        post.update_tags(tag_names)

        # 更新帖子缓存
        key = 'Post-%s' % post_id
        cache.set(key, post)
        print('缓存更新')
        return redirect('/post/read/?post_id=%d' % post.id)
    else:
        post_id = int(request.GET.get('post_id'))
        post = Post.objects.get(pk=post_id)
        str_tags = ', '.join([t.name for t in post.tags()])
        return render(request, 'edit_post.html', {'post': post, 'tags': str_tags})


def read_post(request):
    post_id = int(request.GET.get('post_id'))

    key = 'Post-%s' % post_id
    post = cache.get(key)
    print('从缓存获取：', post)
    if post is None:
        # 从数据库取出数据，并且添加到缓存里
        post = Post.objects.get(pk=post_id)
        cache.set(key, post)
        print('从数据库获取：', post)

    # 增加阅读计数
    rds.zincrby('ReadCounter', post_id)
    return render(request, 'read_post.html', {'post': post})


@login_required
@need_perm('del_post')
def delete_post(request):
    '''删除对象'''
    post_id = int(request.GET.get('post_id'))
    Post.objects.get(pk=post_id).delete()
    rds.zrem('ReadCounter', post_id)  # 同时删除排行数据
    return redirect('/')


@page_cache(5)
def post_list(request):
    page = int(request.GET.get('page', 1))  # 当前页码
    total = Post.objects.count()         # 帖子总数
    per_page = 10                        # 每页帖子数
    pages = ceil(total / per_page)       # 总页数

    start = (page - 1) * per_page  # 当前页开始的索引
    end = start + per_page         # 当前页结束的索引
    posts = Post.objects.all()[start:end]

    return render(request, 'post_list.html',
                  {'posts': posts, 'pages': range(pages)})


def search(request):
    keyword = request.POST.get('keyword')
    posts = Post.objects.filter(content__contains=keyword)
    return render(request, 'search.html', {'posts': posts})


def top10(request):
    # rank_data = [
    #     [Post(9), 100],
    #     [Post(5), 91],
    #     [Post(7), 79],
    # ]
    rank_data = get_top_n(10)
    return render(request, 'top10.html', {'rank_data': rank_data})


@login_required
def comment(request):
    uid = request.session['uid']
    post_id = int(request.POST.get('post_id'))
    content = request.POST.get('content')
    Comment.objects.create(uid=uid, post_id=post_id, content=content)
    return redirect('/post/read/?post_id=%s' % post_id)


@login_required
@need_perm('del_comment')
def del_comment(request):
    post_id = int(request.GET.get('post_id'))
    comment_id = int(request.GET.get('comment_id'))
    Comment.objects.get(pk=comment_id).delete()
    return redirect('/post/read/?post_id=%s' % post_id)


@login_required
@need_perm('del_user')
def del_user(request):
    return render(request, '')
