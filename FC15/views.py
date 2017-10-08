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

AUTO_COMPILE = False


# All of the views

# Home page
def home(request):
    username = request.COOKIES.get('username', '')
    posts = BlogPost.objects.all()
    return render(request, 'home.html', {'posts': posts, 'username': username})


# Login
def login(request):
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
        userform = UserRegistForm()
    return render(request, 'regist.html', {'form': userform})


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
    return render(request, 'resetrequest.html', {'form': userform})


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
        userform = ChangeForm(data = {'email': user.email})
    return render(request, 'change.html', {'username': username, 'form': userform})


# To index page
def index(request):
    username = request.COOKIES.get('username', '')
    if username == '':
        flash(request, 'Error', 'Please login first', 'error')
        return HttpResponseRedirect('/login/')
    posts = BlogPost.objects.filter(username__exact = username)
    files = FileInfo.objects.filter(username__exact = username)
    me = get_object_or_404(UserInfo, username = username)
    if me.team == '':
        warning = 'You have not joined a team yet'
        return render(request, 'index.html', {'username': username, 'posts': posts, 'files': files, 'warning': warning})
    else:
        warning = ''
        codes = FileInfo.objects.filter(teamname__exact = me.team).exclude(username = username)
        return render(request, 'index.html', {'username': username, 'posts': posts, 'files': files, 'warning': '', 'codes': codes})


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
                run() #=========================================================================================
            return HttpResponseRedirect('/index/')
            #return HttpResponse('Upload success!')
    else:
        userform = FileUploadForm()
        username = request.COOKIES.get('username', '')
        if username == '':
            return HttpResponseRedirect('/login/')
    return render(request, 'upload.html', {'username': username, 'form': userform})


# Edit a file
def fileedit(request, pk):
    file = get_object_or_404(FileInfo, pk = pk)
    username = request.COOKIES.get('username', '')
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
        myfile = reqeust.FILES.get('file', None)
        if myfile:
            if myfile.size >= 1048576:
                flash(request, 'Error', 'File should not be larger than 1 MiB', 'error')
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

        if userform.is_valid():
            # delete old file
            os.remove(file.path)
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
                run() #=====================================================================================
            return HttpResponseRedirect('/index/')
            #return HttpResponse('File edited successfully')
    else:
        userform = FileUploadForm(data = {'filename': file.filename, 'description': file.description, 'file': file.file})
    return render(request, 'upload.html', {'username': username, 'form': userform})


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
    if username != file.username:
        flash(request, 'Error', 'You can only download you own file!')
        return HttpResponseRedirect('/index/')
        #return HttpResponse('Error! You can only download your own file.')
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
                flash(request, 'Error', 'Please login first', 'error')
                return HttpResponseRedirect('/login/')
            else:
                blogpost = BlogPost()
                blogpost.title = userform.cleaned_data['title']
                blogpost.content = userform.cleaned_data['content']
                blogpost.username = username
                blogpost.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                blogpost.save()
                flash(request, 'Success', 'The blog has been successfully posted.')
                return HttpResponseRedirect('/index/')
                #return HttpResponse('Blog posted successfully')
    else:
        userform = BlogPostForm()
        username = request.COOKIES.get('username', '')
        if username == '':
            flash(request, 'Error', 'Please login first', 'error')
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
    return render(request, 'team.html', {'myteam': myteam,'joinedteam': joinedteam, 'teams': teams})


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
        flash(request, 'Error', 'You have already joined a team', 'error')
        return HttpResponseRedirect('/team/')
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
        flash(request, 'Error', 'You have already joined a tem', 'error')
        return HttpResponseRedirect('/team/')
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
        flash(request, 'Error', 'You have already joined a team!', 'error')
        return HttpResponseRedirect('/team/')
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
    my_team = get_object_or_404(TeamInfo, teamname = me.team)
    members = UserInfo.objects.filter(team__exact = my_team.teamname)
    requests = TeamRequest.objects.filter(destin_team = my_team.teamname)
    return render(request, 'teamdetail.html', {'username': username, 'team': my_team, 'members': members, 'requests': requests})


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
                return HttpResponseRedirect('/team/')
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
                return HttpResponseRedirect('/team/')
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


# compile all file ==============================================
def compileall(request):
    run()
    return HttpResponse('done!')