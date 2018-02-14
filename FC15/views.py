from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import RequestContext
from django.contrib import messages

from FC15.models import UserInfo, TeamInfo, FileInfo, BlogPost, EmailActivate, PasswordReset, TeamRequest
from FC15.forms import BlogPostForm, UserLoginForm, UserRegistForm, FileUploadForm, CreateTeamForm, ResetPasswordForm, ChangeForm, TeamRequestForm
from FC15.sendmail import mail_activate, password_reset
from FC15.forms import flash
from FC15.oj import run
import time, os, random

AUTO_COMPILE = True


# All of the views

# Home page
def home(request):
    username = request.COOKIES.get('username', '')
    posts1 = BlogPost.objects.all()[: 2]
    posts2 = BlogPost.objects.all()[2: 4]
    return render(request, 'home.html', {'posts1': posts1, 'posts2': posts2, 'username': username})


# Login
def login(request):
    current_username = request.COOKIES.get('username', '')
    if current_username != '':
        flash(request, 'Error', 'You have already login! Please logout first.')
        return HttpResponseRedirect('/index/')
    if request.method == 'POST':
        userform = UserLoginForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']

            user = UserInfo.objects.filter(username__exact = username, password__exact = password)

            if user:
                user_exact = UserInfo.objects.get(username = username, password = password)
                if user_exact.activated:
                    response = HttpResponseRedirect('/index/')
                    # User will automatically login within 1 hour
                    response.set_cookie('username', username, 3600)
                    return response
                else:
                    flash(request, 'Error', 'This user account has not been activated!', 'error')
                #    return HttpResponse('This user account has not been activated!')
            else:
                flash(request, 'Error', 'Incorrect username or password, please retry.', 'error')
                #return HttpResponseRedirect('/login/')
                #return HttpResponse('Incorrect username or password, please retry.')
    else:
        userform = UserLoginForm()
    return render(request, 'login.html', {'form': userform})


# Logout
def logout(request):
    response = HttpResponseRedirect('/home/')
    flash(request, 'Success', 'Logout successfully', 'success')
    response.delete_cookie('username')
    return response


# Register
def regist(request):
    if request.method == 'POST':
        userform = UserRegistForm(request.POST)
        un = request.POST['username']
        print(un)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            realname = userform.cleaned_data['realname']
            password = userform.cleaned_data['password']
            email = userform.cleaned_data['email']
            stu_number = userform.cleaned_data['stu_number']
            password_confirm = userform.cleaned_data['password_confirm']

            if password == password_confirm:
                existing_user = UserInfo.objects.filter(username__exact = username)
                if existing_user:
                    flash(request, 'Error', 'The username already exists!', 'error')
                    return render(request, 'regist.html', {'form': userform})
                    #return HttpResponse('Error! The username already exists')
                existing_email = UserInfo.objects.filter(email__exact = email)
                if existing_email:
                    flash(request, 'Error', 'The email address has already been used!', 'error')
                    return render(request, 'regist.html', {'form': userform})
                    #return HttpResponse('Error! The email address has already been used!')
                UserInfo.objects.create(username = username, realname = realname, password = password, email = email, stu_number = stu_number, activated = False)
                mail_activate(email, username)
                flash(request, 'Success', 'The confirmation email has been successfully sent. Please check you email!')
                return HttpResponseRedirect('/home/')
                #return HttpResponse('Regist success! Please check your email.')
            else:
                flash(request, 'Error', 'You should enter the same password!')
                return HttpResponseRedirect('/regist/')
        else:
            flash(request, 'Error', 'Please complete the form and then submit.')
            print('userform is invalid')
    else:
        userform = UserRegistForm()
    return render(request, 'regist.html', {'form': userform})


# About page
#def about(request):
#    return render(request, 'about.html')


# Introduction for FC15(and the game)
def about_fc15(request):
    return render(request, 'about_fc15.html')


# Introduction for DAASTA
def about_asta(request):
    return render(request, 'about_asta.html')


# Introduction for the sponsor
def about_sponsor(request):
    return render(request, 'about_sponsor.html')


# Documents of the game
def document(request):
    return render(request, 'document.html')


