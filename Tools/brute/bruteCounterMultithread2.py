username='tux3'
password='Sejymo33'
proxy=''
proxy='http://eleve.cpge:cpge@10.145.21.183:8080' # Example : proxy='http://user:password@proxy.tld:8080'
import urllib.parse,http.cookiejar,http.cookies,sys,os,json,threading;from urllib.request import *
curStories=[] # Stories being processed, format ('%d,%d,[],%d',id,nChaptersChecked,chapters[],wordsRead)
totalWords=0
STORIES_SIZE=5
LOG_UNREAD=False
def getUrl(url):
    req = Request(url)
    conn = urlopen(req)
    return str(conn.read())
def findAll(string, sub, offset=0):
    listindex=[]
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex    
def failWith(str):
    input(str)
    os._exit(0)
def checkChapter(chapter,storyId):
    global totalWords
    global curStories
    words=0
    id = chapter['id']
    try: opener.open('http://www.fimfiction.net/ajax/toggle_read.php',urllib.parse.urlencode({'chapter':id}).encode('ascii'))
    except: pass
    finally: result=str(opener.open('http://www.fimfiction.net/ajax/toggle_read.php',urllib.parse.urlencode({'chapter':id}).encode('ascii')).read())
    if result.find('tick')!=-1: words+=chapter['words']
    totalWords+=words
    for story in curStories:
        if story[0]==storyId:
            story[1]+=1
            story[3]+=words
            break
def checkStory(id):
    global curStories,nextToProcess,nextToPreload,stories,storiesSize
    #print('Downloading story '+str(id))
    story = json.loads(urlopen(Request('http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'+str(id))).read().decode("utf-8"))
    for curStory in curStories:
        if curStory[0]==id:
            curStory[1]=0 # Set state to chapters loading
            if story['story']['words']!=0: 
                curStory[2]=story['story']['chapters']
                for chapter in curStory[2]:
                    threading.Thread(None, checkChapter, None, (chapter,id)).start()
            else:
                # Just process this one now since it's empty, and flag it for deletion
                curStory[1]=0
                curStory[2]=[]
                break
            
try:
    if username=='': username=input("Username: ")
    if password=='': password=input("Password: ")
    if proxy!='': 
        opener=build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(http.cookiejar.CookieJar()))
        print('Using proxy : '+proxy)
    else: opener=build_opener(HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(http.cookiejar.CookieJar()))
    login_data=urllib.parse.urlencode({'username':username,'password':password}).encode('ascii')
    ret=opener.open('http://www.fimfiction.net/ajax/login.php',login_data)
    install_opener(opener)
    if str(ret.read()).find('0') == -1: failWith('Login failed, check your username and password')
    cookie=ret.info()['Set-Cookie']
    print('Connected to FimFiction')
    
    # TODO: Read stories.txt and loop on the content
    stories=[]
    try: file=open('stories.txt','r')
    except: failWith('Can\'t open stories.txt, aborting') 
    else:
        lines=file.read().splitlines()
        for line in lines:
            stories.append(int(line[:(line.find(' '))]))
    print('Found '+str(len(stories))+' stories')
    nextToPreload=nextToProcess=0
    storiesSize=len(stories)
    logfile=open('readlistBrute.txt','w')
    # Start preloading
    while nextToPreload<STORIES_SIZE and nextToPreload<storiesSize:
        curStories.append([stories[nextToPreload],-2,[],0])
        threading.Thread(None, checkStory, None, (stories[nextToPreload],)).start()
        nextToPreload+=1
    # Main loop
    while nextToProcess<storiesSize:                        
        # Process curStories
        for curStory in curStories:
            # Try to process the current story
            if curStory[0]==stories[nextToProcess]:
                if curStory[1]>=len(curStory[2]): # Chapters loaded
                    # Preload a new story
                    if nextToPreload<storiesSize:
                        curStories.append([stories[nextToPreload],-2,[],0])
                        threading.Thread(None, checkStory, None, (stories[nextToPreload],)).start()
                        nextToPreload+=1
                    # Process current story
                    curStories.remove(curStory)
                    print('Story '+str(curStory[0])+' ('+str(nextToProcess+1)+'/'+str(len(stories))+') : '+str("{:,}".format(curStory[3]))+' words read')
                    if LOG_UNREAD or curStory[3]!=0:
                        logfile.write(str(curStory[0])+' '+str("{:,}".format(curStory[3]))+'\n')
                        logfile.flush()
                    nextToProcess+=1
                else: # Story found, but chapters still loading
                    time.sleep(0.005)
                    continue
    file.close()
    logfile.close()
except KeyboardInterrupt: failWith('\nTotal words count : '+str("{:,}".format(totalWords)))
finally:
    print('\nTotal words count : '+str("{:,}".format(totalWords)))
    input('Press enter to exit')