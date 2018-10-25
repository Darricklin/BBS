from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password

from user.forms import RegisterForm
from user.models import User
from user.helper import get_wb_access_token
from user.helper import wb_user_show
from post.helper import page_cache
from user.helper import login_required


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)
            user.save()
            return redirect('/user/login/')
        else:
            return render(request, 'register.html', {'error': form.errors})
    else:
        return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname').strip()
        password = request.POST.get('password').strip()
        # 检查用户是否存在
        try:
            user = User.objects.get(nickname=nickname)
        except User.DoesNotExist:
            return render(request, 'login.html',
                          {'error': '用户不存在', 'auth_url': settings.WB_AUTH_URL})
        # 检查密码是否正确
        if check_password(password, user.password):
            request.session['uid'] = user.id
            request.session['nickname'] = user.nickname
            request.session['avatar'] = user.avatar
            return redirect('/user/info/')
        else:
            return render(request, 'login.html',
                          {'error': '密码错误', 'auth_url': settings.WB_AUTH_URL})
    else:
        return render(request, 'login.html', {'auth_url': settings.WB_AUTH_URL})


def logout(request):
    request.session.flush()
    return redirect('/')

@login_required
@page_cache(20)
def user_info(request):
    uid = request.session.get('uid')
    user = User.objects.get(pk=uid)
    return render(request, 'user_info.html', {'user': user})


def weibo_callback(request):
    '''微博回调接口'''
    code = request.GET.get('code')

    # 获取 access_token
    access_token, wb_uid = get_wb_access_token(code)
    if access_token is None:
        return render(request, 'login.html',
                      {'error': '微博 Token 接口错误', 'auth_url': settings.WB_AUTH_URL})

    # 获取微博的用户数据
    screen_name, avatar = wb_user_show(access_token, wb_uid)
    if screen_name is None:
        return render(request, 'login.html',
                      {'error': '微博 User 接口错误', 'auth_url': settings.WB_AUTH_URL})

    # 利用微博的账号，在论坛内进行登陆、注册
    nickname = '%s_wb' % screen_name
    user, is_created = User.objects.get_or_create(nickname=nickname)
    user.plt_icon = avatar
    user.save()

    # 记录用户状态
    request.session['uid'] = user.id
    request.session['nickname'] = user.nickname
    request.session['avatar'] = user.avatar

    return redirect('/user/info/')