# Activate account with email
def activate(request, activate_code):
    activate_record = EmailActivate.objects.get(activate_string = activate_code)
    if activate_record:
        username = activate_record.username
        user = UserInfo.objects.get(username = username)
        if user:
            user.activated = True
            user.save()
            activate_record.delete()
            flash(request, 'Success', 'You have successfully activated the account!')
            return HttpResponseRedirect('/login/')
            #return HttpResponse('You have successfully activated the account!')
        else:
            flash(request, 'Error', 'Invalid activating code!')
            return HttpResponseRedirect('/home/')
            #return HttpResponse('Invalid activating code!')
    else:
        return HttpResponse('Invalid activating url!')


# Fill in the request to reset password
def resetrequest(request):
    username = request.COOKIES.get('username', '')
    if request.method == 'POST':
        userform = ResetPasswordForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            email = userform.cleaned_data['email']
            user = UserInfo.objects.filter(username__exact = username, email__exact = email)
            if user:
                password_reset(email, username)
                flash(request, 'Success', 'The email has been send, please check you email!')
                return HttpResponseRedirect('/home/')
                #return HttpResponse('Success! Please check your email.')
            else:
                flash(request, 'Error', 'Incorrect user information!')
                return HttpResponseRedirect('/resetrequest/')
                #return HttpResponse('Error! Incorrect user information!')
    else:
        userform = ResetPasswordForm()
    return render(request, 'resetrequest.html', {'username': username, 'form': userform})


# Reset the password
def resetpassword(request, reset_code):
    reset_record = PasswordReset.objects.get(reset_string = reset_code)
    if reset_record:
        user = UserInfo.objects.get(username = reset_record.username)
        user.password = reset_record.new_password
        user.save()
        reset_record.delete()
        flash(request, 'Success', 'Your password has been successfully reset!\nPlease change your password after you login.', 'success')
        return HttpResponseRedirect('/login/')
        #return HttpResponse('Your password has been successfully reset!\nPlease change your password after you login.')
    else:
        flash(request, 'Error', 'Invalid reset code!', 'error')
        return HttpResponseRedirect('/home/')
        #return HttpResponse('Error! Invalid reset code!')


