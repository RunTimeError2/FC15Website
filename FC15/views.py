from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import RequestContext

from FC15.models import UserInfo, TeamInfo, FileInfo, BlogPost
from FC15.forms import BlogPostForm, UserLoginForm, UserRegistForm, FileUploadForm, CreateTeamForm
import time, os

# All of the views

# Home page
def home(request):
    return render(request, 'home.html')


# Login
def login(request):
    if request.method == 'POST':
        userform = UserLoginForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']

            user = UserInfo.objects.filter(username__exact = username, password__exact = password)

            if user:
                response = HttpResponseRedirect('/index/')
                # User will automatically login within 1 hour
                response.set_cookie('username', username, 3600)
                return response
            else:
                return HttpResponseRedirect('/login/')
    else:
        userform = UserLoginForm()
    return render(request, 'login.html', {'form': userform})


# Logout
def logout(request):
    response = HttpResponse('Logout successfully')
    response.delete_cookie('username')
    return response


# Register
def regist(request):
    if request.method == 'POST':
        userform = UserRegistForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            email = userform.cleaned_data['email']
            stu_number = userform.cleaned_data['stu_number']
            password_confirm = userform.cleaned_data['password_confirm']

            if password == password_confirm:
                UserInfo.objects.create(username = username, password = password, email = email, stu_number = stu_number)
                return HttpResponse('Regist success!')
            else:
                return HttpResponseRedirect('/regist/')
    else:
        userform = UserRegistForm()
    return render(request, 'regist.html', {'form': userform})


# To index page
def index(request):
    username = request.COOKIES.get('username', '')
    posts = BlogPost.objects.filter(username__exact = username)
    files = FileInfo.objects.filter(username__exact = username)
    return render(request, 'index.html', {'username': username, 'posts': posts, 'files': files})


# Uplaod file
def upload(request):
    if request.method == 'POST':
        userform = FileUploadForm(request.POST, request.FILES)
        if userform.is_valid():
            #limit the size and type of file to be uploaded
            myfile = request.FILES.get('file', None)
            if myfile:
                if myfile.size >= 1048576:
                    return HttpResponse('Error! File should not be larger than 1 MiB')
                if myfile.name.endswith('.cpp') == False:
                    return HttpResponse('Error! Only .cpp file is accepted.')
            else:
                return HttpResponse('Error! File does not exist.')

            username = request.COOKIES.get('username', '')
            if username == '':
                return HttpResponseRedirect('/upload/login/')
            else:
                user = UserInfo.objects.get(username = username)
                fileupload = FileInfo()
                fileupload.filename = userform.cleaned_data['filename']
                fileupload.username = username
                fileupload.teamname = user.team
                fileupload.description = userform.cleaned_data['description']
                fileupload.file = userform.cleaned_data['file']
                fileupload.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                fileupload.save()
                return HttpResponse('Upload success!')
    else:
        userform = FileUploadForm()
        username = request.COOKIES.get('username', '')
        if username == '':
            return HttpResponseRedirect('/upload/login/')
    return render(request, 'upload.html', {'username': username, 'form': userform})


# Edit a file
def fileedit(request, pk):
    file = get_object_or_404(FileInfo, pk = pk) # Process 404 ?????????????????????????????????????????
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    if username != file.username:
        return HttpResponse('Error! You can only edit your own file.')
    if request.method == 'POST':
        userform = FileUploadForm(request.POST, request.FILES)

        #limit the size and type of file to be uploaded
        myfile = reqeust.FILES.get('file', None)
        if myfile:
            if myfile.size >= 1048576:
                return HttpResponse('Error! File should not be larger than 1 MiB')
            if myfile.name.endswith('.cpp') == False:
                return HttpResponse('Error! Only .cpp file is accepted.')
        else:
            return HttpResponse('Error! File does not exist.')

        if userform.is_valid():
            # delete old file
            os.remove(file.path)
            file.filename = userform.cleaned_data['filename']
            file.description = userform.cleaned_data['description']
            file.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            file.file = userform.cleaned_data['file']
            file.save()
            return HttpResponse('File edited successfully')
    else:
        userform = FileUploadForm(data = {'filename': file.filename, 'description': file.description, 'file': file.file})
    return render(request, 'upload.html', {'username': username, 'form': userform})


