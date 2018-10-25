"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from post import views as post_views
from user import views as user_views


urlpatterns = [
    url(r'^$', post_views.post_list),
    url(r'^post/list/', post_views.post_list),
    url(r'^post/create/', post_views.create_post),
    url(r'^post/edit/', post_views.edit_post),
    url(r'^post/read/', post_views.read_post),
    url(r'^post/delete/', post_views.delete_post),
    url(r'^post/search/', post_views.search),
    url(r'^post/top10/', post_views.top10),
    url(r'^post/comment/', post_views.comment),
    url(r'^post/del_comment/', post_views.del_comment),

    url(r'^post/del_user/', post_views.del_user),

    url(r'user/register/', user_views.register),
    url(r'user/login/', user_views.login),
    url(r'user/logout/', user_views.logout),
    url(r'user/info/', user_views.user_info),

    url(r'weibo/callback/', user_views.weibo_callback),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
