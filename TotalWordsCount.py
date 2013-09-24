import urllib.request
import urllib.parse
import http.cookiejar
import http.cookies
import sys
import re

cookie=''
username=''
password=''
#proxy='http://user:password@proxy.tld:8080'
proxy=''

def init():
    opener=0
    cj = http.cookiejar.CookieJar()
    auth = urllib.request.HTTPBasicAuthHandler()
    if proxy != '':
        proxyh = urllib.request.ProxyHandler({'http': proxy})
        opener = urllib.request.build_opener(proxyh, auth, urllib.request.HTTPHandler, urllib.request.HTTPCookieProcessor(cj))
    else:
        opener = urllib.request.build_opener(auth, urllib.request.HTTPHandler, urllib.request.HTTPCookieProcessor(cj))
    login_data = urllib.parse.urlencode({'username':username, 'password':password})
    blogin_data = login_data.encode('ascii')
    ret = opener.open('http://www.fimfiction.net/ajax/login.php', blogin_data)
    urllib.request.install_opener(opener)
    if str(ret.read()).find('0') == -1:
        sys.exit('Login failed, check your username and password')
    
    global cookie
    cookie=ret.info()['Set-Cookie']
    
def getUrl(url):
    req = urllib.request.Request(url)
    req.add_header('Cookie', cookie+'; view_mature=true')
    conn = urllib.request.urlopen(req)
    return str(conn.read())

def findAll(string, sub, listindex=[], offset=0):
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex    
    
def addCommas(quantity):
    return "{:,}".format(quantity)

# Init
if username=='':
    username = input("Username: ")
if password=='':
    password = input("Password: ")
init()
print('Connected to FimFiction')

# Get number of favorites
favData = getUrl('http://www.fimfiction.net/ajax/infocard_user.php?name=tux3')
nFavs=0
nFavPos=favData.find('=1">')
if nFavPos>=0:
    nFavs=int(favData[nFavPos+4:(favData[nFavPos+4:].find(' ')+nFavPos+4)])
else:
    sys.exit('Error finding number of favorites')
print ('Found '+str(nFavs)+' favorites')

# Load each page of favorites and for each count number of stories
nPages=-(-nFavs // 10)
curPage=1
nStories=0
totalWords=0
while curPage<=nPages:
    print('Loading page '+str(curPage)+'/'+str(nPages)+'...')
    url = 'http://www.fimfiction.net/index.php?view=category&tracking=1&order=updated&page='+str(curPage)
    data=getUrl(url)
    data=data.replace(r'\t','')
    data=data.replace(r'\r\n','')
    indexes=findAll(data,r'word_count"><b>')
    pageWords=0
    for i in indexes:
        num=data[i+15:(data[i+15:].find('<')+i+15)]
        #print('Found at '+str(i)+' : '+num)
        pageWords+=int(num.replace(',',''))
    indexes[:] = []
    totalWords+=pageWords
    #print('Page words count : '+str(pageWords))
    curPage+=1
    
print('Total words count : '+str(addCommas(totalWords)))

# http://www.fimfiction.net/index.php?view=category&tracking=1&order=updated&page=X