# Delete a file
def filedelete(request, pk):
    file = get_object_or_404(FileInfo, pk = pk)
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    if username != file.username:
        return HttpResponse('Error! You can only delete your own file.')
    os.remove(file.path)
    file.delete()
    return HttpResponseRedirect('/index/')


# Download a file
def filedownload(request ,pk):
    def file_iterator(file_name, chunk_size = 2048):  
        with open(file_name) as f:  
            while True:  
                c = f.read(chunk_size)  
                if c:
                    yield c
                else:
                    break  

    file = get_object_or_404(FileInfo, pk = pk)
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    if username != file.username:
        return HttpResponse('Error! You can only download your own file.')
    response = StreamingHttpResponse(file_iterator(file.path))  
    response['Content-Type'] = 'application/octet-stream'  
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file.origin_name)
    return response


# Post a blog
def postblog(request):
    if request.method == 'POST':
        userform = BlogPostForm(request.POST)
        if userform.is_valid():
            username = request.COOKIES.get('username', '')
            if username == '':
                return HttpResponseRedirect('/login/')
            else:
                blogpost = BlogPost()
                blogpost.title = userform.cleaned_data['title']
                blogpost.content = userform.cleaned_data['content']
                blogpost.username = username
                blogpost.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                blogpost.save()
                return HttpResponse('Blog posted successfully')
    else:
        userform = BlogPostForm()
        username = request.COOKIES.get('username', '')
        if username == '':
            return HttpResponseRedirect('/login/')
    return render(request, 'blogpost.html', {'username': username, 'form': userform})


# Show the detail of a blog
def blogdetail(request, pk):
    post = get_object_or_404(BlogPost, pk = pk)
    return render(request, 'blogdetail.html', {'post': post})


# Edit a blog
def blogedit(request, pk):
    post = get_object_or_404(BlogPost, pk = pk)
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    if username != post.username:
        return HttpResponse('Error! You can only edit your own blog.')
    if request.method == 'POST':
        userform = BlogPostForm(request.POST)
        if userform.is_valid():
            post.title = userform.cleaned_data['title']
            post.content = userform.cleaned_data['content']
            post.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            post.save()
            return render(request ,'blogdetail.html', {'post': post})
    else:
        userform = BlogPostForm(data = {'title': post.title, 'content': post.content})
    return render(request, 'blogpost.html', {'username': username, 'form': userform})


# Delete a blog
def blogdelete(request, pk):
    post = get_object_or_404(BlogPost, pk = pk)
    post.delete()
    return HttpResponseRedirect('/index/')


# View the list of all teams
def team(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    myteam = TeamInfo.objects.filter(captain__exact = username)
    teams = TeamInfo.objects.all()
    return render(request, 'team.html', {'myteam': myteam, 'teams': teams})


# Create a team
def createteam(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    myteam = TeamInfo.objects.filter(captain__exact = username)

    # Creating more than one team is not allowed
    if myteam:
        return HttpResponse('You have already created a team!')

    if request.method == 'POST':
        userform = CreateTeamForm(request.POST)
        if userform.is_valid():
            newteam = TeamInfo()
            newteam.teamname = userform.cleaned_data['teamname']
            newteam.introduction = userform.cleaned_data['introduction']
            newteam.captain = username
            newteam.save()
            me = UserInfo.objects.get(username = username)
            me.team = newteam.teamname
            return HttpResponse('Team created successfully')
    else:
        userform = CreateTeamForm()
    return render(request, 'createteam.html', {'form': userform})


# Join a team
def jointeam(request, pk):
    username = request.COOKIES.get('username', '')
    if username == '':
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username)
    if me.team != '':
        return HttpResponse('You have already joined a team!')
    team = get_obejct_or_404(TeamInfo, pk = pk)
    me.team = team.teamname
    me.save()
    return HttpResponse('You have successfully joined this team.')