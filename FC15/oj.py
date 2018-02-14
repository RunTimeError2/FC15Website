import os
import threading
from FC15.models import FileInfo, AIInfo

IS_RUNNING = 0
# COMPILE_MODE = 'VS'
COMPILE_MODE = 'G++'
FILE_SUFFIX = 'exe'
# FILE_SUFFIX = 'dll'


# Start running
def run():
    global IS_RUNNING
    if IS_RUNNING == 0:
        IS_RUNNING = 1
        t = threading.Thread(target = compile_all)
        t.start()


# Copy file
def copy_file(username, file_name):
    global COMPILE_MODE
    source_dir = 'fileupload/{0}/{1}'.format(username, file_name)
    if COMPILE_MODE == 'VS':
        destin_dir = 'cpp_proj/cpp_proj/main.cpp'
    if COMPILE_MODE == 'G++':
        destin_dir = 'g++_compile/main.cpp'
    if os.path.isfile(source_dir):
        open(destin_dir, 'wb').write(open(source_dir, 'rb').read())
        return True
    else:
        return False


# Copy exe file
def copy_exe(username, file_name):
    global FILE_SUFFIX
    global COMPILE_MODE
    if COMPILE_MODE == 'VS':
        source_dir = 'cpp_proj/Debug/cpp_proj.' + FILE_SUFFIX
    if COMPILE_MODE == 'G++':
        source_dir = 'g++_compile/main.' + FILE_SUFFIX
    destin_dir = 'fileupload/{0}/{1}.{2}'.format(username, file_name[:-4], FILE_SUFFIX)
    if os.path.isfile(source_dir):
        open(destin_dir, 'wb').write(open(source_dir, 'rb').read())
        return True
    else:
        return False


# Copy executable file to /playgame directory
def store_exe(username, file_name, pk):
    global FILE_SUFFIX
    global COMPILE_MODE
    source_dir = 'fileupload/{0}/{1}.{2}'.format(username, file_name[:-4], FILE_SUFFIX)
    destin_dir = 'playgame/{0}.{1}'.format(pk, FILE_SUFFIX)
    if os.path.isfile(source_dir):
        open(destin_dir, 'wb').write(open(source_dir, 'rb').read())
        return True
    else:
        return False


# Delete copied executable file in /playgame directory
def delete_exe(file_object):
    global FILE_SUFFIX
    if file_object.is_compile_success == 'Successfully compiled':
        if os.path.exists('/playgame/{0}.{1}'.format(file_object.pk, FILE_SUFFIX))
            os.remove('/playgame/{0}.{1}'.format(file_object.pk, FILE_SUFFIX))

# Compile all the file
def compile_all():
    global IS_RUNNING
    if IS_RUNNING == 0:
        return
    is_done = True
    while is_done:
        is_done = False
        all_file = FileInfo.objects.all()
        for file in all_file:
            if file.is_compiled == 'Not compiled':
                is_done = True
                copy_result = copy_file(file.username, file.exact_name)
                if copy_result:
                    # use visual studio to compile the project
                    global COMPILE_MODE
                    if COMPILE_MODE == 'VS':
                        compile_result = os.system('devenv cpp_proj/cpp_proj.sln /rebuild > result.txt')
                    if COMPILE_MODE == 'G++':
                        compile_result = os.system('g++ -o g++_compile/main.' + FILE_SUFFIX + ' g++_compile/main.cpp')
                    file.is_compiled = 'Compiled'
                if compile_result == 0:
                    file.is_compile_success = 'Successfully compiled'
                    copy_exe(file.username, file.exact_name)
                else:
                    file.is_compile_success = 'Compile Error'
                file.save()
    IS_RUNNING = 0


# Copy all available executable file
def copy_all_exe():
    file_available = FileInfo.objects.filter(is_compile_success__exact = 'Successfully compiled')
    for file in file_available:
        store_exe(file.username, file.exact_name, file.pk)


# Play game
def play_game(ai_list):
    logic_exe_name = 'main_logic'
    startgame_failure = -1
    cmd = logic_exe_name + ' '
    if ai_list:
        for item in ai_list:
            cmd = cmd + '{0} '.format(item)
        result = os.system(cmd)
        return result
    else:
        return startgame_failure