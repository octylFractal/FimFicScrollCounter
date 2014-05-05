import urllib.parse
import http.cookiejar
import http.cookies
import sys
from urllib.request import *
cookie=''
def getUrl(url):
    req = Request(url)
    req.add_header('Cookie', cookie+'; view_mature=true')
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
    sys.exit()

def main(username='',password='',proxy='') :
    global cookie
    try :
        if username=='': username=input("Username: ")
        if password=='': password=input("Password: ")
        if proxy!='': 
            opener=build_opener(ProxyHandler({'http':proxy}),HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(http.cookiejar.CookieJar()))
            print('Using proxy : '+proxy)
        else:
            opener=build_opener(HTTPBasicAuthHandler(),HTTPHandler,HTTPCookieProcessor(http.cookiejar.CookieJar()))
        login_data=urllib.parse.urlencode({'username':username,'password':password}).encode('ascii')
        ret=opener.open('http://www.fimfiction.net/ajax/login.php',login_data)
        install_opener(opener)
        if str(ret.read()).find('0') == -1: 
            failWith('Login failed, check your username and password')
        cookie=ret.info()['Set-Cookie']
        print('Connected to FimFiction')
        favData = getUrl('http://www.fimfiction.net/ajax/infocard_user.php?name='+username).replace(',','')
        nFavs=0;curPage=1;nStories=0;totalWords=0;nFavPos=favData.find('=1">')
        if nFavPos>=0: nFavs=int(favData[nFavPos+4:(favData[nFavPos+4:].find(' ')+nFavPos+4)])
        else: failWith('Error finding number of favorites')
        print ('Found '+str(nFavs)+' favorites')
        nPages=-(-nFavs // 10)+curPage
        file=open('readlist.txt','w')
        
        while curPage<=nPages:
            print('Loading page '+str(curPage)+'/'+str(nPages)+'...')
            data=getUrl('http://www.fimfiction.net/index.php?view=category&tracking=1&order=date_added&page='+str(curPage))
            data=data.replace(r'\t','').replace(r'\r','').replace(r'\n','').replace('&#039;','\'').replace('&amp;','&').replace('&quot;','"')
            indexes=findAll(data,r'word_count"><b>')
            indexes2=findAll(data,r'data-minimum-size="0.5">')
            if len(indexes)!=len(indexes2):
                j=-1
                print('Error parsing page '+str(curPage)); file.write('Error parsing page '+str(curPage))
            j=0;curPage+=1;
            for i in indexes:
                num=data[i+15:(data[i+15:].find('<')+i+15)]
                totalWords+=int(num.replace(',',''))
                if (j>=0):
                    ji=indexes2[j]+24
                    title=data[ji:(data[ji:].find('<')+ji)]
                    file.write(title+' '+num+'\n')
                    j+=1
        
        file.write('Total words count : '+str(str("{:,}".format(totalWords))))
        file.close()
        print('Total words count : '+str("{:,}".format(totalWords)))
        input('Press enter to exit')
    except BaseException as e:
        failWith('Error:'+str(e).encode('ascii', errors='replace').decode('ascii')+'\nPress enter to exit')
if __name__ == "__main__" :
    main()