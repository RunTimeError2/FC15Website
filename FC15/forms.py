from django import forms
from FC15.models import UserInfo, FileInfo, BlogPost, TeamInfo

# All forms for this website

# For users to login
class UserLoginForm(forms.Form):
    username = forms.CharField(max_length = 100)
    password = forms.CharField(max_length = 100, widget = forms.PasswordInput)


# For users to register
class UserRegistForm(forms.Form):
    username = forms.CharField(max_length = 100)
    email = forms.EmailField()
    stu_number = forms.CharField(max_length = 100)
    password = forms.CharField(max_length = 100, widget = forms.PasswordInput)
    password_confirm = forms.CharField(max_length = 100, widget = forms.PasswordInput)


# For users to upload code
class FileUploadForm(forms.Form):
    filename = forms.CharField(max_length = 255)
    description = forms.CharField(max_length = 500, widget = forms.Textarea)
    file = forms.FileField()


# For users to post blogs
class BlogPostForm(forms.Form):
    title = forms.CharField(max_length = 100)
    content = forms.CharField(widget = forms.Textarea)


# For users to create teams
class CreateTeamForm(forms.Form):
    teamname = forms.CharField(max_length = 100)
    introduction = forms.CharField(max_length = 500, widget = forms.Textarea)