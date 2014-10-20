#Lists all the stories on fimfic, format is ("%d %s %d %d %d %d %s\n",id,title,wordcount,likes,dislikes,views,short_description) per story found
# OK parameters from Pothier are 150/1500/5
NTHREADS=50
STORIES_MAXSIZE=500
TIMEOUT=5
LOG_EMPTY=False # Log empty stories with 0 words
LOG_404=True # Log stories not found
URL='http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'
id=0
proxy=''
#proxy='http://eleve.cpge:cpge@10.145.21.183:8080'
import urllib.parse,json,sys,threading,time,os;from urllib.request import *
stories = [] # List of stories waiting to be processed.
threadLock=False # Acquire before modifying variables like nextToDownload from a thread
nextToDownload=nextToProcess=0
def sanitize(str): return str.replace('&#039;','\'').replace('&amp;','&').replace('&quot;','"').encode('ascii', errors='replace').decode('ascii')
def fetchStory(id):
    global stories,nextToDownload,threadLock
    try:
        data=urlopen(Request(('http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'+str(id))),None,TIMEOUT).read().decode("utf-8")
        if data=='{"error":"Invalid story id"}':
            data='{"error":"Invalid story id","story":{"id":'+str(id)+'}}'
        data=json.loads(data)
        stories.append(data)
        # Acquire lock
        while threadLock: time.sleep(0.05)
        threadLock=True
        while len(stories)>=STORIES_MAXSIZE: time.sleep(0.05)
        threading.Thread(None, fetchStory, None, (nextToDownload,)).start()
        nextToDownload+=1
        # Release lock
        threadLock=False
    except Exception as e:
        print(('Error downloading story '+str(id)+':'+str(e)).encode('ascii', errors='replace').decode('ascii'))
        time.sleep(0.01)
        fetchStory(id)

# If stories.txt already exists, resume from the last id found
try:
    file=open('stories.txt','r')
except:
    file=open('stories.txt','w')
    pass
else:
    data=file.read()
    file.close()
    file=open('stories.txt','a')
    id=data.rstrip().rfind('\n')
    if id==-1:
        id=0
    else:
        id=int(data[id+1:(data[id+1:].find('\31')+id+1)])+1
    print('Resuming from id '+str(id))

# Init
nextToDownload=nextToProcess=id
if proxy!='': 
    opener=build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler)
    print('Using proxy : '+proxy)
else: opener=build_opener(HTTPBasicAuthHandler(),HTTPHandler)
install_opener(opener)
while threading.active_count()<NTHREADS:
    threading.Thread(None, fetchStory, None, (nextToDownload,)).start()
    nextToDownload+=1
try:
    while True:
        # Check if we have the next story to be process in stories
        for story in stories:
            if story['story']['id']==nextToProcess:
                try:
                    story['error']
                except:
                    title=sanitize(story['story']['title'])
                    print('Story '+str(nextToProcess)+' : '+title)
                    if story['story']['words']!=0 or LOG_EMPTY:
                        file.write(str(nextToProcess)+'\31'+title+'\31'+str(story['story']['words'])+'\31'+str(story['story']['likes'])+'\31'+str(story['story']['dislikes'])\
                        +'\31'+str(story['story']['views'])+'\31'+sanitize(story['story']['short_description'])+'\n')
                        file.flush()
                    nextToProcess+=1
                    stories.remove(story)
                else:
                    if LOG_404: print('Story '+str(nextToProcess)+' doesn\'t exist')
                    nextToProcess+=1
                    stories.remove(story)
        time.sleep(0.001)
except KeyboardInterrupt:
    file.flush()
    file.close()
    print('\nScript stopped by user. Press enter to exit.')
    input()
    os._exit(0)