# Change the password or email
def change(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    user = UserInfo.objects.get(username = username)
    if request.method == 'POST':
        userform = ChangeForm(request.POST)
        if userform.is_valid():
            old_password = userform.cleaned_data['old_password']
            new_password = userform.cleaned_data['new_password']
            confirm_password = userform.cleaned_data['confirm_password']
            if old_password != user.password:
                flash(request, 'Error', 'Incorrect old password!', 'error')
                return render(request, 'change.html', {'username': username, 'form': userform})
                #return HttpResponse('Error! Incorrect old password')
            if new_password != confirm_password:
                flash(request, 'Error', 'Please enter the same password!', 'error')
                return render(request, 'change.html', {'username': username, 'form': userform})
                #return HttpResponse('Error! Please enter the same password')
            user.password = new_password
            user.email = userform.cleaned_data['email']
            user.save()
            flash(request, 'Success', 'You have successfully changed your account. Please login.', 'success')
            response = HttpResponseRedirect('/login/')
            response.delete_cookie('username')
            return response
        else:
            flash(request, 'Error', 'Please complete the form!', 'error')
            return render(request, 'change.html', {'username': username, 'form': userform})
    else:
        userform = ChangeForm(data = {'email': user.email})
    return render(request, 'change.html', {'username': username, 'form': userform})


# To index page
def index(request):
    #return render(request, 'index2.html') #================================================
    #return render(request, 'index.html')
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    posts = BlogPost.objects.filter(username__exact = username)
    files = FileInfo.objects.filter(username__exact = username)
    me = get_object_or_404(UserInfo, username = username)
    if me.team == '':
        warning = 'You have not joined a team yet'
        return render(request, 'userindex.html', {'username': username, 'posts': posts, 'files': files, 'warning': warning})
    else:
        warning = ''
        codes = FileInfo.objects.filter(teamname__exact = me.team).exclude(username = username)
        return render(request, 'userindex.html', {'username': username, 'posts': posts, 'files': files, 'warning': '', 'codes': codes})


# Uplaod file
def upload(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        userform = FileUploadForm(request.POST, request.FILES)
        if userform.is_valid():
            #limit the size and type of file to be uploaded
            myfile = request.FILES.get('file', None)
            if myfile:
                if myfile.size >= 1048576:
                    flash(request, 'Error', 'File should not be larger than 1 MiB.', 'error')
                    return render(request, 'upload.html', {'username': username, 'form': userform})
                    #return HttpResponse('Error! File should not be larger than 1 MiB')
                if myfile.name.endswith('.cpp') == False:
                    flash(request, 'Error', 'Only .cpp file is accepted.', 'error')
                    return render(request, 'upload.html', {'username': username, 'form': userform})
                    #return HttpResponse('Error! Only .cpp file is accepted.')
            else:
                flash(request, 'Error', 'File does not exist.', 'error')
                return render(request, 'upload.html', {'username': username, 'form': userform})
                #return HttpResponse('Error! File does not exist.')

            user = get_object_or_404(UserInfo, username = username)
            fileupload = FileInfo()
            fileupload.filename = userform.cleaned_data['filename']
            fileupload.username = username
            fileupload.teamname = user.team
            fileupload.description = userform.cleaned_data['description']
            fileupload.file = userform.cleaned_data['file']
            fileupload.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            fileupload.is_compiled = 'Not compiled'
            fileupload.is_compile_success = ''
            fileupload.compile_result = ''
            fileupload.save()
            flash(request, 'Success', 'You have successfully uploaded the code.', 'success')
            global AUTO_COMPILE
            if AUTO_COMPILE:
                run()
            return HttpResponseRedirect('/index/')
            #return HttpResponse('Upload success!')
        else:
            pass
    else:
        userform = FileUploadForm()
        username = request.COOKIES.get('username', '')
        if username == '':
            return HttpResponseRedirect('/login/')
    return render(request, 'upload.html', {'username': username, 'form': userform, 'filename': '', 'description': ''})


# Edit a file
def fileedit(request, pk):
    file = get_object_or_404(FileInfo, pk = pk)
    username = request.COOKIES.get('username', '')
    filename = file.filename
    description = file.description
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    if username != file.username:
        flash(request, 'Error', 'You can only edit your own file.', 'error')
        return HttpResponseRedirect('/index/')
        #return HttpResponse('Error! You can only edit your own file.')
    if request.method == 'POST':
        userform = FileUploadForm(request.POST, request.FILES)

        #limit the size and type of file to be uploaded
        myfile = request.FILES.get('file', None)
        if myfile:
            if myfile.size >= 1048576:
                flash(request, 'Error', 'File should not be larger than 1 MiB', 'error')
                return render(request, 'upload.html', {'username': username, 'form': userform, 'filename': filename, 'description': description})
                #return HttpResponse('Error! File should not be larger than 1 MiB')
            if myfile.name.endswith('.cpp') == False:
                flash(request, 'Error', 'Only .cpp file is accepted.', 'error')
                return render(request, 'upload.html', {'username': username, 'form': userform, 'filename': filename, 'description': description})
                #return HttpResponse('Error! Only .cpp file is accepted.')
        else:
            flash(request, 'Error', 'File does not exist.', 'error')
            return render(request, 'upload.html', {'username': username, 'form': userform, 'filename': filename, 'description': description})
            #return HttpResponse('Error! File does not exist.')

        if userform.is_valid():
            # delete old file
            os.remove(file.path)
            if os.path.exists(file.path[:-4] + '.exe'):
                os.remove(file.path[:-4] + '.exe')
            file.filename = userform.cleaned_data['filename']
            file.description = userform.cleaned_data['description']
            file.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            file.file = userform.cleaned_data['file']
            file.is_compiled = 'Not compiled'
            file.is_compile_success = ''
            file.compile_result = ''
            file.save()
            flash(request, 'Success', 'You have successfully edited the file', 'success')
            global AUTO_COMPILE
            if AUTO_COMPILE:
                run()
            return HttpResponseRedirect('/index/')
            #return HttpResponse('File edited successfully')
    else:
        userform = FileUploadForm(data = {'filename': file.filename, 'description': file.description, 'file': file.file})
    return render(request, 'upload.html', {'username': username, 'form': userform, 'filename': filename, 'description': description})


# Delete a file
def filedelete(request, pk):
    file = get_object_or_404(FileInfo, pk = pk)
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    if username != file.username:
        flash(request, 'Error', 'You can only delete your own file.', 'error')
        return HttpResponseRedirect('/index/')
        #return HttpResponse('Error! You can only delete your own file.')
    os.remove(file.path)
    if os.path.exists(file.path[:-4] + '.exe'):
        os.remove(file.path[:-4] + '.exe')
    file.delete()
    flash(request, 'Success', 'You have successfully deleted the file.', 'success')
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
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username)
    authors = UserInfo.objects.filter(username__exact = file.username)
    if authors:
        author = UserInfo.objects.get(username = username)
    else:
        author = None
        flash(request, 'Error', 'Invalid code! The author of the code does not exist.')
        return HttpResponseRedirect('/index/')
    #author = get_object_or_404(UserInfo, username = file.username)
    if username != file.username:
        if author.team == '' or me.team == '' or author.team != me.team:
            flash(request, 'Error', 'You can only download your own file or code of your teammates!')
            return HttpResponseRedirect('/index/')
            #return HttpResponse('Error! You can only download your own file.')
    response = StreamingHttpResponse(file_iterator(file.path))  
    response['Content-Type'] = 'application/octet-stream'  
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file.origin_name)
    return response


