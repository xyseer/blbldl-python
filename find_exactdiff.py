import sys
import re

a=sys.argv[1]
b=sys.argv[2]
aa=open(a,"r",encoding="utf-8")
bb=open(b,"r",encoding="utf-8")
bst=bb.readline()
ast=aa.readline()
i=0
while ast:
    i+=1
    if not re.search(ast,bst):
        print(i)

        w=open("result.txt","w+")
        w.write(bst)
        w.close()
    bst=bb.readline()
    ast=aa.readline()
aa.close()
bb.close()
