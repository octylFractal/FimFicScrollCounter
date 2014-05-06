#!/usr/bin/env python3
# TODO: Filters, like only certain tags/completion status/rating(Teen,...)
import sys,os
def failWith(str):
    input(str)
    os._exit(0)
# Build a stories list in memory from stories.txt
stories=[]
try: file=open('stories.txt','r')
except: failwith('Can\'t open stories.txt')
lines = file.read().splitlines()
file.close()
for line in lines:
    story=line.split('\31')
    stories.append(story)

# Get sort options from user
sortby=input('Sort by (likes,dislikes,views,words,id,comments,chapters) : ')
if sortby=='likes': sortby=3
elif sortby=='dislikes': sortby=4
elif sortby=='views': sortby=5
elif sortby=='words': sortby=2
elif sortby=='id': sortby=0
elif sortby=='comments': sortby=7
elif sortby=='chapters': sortby=10
else: failWith('Not a valid option')
revorder=input('Order (inc/dec) : ')
if revorder=='inc': revorder=False
elif revorder=='dec': revorder=True
else: failWith('Not a valid option')
limit=int(input('Limit : '))

# Sort
r=sorted(stories,key=lambda story: int(story[sortby]),reverse=revorder)

# Output
file=open('result.txt','w')
i=0
while i<limit:
    str="{:,}".format(int(r[i][sortby]))+' : '+r[i][1]+' ('+r[i][0]+'). '+r[i][6]
    print(str)
    file.write(str+'\n')
    i+=1
file.close()
