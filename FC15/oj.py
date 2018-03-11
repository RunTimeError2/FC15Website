import os, time, random
import threading
from FC15.models import FileInfo, AIInfo, GameRecord
from queue import Queue # Python3
#from Queue import Queue # Python2


IS_RUNNING = 0
GAME_RUNNING = 0
#COMPILE_MODE = 'VS'
COMPILE_MODE = 'G++'
FILE_SUFFIX = 'dll'
RECORD_SUFFIX = 'txt' # maybe should be changed to 'json'
DEFAULT_RECORD_FILENAME = 'gamerecord.txt'
# FILE_SUFFIX = 'exe'
GAME_QUEUE = Queue()


class SingleGameInfo(object):
    username = ''
    ai_list = []


# Start running
def run():
    global IS_RUNNING
    if IS_RUNNING == 0:
        IS_RUNNING = 1
        t = threading.Thread(target = compile_all)
        t.start()


# Run all games in the queue, should be put into a new thread
def run_game():
    global GAME_RUNNING
    global GAME_QUEUE
    while GAME_QUEUE.empty() == False:
        gameinfo = GAME_QUEUE.get()
        # Launch game
        result = launch_game(gameinfo.ai_list, gameinfo.username)
        # Generate game record
        record = GameRecord()
        record.username = gameinfo.username
        record.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        if result == 0:
            record.state = 'Success'
        elif result == -1:
            record.state = 'Failed to Launch game'
        elif result == 1:
            record.state = 'Runtime Error'
        else:
            record.state = 'Unknown state'
        now = time.strftime('%Y%m%d%H%M%S')
        file_name = 'record{0}_{1}.{2}'.format(now, random.randint(0, 1000), RECORD_SUFFIX)
        while os.path.exists('gamerecord/{0}'.format(file_name)):
            file_name = 'record{0}_{1}.{2}'.format(now, random.randint(0, 1000), RECORD_SUFFIX)
        destin_dir = 'gamerecord/' + file_name
        source_dir = 'playgame/' + DEFAULT_RECORD_FILENAME
        # Copy record file
        if os.path.exists(source_dir):
            open(destin_dir, 'wb').write(open(source_dir, 'rb').read())
            try:
                os.remove(source_dir) # delete source file, avoid problems when playing game next time (sometimes the sample 'logic' fails to create record file)
            except:
                pass
        else:
            record.state = 'Failed to Launch game'
        record.filename = file_name
        record.save()
    GAME_RUNNING = 0


# Copy file
def copy_file(username, file_name):
    global COMPILE_MODE
    source_dir = 'fileupload/{0}/{1}'.format(username, file_name)
    if COMPILE_MODE == 'VS':
        destin_dir = 'cpp_proj/ai/ai.cpp'
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
        source_dir = 'cpp_proj/Release/ai.' + FILE_SUFFIX
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
        if os.path.exists('/playgame/{0}.{1}'.format(file_object.pk, FILE_SUFFIX)):
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
                        compile_result = os.system('devenv cpp_proj/ai.sln /rebuild > result.txt')
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


# Add game infomation into waiting queue
def play_game(ai_list, username):
    global GAME_RUNNING
    queue_item = SingleGameInfo()
    queue_item.ai_list = ai_list
    queue_item.username = username
    GAME_QUEUE.put(queue_item)
    if GAME_RUNNING == 0:
        GAME_RUNNING = 1
        t = threading.Thread(target = run_game)
        t.start()


# Launch logic once
def launch_game(ai_list, username):
    exe_path = 'playgame\logic.exe' # should be 'playgame/logic.exe' on Ubuntu

    # parameters
    startgame_failure = -1
    result_success = 0
    result_runtimeerror = 1
    # there should be more

    # only for Debugging =================================================================
    print('Launch game: AI List')
    print(ai_list)
    print('username = ')
    print(username)

    cmd = exe_path + ' '
    if ai_list:
        # genereate command to launch logic
        for item in ai_list:
            cmd = cmd + '{0} '.format(item)
        # launch logic
        result = os.system(cmd)
        print(cmd)
        return result
    else:
        return startgame_failure