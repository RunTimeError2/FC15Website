from django.db import models
from django.contrib import admin
import time, random


# Model which stores information of users
class UserInfo(models.Model):
    username = models.CharField(max_length = 100)
    password = models.CharField(max_length = 100)
    stu_number = models.CharField(max_length = 20)
    email = models.EmailField()
    team = models.CharField(max_length = 100, default = '')
    activated = models.BooleanField(default = False)

    def __unicode__(self):
        return self.username


# Determines how to display class UserInfo in tables for admin
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('username', 'stu_number', 'email')


# Model which stores information of teams
class TeamInfo(models.Model):
    teamname = models.CharField(max_length = 100)
    captain = models.CharField(max_length = 100)
    introduction = models.CharField(max_length = 500)


# Determines how to display class TeamInfo in tables for admin
class TeamInfoAdmin(admin.ModelAdmin):
    list_display = ('teamname', 'captain', 'introduction')


# Model for file uploaded
class FileInfo(models.Model):
    # Determines where the file will be saved
    def user_dirpath(instance, filename):
        now = time.strftime('%Y%m%d%H%M%S')
        _path = 'fileupload/{0}/{1}_{2}__{3}'.format(instance.username, now, random.randint(0, 1000), filename)
        instance.path = _path
        instance.origin_name = filename
        return './' + _path

    filename = models.CharField(max_length = 255)
    username = models.CharField(max_length = 100)
    teamname = models.CharField(max_length = 100)
    description = models.CharField(max_length = 1000)
    file = models.FileField(upload_to = user_dirpath)
    path = models.CharField(max_length = 500)
    origin_name = models.CharField(max_length = 255, default = filename)
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.filename


# Determines how to display class FileInfo in tables for admin
class FileInfoAdmin(admin.ModelAdmin):
    list_display = ('filename', 'username', 'description')


# Model for blogs
class BlogPost(models.Model):
    title = models.CharField(max_length = 150)
    username = models.CharField(max_length = 100)
    content = models.TextField()
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.title


# Determines how to display class BlogPost in tables for admin
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'username', 'timestamp')


# Stores the information for activating with email
class EmailActivate(models.Model):
    username = models.CharField(max_length = 100)
    activate_string = models.CharField(max_length = 100)


# Determines how to display class EmailActivate in table for admin
class EmailActivateAdmin(admin.ModelAdmin):
    list_display = ('username', 'activate_string')


# Register all the models to admin
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(TeamInfo, TeamInfoAdmin)
admin.site.register(FileInfo, FileInfoAdmin)
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(EmailActivate, EmailActivateAdmin)