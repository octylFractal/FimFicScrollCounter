#Lists all the stories on fimfic, format is ("%d %s %d %d %d %d %s\n",id,title,wordcount,likes,dislikes,views,short_description) per story found
STORIES_MAXSIZE=500
LOG_EMPTY=False # Log empty stories with 0 words
LOG_404=False # Log stories not found
URL='http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'
id=0
#proxy=''
proxy='http://eleve.cpge:cpge@10.145.21.183:8080'
import urllib.parse,json,sys,threading,time;from urllib.request import *
stories = [] # List of stories waiting to be processed.
nextToDownload=nextToProcess=0
def sanitize(str): return str.replace('&#039;','\'').replace('&amp;','&').replace('&quot;','"').encode('ascii', errors='replace').decode('ascii')
def fetchStory(id):
    global stories
    global nextToDownload
    #print('Downloading story '+str(id)+'...')
    try:
        data=urlopen(Request(('http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'+str(id)))).read().decode("utf-8")
        if data=='{"error":"Invalid story id"}':
            data='{"error":"Invalid story id","story":{"id":'+str(id)+'}}'
        data=json.loads(data)
        stories.append(data)
        #print('Downloaded story '+str(id))
    except Exception as e:
        print(('Error downloading story '+str(id)+':'+str(e)).encode('ascii', errors='replace').decode('ascii'))
        if id<nextToDownload:
            nextToDownload=id
        stories[:]=[]

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
                
        while nextToDownload-nextToProcess < STORIES_MAXSIZE:
            threading.Thread(None, fetchStory, None, (nextToDownload,)).start()
            nextToDownload+=1
        time.sleep(0.01)
except KeyboardInterrupt:
    file.close()
    print('\nScript stopped by user. Press enter to exit.')
    input()