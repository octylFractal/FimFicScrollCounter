username='tux3'
password='Sejymo33'
proxy='http://eleve.cpge:cpge@10.145.21.183:8080' # Example : proxy='http://user:password@proxy.tld:8080'
import urllib.parse,http.cookiejar,http.cookies,sys,os,json;from urllib.request import *
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
    totalWords=0
    
    # TODO: Read stories.txt and loop on the content
    stories=[]
    try: file=open('stories.txt','r')
    except: failWith('Can\'t open stories.txt, aborting') 
    else:
        lines=file.read().splitlines()
        for line in lines:
            stories.append(int(line[:(line.find(' '))]))
    i=1
    for id in stories:
        # Get story metadata
        nStories=len(stories)
        sys.stdout.write('Checking story '+str(id)+' ('+str(i)+'/'+str(nStories)+')')
        sys.stdout.flush()
        story = json.loads(urlopen(Request('http://www.fimfiction.net/api/story.php?story=http://www.fimfiction.net/story/'+str(id))).read().decode("utf-8"))
        if story['story']['words']==0:
            i+=1
            sys.stdout.write('\n')
            continue
        nChapters = len(story['story']['chapters'])
        
        # Check each chapter (print a dot per chapter)
        j=1
        for chapter in story['story']['chapters']:
            id = chapter['id']
            try: opener.open('http://www.fimfiction.net/ajax/toggle_read.php',urllib.parse.urlencode({'chapter':id}).encode('ascii'))
            except: pass
            finally: result=str(opener.open('http://www.fimfiction.net/ajax/toggle_read.php',urllib.parse.urlencode({'chapter':id}).encode('ascii')).read())
            if result.find('tick')!=-1: totalWords+=chapter['words']
            sys.stdout.write('.')
            sys.stdout.flush()
            j+=1
        sys.stdout.write('\n')
        i+=1

except KeyboardInterrupt: failWith('\nTotal words count : '+str("{:,}".format(totalWords)))
except BaseException as e: failWith('Error:'+str(e).encode('ascii', errors='replace').decode('ascii')+'\nPress enter to exit')
finally:
    print('Total words count : '+str("{:,}".format(totalWords)))
    input('Press enter to exit')