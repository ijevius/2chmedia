import os
import sys
import json
import uuid
import platform
import urllib.request

usercode_auth = ""
adult_boards = ['fur', 'fet']
DIRS_SEPARATOR = '\\' if "Windows" in platform.system() else '/' 
DVACH_MIRROR = "2ch.hk"
board, thr = '', 0
DVACH_GET_THREAD_URL_2 = f"https://{DVACH_MIRROR}/makaba/mobile.fcgi?task=get_thread&board=%s&thread=%d&post=%d"

def getLast(b, t):
    #t - только номер треда
    result = 1
    path = f"2ch{DIRS_SEPARATOR}{b}{DIRS_SEPARATOR}{t}last"
    if os.path.exists(path):
        f = open(path, "r")
        c_l = f.read()
        result = int(c_l)
        f.close()
    else:
        print(f"Этот тред еще не сохранялли")
    print(f"Тред {t} на доске {b} start from {result}")
    return result

def writeLast(b, t, l):
    path = f"2ch{DIRS_SEPARATOR}{b}{DIRS_SEPARATOR}{t}last"
    summary = l
    if os.path.exists(path):
        f = open(path, "r")
        c_l = f.read()
        result = int(c_l)
        summary += result-1
        f.close()
    f = open(path, 'w')
    f.write(str(summary))
    f.close()
    print(f"Wrote last for {b}/{t} is {summary}")

def createDirIfNotExists(dirName):
    isDir = os.path.isdir(dirName)
    if not isDir:
        try:
            os.mkdir(dirName)
            #print(f"{dirName} at {os.getcwd()} created")
        except:
            print(f"dcreat: Can't create {dirName}")
    else:
        print(f"dcreat: Dir {os.getcwd()}{DIRS_SEPARATOR}{dirName} is already exists")

def makeNamePretty(str):
    not_allowed = '!@#$&~%*()[]{}\'"\:;<>`' #and space?
    if "Windows" in platform.system():
        not_allowed = '/\:*?"|<>'
    for sym in not_allowed:
        if sym in str:
            str = str.replace(sym, "")
    #return str+"(name mod)"
    return str

def fileDownload(source, dir, name):
    if os.path.exists(dir + name):
        if os.path.getsize(dir + name) == 0:
            os.remove(dir + name)
        else:
            print(f"One more file with name = {name}")
            ext = "." + name.split('.')[-1]
            name += uuid.uuid1().hex + ext
    try:
        opener = urllib.request.build_opener()
        opener.addheaders.append(('Cookie', f'usercode_auth={usercode_auth}; ageallow=1'))
        cont = opener.open(source).read()
        f = open(f"{dir}{DIRS_SEPARATOR}{name}", "wb")
        f.write(cont)
        f.close()
        print(f"{name} saved")
    except:
        print(f"Can't write and close file from url={source}")

print('Через пробел укажите доску и номер треда.')
board, thr = input().split(); thr = int(thr)
if board in adult_boards:
    print("Чтобы смотреть некоторые доски, нужно написать любой пост и вставить сюда cookie=usercode_auth")
    usercode_auth = input()
createDirIfNotExists("2ch")
createDirIfNotExists(f"2ch{DIRS_SEPARATOR}{board}")
last_synced_post_for_thread = getLast(board, thr)
DVACH_GET_THREAD_URL_2 = DVACH_GET_THREAD_URL_2 % (board, thr, last_synced_post_for_thread)
print(DVACH_GET_THREAD_URL_2)

opener = urllib.request.build_opener()
opener.addheaders.append(('Cookie', f'usercode_auth={usercode_auth}; ageallow=1'))
response = "server response here"
try:
    response = json.loads(opener.open(DVACH_GET_THREAD_URL_2).read())
except:
    print("Тред или доска не существует, или usercode_auth неверный")
    sys.exit(0)
print(response)
if len(response) == 0:
    print("Нет новых постов");
    sys.exit(0)
thr_name = response[0]["subject"]
DIR_FOR_THREAD = f"2ch{DIRS_SEPARATOR}{board}{DIRS_SEPARATOR}{thr}{DIRS_SEPARATOR}"

createDirIfNotExists(DIR_FOR_THREAD)
withMedia = 0
total = 1
for item in response:
    files = item["files"]
    if len(files) > 0:
        for file in files:
            origname = file["fullname"]
            origname = makeNamePretty(origname)
            url = f'https://{DVACH_MIRROR}{file["path"]}'
            fileDownload(url, DIR_FOR_THREAD, origname)
        withMedia+=1
        print(files)
    total += 1
writeLast(board, thr, total)

print(f"{withMedia} with media")
