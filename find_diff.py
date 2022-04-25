import sys
import re

a=sys.argv[1]
b=sys.argv[2]
aa=open(a,"r",encoding="utf-8")
bb=open(b,"r",encoding="utf-8")
bst=bb.read()
ast=aa.readline()
bst=re.sub(r"\\"," ",bst)
while ast:
    ast=re.sub(r"\\"," ",ast)
    #bst=re.sub(ast,r"\n",bst)
    bst=bst.replace(ast,"\n")
    ast=aa.readline()
w=open("result.txt","w")
w.write(bst)
w.close()
aa.close()
bb.close()
