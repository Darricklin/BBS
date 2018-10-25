import requests
from django.conf import settings
from django.shortcuts import render, redirect

from user.models import User


def login_required(view_func):
    '''登陆检查装饰器'''
    def check(request):
        if 'uid' in request.session:
            return view_func(request)
        else:
            return redirect('/user/login/')
    return check


def need_perm(perm_name):
    def deco(view_func):
        def wrapper(request):
            user = User.objects.get(pk=request.session['uid'])
            if user.has_perm(perm_name):
                return view_func(request)
            else:
                return render(request, 'blockers.html')
        return wrapper
    return deco


def get_wb_access_token(code):
    '''获取微博的 Access Token'''
    # 构造参数
    args = settings.WB_ACCESS_TOKEN_ARGS.copy()
    args['code'] = code

    response = requests.post(settings.WB_ACCESS_TOKEN_API, data=args)  # 发送请求
    data = response.json()  # 提取数据
    if 'access_token' in data:
        access_token = data['access_token']
        uid = data['uid']
        return access_token, uid
    else:
        return None, None


def wb_user_show(access_token, wb_uid):
    '''根据微博用户ID获取用户信息'''
    # 构造参数
    args = settings.WB_USER_SHOW_ARGS
    args['access_token'] = access_token
    args['uid'] = wb_uid

    # 发送请求
    response = requests.get(settings.WB_USER_SHOW_API, params=args)
    data = response.json()
    if 'screen_name' in data:
        screen_name = data['screen_name']
        avatar = data['avatar_hd']
        return screen_name, avatar
    else:
        return None, None
