#Lists all the stories on fimfic, format is ("%d %s %d\n",id,title,wordcount) per story found
STORIES_MAXSIZE=150
LOG_EMPTY=False # Log empty stories with 0 words
URL='http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'
id=0
#proxy=''
proxy='http://eleve.cpge:cpge@10.145.21.183:8080'
import urllib.parse,json,sys,threading,time;from urllib.request import *
stories = [] # List of stories waiting to be processed.
nextToDownload=nextToProcess=0
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
                    title=story['story']['title'].replace('&#039;','\'').replace('&amp;','&').replace('&quot;','"').encode('ascii', errors='replace').decode('ascii')
                    print('Story '+str(nextToProcess)+' : '+title)
                    if story['story']['words']!=0 or LOG_EMPTY:
                        file.write(str(nextToProcess)+'\31'+title+'\31'+str("{:,}".format(story['story']['words']))+'\n')
                        file.flush()
                    nextToProcess+=1
                    stories.remove(story)
                else:
                    print('Story '+str(nextToProcess)+' doesn\'t exist')
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