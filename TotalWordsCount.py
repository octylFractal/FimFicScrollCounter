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
    req.add_header('Cookie', 'view_mature=true')
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

def failWith(stri):
    print(stri)
    if input("Press enter to exit") == "debug" :
        raise AssertionError(stri)
    sys.exit()

def get_opener(proxy):
    if proxy!='':
        opener = build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(cookiejar.CookieJar()))
        print('Using proxy: ' + proxy)
    else:
        opener = build_opener(HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(cookiejar.CookieJar()))
    return opener

def findFavCount():
    raise NotImplementedError('findFavCount not done')

def deterPageCount(favCount):
    raise NotImplementedError('deterPageCount not done')

def findAllLinks(pageData):
    raise NotImplementedError('findAllLinks not done')

def loadStory(pageData):
    raise NotImplementedError('loadStory not done')

def main(method=TOTAL_WORDS_READ,proxy='') :
    try :
        opener = get_opener(proxy)
        # setup login
        install_opener(opener)
        print('Connected to FimFiction')
        # load fav data
        nFavs = 0
        curPage = 1
        nStories = 0
        counter = 0
        # check for favs
        nFavs = findFavCount()
        print ('Found ' + str(nFavs) + ' favorites')
        nPages = deterPageCount(nFavs)
        file = open('readlist.txt','w')

        allstorylinks = []
        # read favs
        while curPage <= nPages:
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
