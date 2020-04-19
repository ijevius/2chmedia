import os
import sys
import json
import uuid
import platform
import urllib.request

usercode_auth = ""
adult_boards = ['fur', 'fet']
DIRS_SEPARATOR = '\\' if "Windows" in platform.system() else '//'
DVACH_MIRROR = "2ch.hk"
DVACH_GET_THREAD_URL = f'https://{DVACH_MIRROR}/%s/res/%d.json'
board, thr = '', 0
ignoreExisting = ""

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

def fileDownload(source, dir, name, repeatingNames):
    if os.path.exists(dir + name):
        if os.path.getsize(dir + name) == 0:
            os.remove(dir + name)
        else:
            if repeatingNames:
                ext = "." + name.split('.')[-1]
                name += uuid.uuid1().hex + ext
            else:
                print(f"{name} already exists")
                return
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
ignoreExisting = input("Если в этом треде могут быть разные файлы под одним именем, введите 1.\n")
print(ignoreExisting == "1")
ignoreExisting = True if ignoreExisting == "1" else False
if board in adult_boards:
    print("Чтобы смотреть некоторые доски, нужно написать любой пост и вставить сюда cookie=usercode_auth")
    usercode_auth = input()
createDirIfNotExists("2ch")
createDirIfNotExists(f"2ch{DIRS_SEPARATOR}{board}")
#createDirIfNotExists(f"2ch{DIRS_SEPARATOR}{board}{DIRS_SEPARATOR}{thr}")
DVACH_GET_THREAD_URL = DVACH_GET_THREAD_URL % (board, thr)
print(DVACH_GET_THREAD_URL)
r_headers = {"Cookie": ""}

opener = urllib.request.build_opener()
opener.addheaders.append(('Cookie', f'usercode_auth={usercode_auth}; ageallow=1'))
respone = "server response"
try:
    response = json.loads(opener.open(DVACH_GET_THREAD_URL).read())
except:
    print("Тред или доска не существует, или usercode_auth неверный")
    sys.exit(0)
print(response["threads"])
thr_name = response["threads"][0]["posts"][0]["subject"]
DIR_FOR_THREAD = f"2ch{DIRS_SEPARATOR}{board}{DIRS_SEPARATOR}{thr} -- {makeNamePretty(thr_name)}{DIRS_SEPARATOR}"
createDirIfNotExists(DIR_FOR_THREAD)
withMedia = 0
for item in response["threads"][0]["posts"]:
    files = item["files"]
    if len(files) > 0:
        for file in files:
            origname = file["fullname"]
            origname = makeNamePretty(origname)
            url = f'https://{DVACH_MIRROR}{file["path"]}'
            fileDownload(url, DIR_FOR_THREAD, origname, ignoreExisting)
        withMedia+=1
        print(files)

print(withMedia)
