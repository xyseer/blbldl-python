import json
import os
import re
import sys
from pathlib import Path

def dirchange(name):
    if not os.path.exists(name):
        os.mkdir(name)
    os.chdir(name)

if __name__=="__main__":

    result_list = []
    with open("bldl_name_id_to_filter.json", "r", encoding='utf-8') as w:
        result_list = json.load(w)
    if len(sys.argv) > 1:
        dirchange(sys.argv[1])
    curdir=os.getcwd()
    for i in result_list:
        if (Path(curdir)/(i[0]+".mp4")).exists():
            print(i[0]+" found")
            (Path(curdir) / (i[0] + ".mp4")).rename((Path(curdir)/(i[1]+".mp4")))
        else:
            print(f"    {i[1]}    notfound")
        if (Path(curdir) / (i[0] + ".ass")).exists():
            (Path(curdir) / (i[0] + ".ass")).rename((Path(curdir) / (i[1] + ".ass")))
