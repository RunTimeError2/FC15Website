import os
import threading
from FC15.models import FileInfo

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
        compiling = compile_thread()
        compiling.compile_all()


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


# Use a new thread to compile all files because the compiling process is slow
class compile_thread(threading.Thread):
    # Attempt to compile all the files
    def compile_all(self):
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