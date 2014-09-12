import py2to3compat
py2to3compat.fix(__builtins__)
if py2to3compat.PYTHON_VERSION_MAJOR > 2:
    # uses new name
    import urllib.parse as parse
    from http import cookiejar, cookies
    from urllib.request import *
else:
    import urllib as parse
    # uses py3 name
    import cookielib as cookiejar
    # uses py3 name
    import Cookie as cookies
    from urllib2 import *
import sys
import re
import math

# some differnt data getters
TOTAL_WORDS_READ = "totalWords"
PARTIALLY_READ_STORIES = "partialStories"

cookie=''
fimbase = 'https://www.fimfiction.net'

# cache for multiple runs in one go
urlCache = {}
def resetCache():
    global urlCache
    urlCache = {}

def getUrl(url):
    global urlCache
    if url in urlCache.keys() :
        return urlCache[url]
    req = Request(url)
    req.add_header('Cookie', cookie+'; view_mature=true')
    conn = urlopen(req)
    res = str(conn.read()).replace(r'\t','') \
               .replace('\r','') \
               .replace('\n','') \
               .replace(r'\r','') \
               .replace(r'\n','') \
               .replace('&#039;','\'') \
               .replace('&amp;','&') \
               .replace('&quot;','"')
    urlCache[url] = res
    return res
    
def findAll(string, sub, offset=0):
    listindex=[]
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex

# block read list
waituntilpat = re.compile(r'<table +class *= *[\'"]browse_stories[\'"]', re.DOTALL | re.MULTILINE)
linkpat = re.compile(r'<a +href *= *[\'"](.+?)[\'"]', re.DOTALL | re.MULTILINE)

def findAllLinks(pageData):
    starthere = waituntilpat.search(pageData).start()
    return linkpat.findall(pageData, starthere)

storytitlepat = re.compile(r'<a class="story_name.+?>(.+?)</a>', re.DOTALL | re.MULTILINE)
chapterpat = re.compile(r'<div class="word_count">\s*?(?!<b>)(.+?)<', re.DOTALL | re.MULTILINE)
strictcpat = re.compile(r'<i class=.+?chapter-read(?!-icon).+?<div class="word_count">\s*?(?!<b>)(.+?)<', re.DOTALL | re.MULTILINE)
storywcpat = re.compile(r'<div class="word_count">\s*?<b>(.+?)<', re.DOTALL | re.MULTILINE)

def loadStory(storyData):
    """
    Returns a tuple of data:
    (word count, read word count, title)
    """
    title = storytitlepat.findall(storyData)[0]
    chapterwordcnt = chapterpat.findall(storyData)
    chapterwordcnt = [int(deprettify(x)) for x in chapterwordcnt if x.strip() != '']
    chapterwcadd = sum(chapterwordcnt)
    storywordcnt = int(deprettify(storywcpat.findall(storyData)[0]))
    if chapterwcadd != storywordcnt :
        print('Chapters added != Story Word Count')
        return (storywordcnt, 0, title)
    strictwc = 0
    strictchwc = strictcpat.findall(storyData)
    strictchwc = [int(deprettify(x)) for x in strictchwc if x.strip() != '']
    strictwc = sum(strictchwc)
    return (chapterwcadd, strictwc, title)

def deprettify(numstr):
    return numstr.replace(',', '').strip()

def prettify(num):
    return "{:,}".format(num)

