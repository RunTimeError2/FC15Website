"""
Definition of urls for FC15Website.
"""
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import staticfiles

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
import FC15.views
admin.autodiscover()

urlpatterns = [
    url(r'^$', FC15.views.home, name = 'home'),
    url(r'^home/$', FC15.views.home, name = 'home'),
    #url(r'^about/$', FC15.views.about, name = 'about'),
    url(r'^about_fc15/$', FC15.views.about_fc15, name = 'about_fc15'),
    url(r'^about_asta/$', FC15.views.about_asta, name = 'about_asta'),
    url(r'^about_sponsor/$', FC15.views.about_sponsor, name = 'about_sponsor'),
    url(r'^document/$', FC15.views.document, name = 'document'),
    url(r'^index/$', FC15.views.index, name = 'index'),
    url(r'^login/$', FC15.views.login, name = 'login'),
    url(r'^logout/$', FC15.views.logout, name = 'logout'),
    url(r'^regist/$', FC15.views.regist, name = 'regist'),
    url(r'^upload/$', FC15.views.upload, name = 'upload'),
    url(r'^postblog/$', FC15.views.postblog, name = 'postblog'),
    url(r'^team/$', FC15.views.team, name = 'team'),
    url(r'^createteam/$', FC15.views.createteam, name = 'createteam'),
    url(r'^resetrequest/$', FC15.views.resetrequest, name = 'resetrequest'),
    url(r'^change/$', FC15.views.change, name = 'change'),
    url(r'^teamdetail/$', FC15.views.teamdetail, name = 'teamdetail'),
    url(r'^teamrequest/$', FC15.views.jointeamrequest, name = 'jointeamrequest'),
    url(r'^quitteam/$', FC15.views.quitteam, name = 'quitteam'),
    url(r'^dismissteam/$', FC15.views.dismissteam, name = 'dismissteam'),

    url(r'^blogdetail/(?P<pk>[0-9]+)/$', FC15.views.blogdetail, name = 'blogdetail'),
    url(r'^blogedit/(?P<pk>[0-9]+)/$', FC15.views.blogedit, name = 'blogedit'),
    url(r'^blogdelete/(?P<pk>[0-9]+)/$', FC15.views.blogdelete, name = 'blogdelete'),
    url(r'^fileedit/(?P<pk>[0-9]+)/$', FC15.views.fileedit, name = 'fileedit'),
    url(r'^filedelete/(?P<pk>[0-9]+)/$', FC15.views.filedelete, name = 'filedelete'),
    url(r'^filedownload/(?P<pk>[0-9]+)/$', FC15.views.filedownload, name = 'filedownload'),
    url(r'^jointeam/(?P<pk>[0-9]+)/$', FC15.views.jointeam, name = 'jointeam'),
    url(r'^jointeamrequest/(?P<pk>[0-9]+)/$', FC15.views.jointeamrequest, name = 'jointeamrequest'),
    url(r'^mailactivate/(?P<activate_code>.*)/$', FC15.views.activate, name = 'activate'),
    url(r'^resetpassword/(?P<reset_code>.*)/$', FC15.views.resetpassword, name = 'resetpassword'),
    url(r'^acceptrequest/(?P<pk>[0-9]+)/$', FC15.views.acceptrequest, name = 'acceptrequest'),
    url(r'^rejectrequest/(?P<pk>[0-9]+)/$', FC15.views.rejectrequest, name = 'rejectrequest'),

    url(r'^admin/', include(admin.site.urls)),

    #url(r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root': '/static'}),  
]

#urlpatterns += staticfiles_urlpatterns()