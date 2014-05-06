import urllib.parse
import http.cookiejar
import http.cookies
import sys
import re
import math
from urllib.request import *
cookie=''
fimbase = 'http://www.fimfiction.net'

def getUrl(url):
    req = Request(url)
    req.add_header('Cookie', cookie+'; view_mature=true')
    conn = urlopen(req)
    return str(conn.read()).replace(r'\t','') \
               .replace(r'\r','') \
               .replace(r'\n','') \
               .replace('&#039;','\'') \
               .replace('&amp;','&') \
               .replace('&quot;','"')
    
def findAll(string, sub, offset=0):
    listindex=[]
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex

linkpat = re.compile('<a +href *= *[\'"](.+?)[\'"]')

def findAllLinks(pageData):
    return linkpat.findall(pageData)

storytitlepat = re.compile('<a class="story_name.+?>(.+?)</a>')
chapterpat = re.compile('<div class="word_count">(?!<b>)(.+?)<')
strictcpat = re.compile('<i class=.+?chapter-read(?!-icon).+?<div class="word_count">(?!<b>)(.+?)<')
storywcpat = re.compile('<div class="word_count"><b>(.+?)<')

def loadStory(storyData):
    """
    Returns a tuple of data:
    (word count, read word count, title)
    """
    title = storytitlepat.findall(storyData)[0]
    chapterwordcnt = chapterpat.findall(storyData)
    chapterwordcnt = [int(deprettify(x)) for x in chapterwordcnt]
    chapterwcadd = sum(chapterwordcnt)
    storywordcnt = int(deprettify(storywcpat.findall(storyData)[0]))
    if chapterwcadd != storywordcnt :
        print('Chapters added != Story Word Count')
        return (storywordcnt, 0, title)
    strictchwc = strictcpat.findall(storyData)
    strictchwc = [int(deprettify(x)) for x in strictchwc]
    strictwc = sum(strictchwc)
    return (chapterwcadd, strictwc, title)

def deprettify(numstr):
    return numstr.replace(',', '')

def prettify(num):
    return "{:,}".format(num)

def getPage(pagenum):
    # pull page
    data = getUrl(
        'http://www.fimfiction.net/index.php?view=category&tracking=1&compact_view=1&order=date_added&page='
        + str(pagenum))
    return data

def deterPageCount(storyCount):
    page1 = getPage(1)

    # decode story count
    # find title links in HTML
    indexes=findAll(page1,r'class="title">')

    # this matches the heading title as well
    # so we remove it
    indexes = indexes[1:]
    # find word count in html
    indexes2=findAll(page1,r'class="info">')
    # story count mismatch check
    # usually indicates site layout change
    if len(indexes) == len(indexes2):
        storiesPerPage = len(indexes)
        if storiesPerPage == 0 :
            return 0
        return math.ceil(storyCount / storiesPerPage)
    else:
        raise SyntaxError()
    
def failWith(stri):
    if input(stri) == "debug" :
        raise RuntimeError()
    sys.exit()

def main(username='',password='',proxy='') :
    global cookie
    try :
        # request basic data
        if username=='': username = input("Username: ")
        if password=='': password = input("Password: ")
        # proxy
        if proxy!='': 
            opener = build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(http.cookiejar.CookieJar()))
            print('Using proxy : ' + proxy)
        else:
            opener = build_opener(HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(http.cookiejar.CookieJar()))
        # setup login
        login_data = urllib.parse.urlencode({'username':username,'password':password}).encode('ascii')
        ret = opener.open('http://www.fimfiction.net/ajax/login.php',login_data)
        install_opener(opener)
        # check fail
        if str(ret.read()).find('0') == -1: 
            failWith('Login failed, check your username and password')
        cookie=ret.info()['Set-Cookie']
        print('Connected to FimFiction')
        # load fav data
        favData = getUrl('http://www.fimfiction.net/ajax/infocard_user.php?name='+username).replace(',','')
        nFavs = 0
        curPage = 1
        nStories = 0
        totalWords = 0
        # check for favs
        favRegex = '^.*?(\d+) fav.*$'
        if re.search(favRegex, favData) != None:
            nFavs = int(re.sub(favRegex, '\\1', favData))
        else:
            failWith('Error finding number of favorites')
        print ('Found ' + str(nFavs) + ' favorites')
        nPages = deterPageCount(nFavs)
        file = open('readlist.txt','w')

        allstorylinks = []
        
        # read favs
        while curPage<=nPages:
            print('Loading page ' + str(curPage) + '/' + str(nPages) + '...')
            data = getPage(curPage)
            links = findAllLinks(data)
            links = [fimbase + x for x in links if x.find('story') > 0]
            allstorylinks += links
            curPage += 1

        # process favs
        for lnk in allstorylinks:
            data = getUrl(lnk)
            sdata = loadStory(data)
            writestr = prettify(sdata[1]) + '/' + prettify(sdata[0]) + ' words read of "' + sdata[2] + '"'
            file.write(writestr + '\n')
            print(writestr)
            totalWords += sdata[1]

        file.write('Total words count : ' + str("{:,}".format(totalWords)))
        file.close()
        print('Total words count : '+str("{:,}".format(totalWords)))
        input('Press enter to exit')
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        try :
            failWith('Error:'+str(e).encode('ascii', errors='replace').decode('ascii')+'\nPress enter to exit')
        except SystemExit:
            pass
if __name__ == "__main__" :
    main()