def getPage(pagenum):
    # pull page
    data = getUrl(
        fimbase + '/index.php?view=category&tracking=1&compact_view=1&order=date_added&page='
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
        return int(math.ceil(float(storyCount) / float(storiesPerPage)))
    else:
        raise SyntaxError()
    
def failWith(stri):
    print(stri)
    if input("Press enter to exit") == "debug" :
        raise AssertionError(stri)
    sys.exit()

globdebug = dict()

def main(username='',password='',method=TOTAL_WORDS_READ,proxy='') :
    global cookie, globdebug
    try :
        # request basic data
        if username=='': username = input("Username: ")
        if password=='': password = input("Password: ")
        # proxy
        if proxy!='': 
            opener = build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(cookiejar.CookieJar()))
            print('Using proxy : ' + proxy)
        else:
            opener = build_opener(HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(cookiejar.CookieJar()))
        # setup login
        login_data = parse.urlencode({'username':username,'password':password}).encode('ascii')
        ret = opener.open(fimbase + '/ajax/login.php',login_data)
        install_opener(opener)
        # check fail
        if str(ret.read()).find('0') == -1: 
            failWith('Login failed, check your username and password')
        cookie=ret.info()['Set-Cookie']
        print('Connected to FimFiction')
        # load fav data
        favData = getUrl(fimbase + '/ajax/infocard_user.php?name='+username).replace(',','')
        nFavs = 0
        curPage = 1
        nStories = 0
        counter = 0
        # check for favs
        favURLRegex = r'<a href="(/index.php\?view=category&user=\d+&tracking=1)">\d+ favourites'
        favURLResult = re.search(favURLRegex, favData, re.MULTILINE)
        favNumRegex = r'<div class="search_results_count">\s+Viewing <b>\d+</b> - <b>\d+</b> of <b>(\d+)</b> stories\s+</div>'
        if favURLResult != None:
            nFavs = int(re.search(favNumRegex, getUrl(fimbase + favURLResult.group(1)), re.MULTILINE).group(1))
        else:
            print(favData)
            raise LookupError('Error finding number of favorites')
        print ('Found ' + str(nFavs) + ' favorites')
        nPages = deterPageCount(nFavs)
        file = open('readlist.txt','w')

        allstorylinks = []

        globdebug['links'] = allstorylinks
        
        # read favs
        while curPage<=nPages:
            print('Loading page ' + str(curPage) + '/' + str(nPages) + '...')
            data = getPage(curPage)
            links = findAllLinks(data)
            links = [fimbase + x for x in links if x.find('story') > 0]
            allstorylinks += links
            curPage += 1

        if len(allstorylinks) < nFavs:
            raise ValueError(str(len(allstorylinks)) + "<" + str(nFavs))

        procd = 0
        lastput = 0

        # process favs
        print('Processing...')
        for lnk in allstorylinks:
            globdebug['lastlink'] = lnk
            data = getUrl(lnk)
            sdata = loadStory(data)
            writestr = None
            if method == TOTAL_WORDS_READ:
                writestr = totalLoop(sdata)
            elif method == PARTIALLY_READ_STORIES:
                writestr = partialLoop(sdata)
            if writestr != None:
                file.write(writestr + '\n')
                print(writestr)
                if method == TOTAL_WORDS_READ:
                    counter += totalInc(sdata)
                elif method == PARTIALLY_READ_STORIES:
                    counter += partialInc(sdata)
            if math.floor((float(procd) / float(len(allstorylinks))) * 100) > lastput + 5:
                lastput = math.floor((float(procd) / float(len(allstorylinks))) * 100)
                print('About ' + str(lastput) + '% done')
            procd += 1

        
        if method == TOTAL_WORDS_READ:
            writestr = totalEnd(counter)
        elif method == PARTIALLY_READ_STORIES:
            writestr = partialEnd(counter)

        file.write(writestr + '\n')
        file.close()
        print(writestr)
        input('Press enter to exit')
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        reraise = False
        try :
            failWith('Error: ' + str(e).encode('ascii', errors='replace').decode('ascii'))
        except SystemExit:
            pass
        except AssertionError:
            reraise = True
        if reraise :
            raise
def partialLoop(storyData):
    if storyData[1] < storyData[0] and storyData[1] != 0:
        return 'Partially read: ' + prettify(storyData[1]) + '/' + prettify(storyData[0]) + ' words read of "' + storyData[2] + '"'
    return None
def partialEnd(counter):
    return 'Total partially read stories count: ' + prettify(counter)
def partialInc(storyData):
    return 1
def totalLoop(storyData):
    return prettify(storyData[1]) + '/' + prettify(storyData[0]) + ' words read of "' + storyData[2] + '"'
def totalEnd(counter):
    return 'Total words read: ' + prettify(counter)
def totalInc(storyData):
    return storyData[1]

if __name__ == "__main__" :
    main()