# View all blogs
def viewblogs(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    blogs = BlogPost.objects.all()
    #return render(request, 'viewblogs.html', {'username': username, 'blogs': blogs})
    return render(request, 'viewblogs.html', {'username': username, 'blogs': blogs})


# Post a blog
def postblog(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        userform = BlogPostForm(request.POST)
        if userform.is_valid():
            blogpost = BlogPost()
            blogpost.title = userform.cleaned_data['title']
            blogpost.content = userform.cleaned_data['content']
            blogpost.username = username
            blogpost.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            blogpost.save()
            flash(request, 'Success', 'The blog has been successfully posted.')
            return HttpResponseRedirect('/index/')
            #return HttpResponse('Blog posted successfully')\
        else:
            print('Invalid userform')
    else:
        userform = BlogPostForm()
    return render(request, 'blogpost.html', {'username': username, 'form': userform, 'title': '', 'content': ''})


# Return an 'unfinished' message
def unfinished(request):
    return HttpResponse('Oh, this function has not been finished yet!')


# Show the detail of a blog
def blogdetail(request, pk):
    username = request.COOKIES.get('username', '')
    post = get_object_or_404(BlogPost, pk = pk)
    background_image_count = 2
    bg_index = random.randint(1, background_image_count)
    bg_filename = 'blog-bg-' + str(bg_index) + '.jpg'
    return render(request, 'blogdetail.html', {'post': post, 'username': username, 'bgname': bg_filename})


# Edit a blog
def blogedit(request, pk):
    post = get_object_or_404(BlogPost, pk = pk)
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    if username != post.username:
        flash(request, 'Error', 'You can only edit you own blog!')
        return HttpResponseRedirect('/index/')
        #return HttpResponse('Error! You can only edit your own blog.')
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
    return render(request, 'blogpost.html', {'username': username, 'form': userform, 'title': post.title, 'content': post.content})


# Delete a blog
def blogdelete(request, pk):
    post = get_object_or_404(BlogPost, pk = pk)
    post.delete()
    return HttpResponseRedirect('/index/')


# View the list of all teams
def team(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = UserInfo.objects.get(username = username)
    myteams = TeamInfo.objects.filter(captain__exact = username)
    if myteams:
        myteam = TeamInfo.objects.get(captain = username)
    else:
        myteam = None
    if TeamInfo.objects.filter(teamname__exact = me.team):
        joinedteam = TeamInfo.objects.get(teamname = me.team)
    else:
        joinedteam = None
    teams = TeamInfo.objects.all()
    return render(request, 'team.html', {'username': username, 'myteam': myteam,'joinedteam': joinedteam, 'teams': teams})


# Create a team
def createteam(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    myteam = TeamInfo.objects.filter(captain__exact = username)

    # Creating or joining more than one team is not allowed
    if myteam:
        flash(request, 'Error', 'You have already created a team', 'error')
        return HttpResponseRedirect('/team/')
        #return HttpResponse('You have already created a team!')
    me = get_object_or_404(UserInfo, username = username)
    if me.team != '':
        my_current_team = TeamInfo.objects.filter(teamname__exact = me.team)
        if my_current_team:
            flash(request, 'Error', 'You have already joined a team', 'error')
            return HttpResponseRedirect('/team/')
        else:
            flash(request, 'Error', 'Your current team does not exist, now you do not belong to any team lol.')
            me.team = ''
            me.save()
        #return HttpResponse('You have already joined a team!')

    if request.method == 'POST':
        userform = CreateTeamForm(request.POST)
        if userform.is_valid():
            newteam = TeamInfo()
            newteam.teamname = userform.cleaned_data['teamname']
            newteam.introduction = userform.cleaned_data['introduction']
            newteam.captain = username
            newteam.members = 1
            newteam.save()
            me = UserInfo.objects.get(username = username)
            me.team = newteam.teamname
            me.save()
            flash(request, 'Success', 'Team created successfully', 'success')
            return HttpResponseRedirect('/team/')
            #return HttpResponse('Team created successfully')
    else:
        userform = CreateTeamForm()
    return render(request, 'createteam.html', {'form': userform})


# Join a team
def jointeam(request, pk):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username)
    if me.team != '':
        my_current_team = TeamInfo.objects.filter(teamname__exact = me.team)
        if my_current_team:
            flash(request, 'Error', 'You have already joined a tem', 'error')
            return HttpResponseRedirect('/team/')
        else:
            flash(request, 'Error', 'Your current team does not exist, now you do not belong to any team lol.')
            me.team = ''
            me.save()
        #return HttpResponse('You have already joined a team!')
    team = get_object_or_404(TeamInfo, pk = pk)
    userform = TeamRequestForm(data = {'destin_team': team.teamname})
    return render(request, 'teamrequest.html', {'username': username, 'form': userform})


# Send a request to join the team
def jointeamrequest(request, pk):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username)
    if me.team != '':
        my_current_team = TeamInfo.objects.filter(teamname__exact = me.team)
        if my_current_team:
            flash(request, 'Error', 'You have already joined a team!', 'error')
            return HttpResponseRedirect('/team/')
        else:
            flash(request, 'Error', 'Your current team does not exist, now you do not belong to any team lol.')
            me.team = ''
            me.save()
        #return HttpResponse('You have already joined a team!')
    team = get_object_or_404(TeamInfo, pk = pk)
    if request.method == 'POST':
        userform = TeamRequestForm(request.POST)
        if userform.is_valid():
            team_request = TeamRequest()
            team_request.username = username
            team_request.destin_team = userform.cleaned_data['destin_team']
            team_request.message = userform.cleaned_data['message']
            team_request.status = False
            existing_request = TeamRequest.objects.filter(username__exact = username, destin_team__exact = team_request.destin_team)
            if existing_request:
                flash(request, 'Error', 'Error! You have already sent a request to join this team!', 'error')
                return HttpResponseRedirect('/team/')
            team_request.save()
            flash(request, 'Success', 'Request has been sent! Please wait for the captain to reply.', 'success')
            return HttpResponseRedirect('/team/')
        else:
            flash(request, 'Error', 'Please complete the form!')
            return render(request, 'teamrequest.html', {'username': username, 'form': userform})
    else:
        msg = 'I am ' + username + ', ' + me.realname
        userform = TeamRequestForm(data = {'destin_team': team.teamname, 'message': msg})
    return render(request, 'teamrequest.html', {'username': username, 'form': userform})


# Accept a request to join a team
def acceptrequest(request, pk):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username) # Me, namely the captain
    team_request = get_object_or_404(TeamRequest, pk = pk)
    destin_team = team_request.destin_team
    team = get_object_or_404(TeamInfo, teamname = destin_team)
    apply_user = get_object_or_404(UserInfo, username = team_request.username) # The one who sent the request
    if team.captain == me.username:
        if team.members >= 4:
            flash(request, 'Error', 'A team at most has 4 members')
            return HttpResponseRedirect('/team/')
            #return HttpResponse('A team at most has 4 members')
        apply_user.team = destin_team
        apply_user.save()
        user_codes = FileInfo.objects.filter(username__exact = apply_user.username)
        if user_codes:
            for code in user_codes:
                code.teamname = destin_team
                code.save()
        team.members = team.members + 1
        team.save()
        team_request.delete()
        flash(request, 'Success', 'You have successfully accepted the request')
        return HttpResponseRedirect('/team/')
        #return HttpResponse('You have successfully accepted the requet.')
    else:
        flash(request, 'Error', 'You can only accept requests to join your own team.')
        return HttpResponseRedirect('/team/')
        #return HttpResponse('You can only accept requests to join your own team.')


# Reject a request to join a team
def rejectrequest(request, pk):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username) # Me, namely the captain
    team_request = get_object_or_404(TeamRequest, pk = pk)
    destin_team = team_request.destin_team
    team = get_object_or_404(TeamInfo, teamname = destin_team)
    if team.captain == me.username:
        team_request.delete()
        flash(request, 'Success', 'You have successfully rejected the request', 'succes')
        return HttpResponseRedirect('/team/')
        #return HttpResponse('You have successfully rejected the request')
    else:
        flash(request, 'Error', 'You can only reject requests to join your own team.')
        return HttpResponseRedirect('/team')
        #return HttpResponse('You can only reject requests to join your own team.')


