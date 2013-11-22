#Lists all the stories on fimfic, format is ("%d %s %d\n",id,title,wordcount) per story found
# API Story url is : http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/XXX
URL='http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'
id=0
proxy='http://eleve.cpge:cpge@10.145.21.183:8080'
#proxy=''
import urllib.parse,json,sys;from urllib.request import *
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
        id=int(data[id+1:(data[id+1:].find(' ')+id+1)])+1
    print('Resuming from id '+str(id))

# Init
if proxy!='': opener=build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler)
else: opener=build_opener(HTTPBasicAuthHandler(),HTTPHandler)
install_opener(opener)
  
try:
    while True:
        sys.stdout.write('Fetching story '+str(id)+'...')
        sys.stdout.flush()
        data=json.loads(urlopen(Request(('http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'+str(id)))).read().decode("utf-8"))
        try:
            title=data['story']['title'].replace('&#039;','\'').replace('&amp;','&').replace('&quot;','"')
            sys.stdout.write(title+'\n')
            file.write(str(id)+' '+title+' '+str("{:,}".format(data['story']['words']))+'\n')
            file.flush()
        except:
            sys.stdout.write('Not found\n')
        sys.stdout.flush()
        id+=1
except KeyboardInterrupt:
    file.close()
    print('\nScript stopped by user. Press enter to exit.')
    input()