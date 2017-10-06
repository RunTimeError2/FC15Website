import os
import threading
from FC15.models import FileInfo

IS_RUNNING = 0


# Start running
def run():
    global IS_RUNNING
    if IS_RUNNING == 0:
        IS_RUNNING = 1
        compiling = compile_thread()
        compiling.compile_all()


# Copy file
def copy_file(username, file_name):
    source_dir = 'fileupload/{0}/{1}'.format(username, file_name)
    destin_dir = 'cpp_proj/cpp_proj/main.cpp'
    if os.path.isfile(source_dir):
        open(destin_dir, 'wb').write(open(source_dir, 'rb').read())
        return True
    else:
        return False


# Copy exe file
def copy_exe(username, file_name):
    source_dir = 'cpp_proj/Debug/cpp_proj.exe'
    destin_dir = 'fileupload/{0}/{1}.exe'.format(username, file_name[:-4])
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
                if file.is_compiled == '未编译':
                    is_done = True
                    copy_result = copy_file(file.username, file.exact_name)
                    if copy_result:
                        # use visual studio to compile the project
                        compile_result = os.system('devenv cpp_proj/cpp_proj.sln /rebuild > result.txt')
                        file.is_compiled = '已编译'
                    if compile_result == 0:
                        file.is_compile_success = '编译成功'
                        copy_exe(file.username, file.exact_name)
                    else:
                        file.is_compile_success = '编译失败'
                    file.save()
        IS_RUNNING = 0