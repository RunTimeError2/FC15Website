from django.conf.urls import url, include
from django.contrib import admin
from FC15 import views

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^home', views.home, name = 'home'),
    url(r'^index', views.index, name = 'index'),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^regist/$', views.regist, name = 'regist'),
    ]