# Show the detail of a team to the captain
def teamdetail(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    #my_team = get_object_or_404(TeamInfo, captain = username)
    me = get_object_or_404(UserInfo, username = username)
    #my_team_exists = TeamInfo.objects.filter(username__exact = username)
    my_team = me.team
    if my_team:
        my_team = get_object_or_404(TeamInfo, teamname = me.team)
        if my_team.captain == username:
            is_captain = True
        else:
            is_captain = False
        members = UserInfo.objects.filter(team__exact = my_team.teamname)
        requests = TeamRequest.objects.filter(destin_team = my_team.teamname)
        return render(request, 'teamdetail.html', {'username': username, 'team': my_team, 'members': members, 'requests': requests, 'is_captain': is_captain})
    else:
        flash(request, 'Error', 'Please join a team first!', 'error')
        return HttpResponseRedirect('/team/')


# Quit the team
def quitteam(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username)
    if me:
        my_team = me.team
        if my_team == '':
            flash(request, 'Error', 'You have not joined a team yet!', 'error')
            return HttpResponseRedirect('/team/')
        team = get_object_or_404(TeamInfo, teamname = my_team)
        if team:
            captain = team.captain
            if captain == username:
                flash(request, 'Error', 'You are the captain so you cannot simply quit the team!')
                return HttpResponseRedirect('/teamdetail/')
            else:
                me.team = ''
                me.save()
                team.members = team.members - 1
                team.save()
                flash(request, 'Success', 'You have successfully quitted the team.')
                return HttpResponseRedirect('/team/')
        else:
            flash(request, 'Error', 'Team does not exist', 'error')
            return HttpResponseRedirect('/team/')
    else:
        flash(request, 'Error', 'User does not exist!', 'error')
        return HttpResponseRedirect('/login/')


# Dismiss the team
def dismissteam(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    me = get_object_or_404(UserInfo, username = username)
    if me:
        my_team = me.team
        if my_team == '':
            flash(request, 'Error', 'You have not joined a team yet!', 'error')
            return HttpResponseRedirect('/team/')
        team = get_object_or_404(TeamInfo, teamname = my_team)
        if team:
            captain = team.captain
            if captain != username:
                flash(request, 'Error', 'You are not the captain so you cannot dismiss the team!', 'error')
                return HttpResponseRedirect('/teamdetail/')
            else:
                members = UserInfo.objects.filter(team__exact = my_team)
                if members:
                    for member in members:
                        member.team = ''
                        member.save()
                team.delete()
                flash(request, 'Success', 'You have successfully dismissed the team', 'success')
                return HttpResponseRedirect('/team/')
        else:
            flash(request, 'Error', 'Team does not exist!', 'error')
            return HttpResponse('/team/')
    else:
        flash(request, 'Error', 'User does not exist', 'error')
        return HttpResponseRedirect('/login/')


# Play game online
def playgame(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first!', 'error')
        return HttpResponseRedirect('/login/')
    if request.method == 'POST':
        check_box_list = request.POST.getlist('check_box_list')
        if check_box_list:
            for item in check_box_list:
                print('index of ai is ', item)
            return HttpResponse('Submit successfully')
        else:
            print('fail')
            flash(request, 'Error', 'Please choose at lease one item!', 'error')
            return HttpResponseRedirect('/playgame/')
    else:
        all_file = FileInfo.objects.all()
        return render(request, 'playgame.html', {'ailist': all_file})


# Handles 404 error
def page_not_found(request):
    #return HttpResponse('Page not found lol.')
    return render(request, 'page404.html')


# Handles 500 error
def page_error(request):
    #return HttpResponse('Page error lol.')
    return render(request, 'page500.html')