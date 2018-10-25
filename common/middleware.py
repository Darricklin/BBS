import time

from django.shortcuts import render
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin


def test_middleware(view_func):
    '''最简单的中间件'''
    def wrapper(request):
        print('1. view执行之前的处理 (proces_request)')
        response = view_func(request)
        print('2. view执行之后的处理 (process_response)')
        return response
    return wrapper


class BlockMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_ip = request.META['REMOTE_ADDR']
        request_key = 'Request-%s' % user_ip
        block_key = 'Block-%s' % user_ip

        # 黑名单检查
        if cache.has_key(block_key):
            return render(request, 'blockers.html')

        now = time.time()
        # 检查当前时间与前三次的时差是否 小于 1 秒
        request_time = cache.get(request_key, [0] * 10)
        if now - request_time[0] < 1:
            # 封禁 IP
            cache.set(block_key, 1, 15)
            return render(request, 'blockers.html')
        else:
            # 更新访问时间
            request_time.pop(0)
            request_time.append(now)
            cache.set(request_key, request_time)
