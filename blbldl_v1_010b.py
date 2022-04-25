#! -coding:utf8 -*-
import os
import requests
import re
#from tkinter import *
#from tkinter import messagebox
from bs4 import BeautifulSoup
import json
import sys
from time import sleep
import threading
import danmaku2ass

info_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Host': 'www.bilibili.com',
    'Cookie':"sid=8p7wlbkl; DedeUserID=457022714; DedeUserID__ckMd5=7b6955be650f3ddc; SESSDATA=73245a84%2C1613552124%2C3ed81*81; bili_jct=dd492a72eaafe7ba42645c29a2ba2b6e; LIVE_BUVID=AUTO2815980001248799; rpdid=|(u)~kmkJl|)0J'ulm)|u)JYR; blackside_state=1; CURRENT_FNVAL=80; buvid3=7BB721A9-46EE-EB11-6D31-43F8AFF4FA7761097infoc; _uuid=55CD4D9D-7007-3375-3252-A95DBA1ABFFB81418infoc; CURRENT_QUALITY=120; bp_t_offset_457022714=482356940812554924",
}
url=""
re_all = r"([0-9]|[a-z])*"
mode =""
try:
    info_headers['Cookie'] = open('cookie','r').readline()
except Exception as e:
    print('Cookie loads error')
###由于修改了下载逻辑，所以这里要重新cd到./result
def dirchange(name):
    if not os.path.exists(name):
        os.mkdir(name)
    os.chdir(name)

currentdir=os.getcwd()
choice=''
dirooo="./result"
bin_aria2_path=r'aria2c'
order_aria2='aria2c -s18 -x10  %url%  --referer "https://www.bilibili.com" --file-allocation none'
bin_ffmpeg_path=r'ffmpeg'
order_ffmpeg='ffmpeg -i %video% -i %audio% -y -c:v copy -c:a copy %filename%'

try:
    optiondict=json.load(open("option.json","r"))
    dirooo=optiondict.get("dirooo","./result")
    bin_aria2_path=optiondict.get("bin_aria2_path",r'aria2c')
    order_aria2=optiondict.get("order_aria2",'aria2c -s18 -x10  %url%  --referer "https://www.bilibili.com" --file-allocation none')
    bin_ffmpeg_path=optiondict.get("bin_ffmpeg_path",r'ffmpeg')
    order_ffmpeg=optiondict.get("order_ffmpeg",'ffmpeg -i %video% -i %audio% -y -c:v copy -c:a copy %filename%')
    mode=optiondict.get("mode","")
except Exception as e:
    print('option loads error,using default')

dirchange(dirooo)

class Job(threading.Thread):

    def __init__(self, name,*args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.name = name

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            exec(self.name)
            self.stop()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False


def ending(status=0):
    ###结束，退出
    if status==0:
        print("-----------------------------------\nDownload Success! Exit after 3 s!")
        sleep(3)
        os._exit(0)
        sys.exit()
    else:
        print("-----------------------------------\nDownload Failed! Please check!")
        os._exit(0)
        sys.exit()


def del_func(filename):
    if os.name=='nt':
        os.system("del /Q " + filename)
    elif os.name=='posix':
        os.system("rm -f " + filename)
###原aria2dl
def get_file_from_cmd(link):
    ###把路径cd到./result文件夹
    global bin_aria2_path,order_aria2
    exe_path = bin_aria2_path
    order=re.sub(r'aria2c',exe_path,order_aria2)
    order=re.sub(r'%url%',link,order)
    os.system(order)



### NEW download function
###STEP 1: api to get cid
def api_to_get_cid(id):
    api="https://api.bilibili.com/x/web-interface/view?"
    cidurl=""
    if re.search("bv" + re_all, id, re.I) :
        cidurl = api + "bvid=" + id
    elif re.search("av" + re_all, id, re.I) :
        cidurl = api + "aid=" + re.search("[^a|v][0-9]*" , id, re.I).group(0)
    else :
        print("GETCID_Exception :not a av or bv id")
        return 0
    info_header2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'sec-fetch-dest': 'document',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate', 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': info_headers['Cookie']}
    r = requests.get(cidurl, headers=info_header2)
    del cidurl
    jsondocs = json.loads(r.text)  # 从page中截取出json部分
    del r
    amounts=jsondocs['data']['videos']
    dict_Ep=[{} for _ in range(amounts)]
    for p,i in enumerate(jsondocs['data']['pages']):
        dict_Ep[p]['cid']=i.get('cid',0)
        dict_Ep[p]['ep']=i.get('page',0)
    return dict_Ep

###新api下载法,获取非正常类型的bvid
def url_to_bvid(aurl):
    ra = requests.get(aurl, headers=info_headers)
    sleep(1)
    aurl = ra.url  # 为避免重定向导致的header错误，再进行一次获取
    ra = requests.get(aurl, headers=info_headers)
    soup = BeautifulSoup(ra.content.decode(), 'lxml')  # 拿汤分析html页面，使用lxml较快

    # 找出带有视频信息的json位置：位于script标签下，playinfo中
    raw = soup.find_all("script")  # 找出所有script标签
    pt1 = -1  # 记录info在第几个script标签内
    for p, i in enumerate(raw):
        if str(i).find("window.__INITIAL_STATE__") != -1:
            pt1 = p
            break

    if pt1 == -1:
        print("error: not a valid link")
        sys.exit(1)  # 报错后直接卡掉程序

    page = str(raw[pt1])  # 将element转换为str

    ###浪费效率，节省内存，从我做起！[/滑稽]
    del raw
    del pt1
    del soup
    del aurl
    del ra
    ### 截止到目前 全局变量还有 filename page

    ###开始load json
    ###截止到程序build 2021.01.28 正33后131 为该script中的json部分
    jsondocs = json.loads(page[33:-131])
    #cid = jsondocs['videoData']['cid']
    bvid = jsondocs['videoData']['bvid']
    return bvid

###新blbldl,对api下载
def blbldl(durl,filename="",cid=0):
    ###开始使用request获取html
    info_header2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'sec-fetch-dest': 'document',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate',
        'upgrade-insecure-requests': "1",
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'Cookie': info_headers['Cookie'],
    }
    r = requests.get(durl, headers=info_header2)
    ### 截止到目前 全局变量还有 filename r### update in 08/10/21 request does not support 'br' zip mode
    ###开始load json
    if re.search(r"api.bilibili.com",durl,re.I):
        jsondocs = json.loads(r.text)  # 从api的response中截取出json部分
    else:
        soup = BeautifulSoup(r.content.decode(), 'lxml')  # 拿汤分析html页面，使用lxml较快

        # 找出带有视频信息的json位置：位于script标签下，playinfo中
        raw = soup.find_all("script")  # 找出所有script标签
        pt1 = -1  # 记录info在第几个script标签内
        for p, i in enumerate(raw):
            if str(i).find("window.__playinfo__") != -1:
                pt1 = p
                break

        if pt1 == -1:
            print("error: not a valid link")
            ending(-1)  # 报错后直接卡掉程序

        page = str(raw[pt1])  # 将element转换为str
        jsondocs = json.loads(page[28:-9])  # 从page中截取出json部分
    ###浪费效率，节省内存，从我做起！[/滑稽]
    del durl
    del r
    if jsondocs.get('data','None') == 'None':
        print("Invalid b-video link,None given from api")
        ending(-1)
    ulp = jsondocs['data']['dash']  # playinfo位于该json中/data/dash下
    infov = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]  # 创建列表接受视频信息
    info_p = 0  # 位置‘指针’

    for i in ulp['video']:
        infov[info_p]['bandwidth'] = i.get('bandwidth', 0)  # 可通过带宽信息比较文件清晰度
        infov[info_p]['width'] = i.get('width', 0)
        infov[info_p]['height'] = i.get('height', 0)
        #infov[info_p]['codecid'] = i.get('codecid', 0)  # codecid 7=h264 12=h265
        infov[info_p]['base_url'] = i.get('base_url', i.get('backup_url', ''))
        info_p += 1

    infoa = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
    info_p = 0
    if ulp.get('audio', "")!= "" and ulp.get('audio', "")[0].get('bandwidth', '')!= '':
        for i in ulp['audio']:
            infoa[info_p]['bandwidth'] = i.get('bandwidth', 0)
            infoa[info_p]['id'] = i.get('id', 0)
            infoa[info_p]['base_url'] = i.get('base_url', '')
            info_p += 1
    # 下面获取最高清晰度文件信息，其实根据分析，第一个必然是最清楚的h264视频
    bestvideo_p = 0
    bestaudio_p = 0

    for i, p in enumerate(infov):
        if p:
            if infov[bestvideo_p]['bandwidth'] < p['bandwidth']:
                bestvideo_p = i
    if info_p>=1:
        for i, p in enumerate(infoa):
            if p:
                if infoa[bestaudio_p]['bandwidth'] < p['bandwidth']:
                    bestaudio_p = i

    print("Get video link:SUCCESS!")

    ###下面开始下载与整合
    videoname = re.findall(r".*?.m4s", infov[bestvideo_p]["base_url"].split("/")[7])[
        0]  # 啊这是发现b站视频链接第7个/后是视频名，正则不会提所以暂时用土方了
    audioname=""
    if info_p>=1:
        audioname = re.findall(r".*?.m4s", infoa[bestaudio_p]["base_url"].split("/")[7])[0]
    ###下载
    global mode
    if re.search("ass", mode, re.I) and cid !=0:
        vUrl = 'http://comment.bilibili.com/' + str(cid) + '.xml'
        r = requests.get(vUrl,headers=info_header2)
        DanMu=open(str(cid) + '.xml','w',encoding='utf-8')
        DanMu.write(r.content.decode('utf8'))
        DanMu.close()
        danmaku2ass.Danmaku2ASS(str(cid) + '.xml', 'Bilibili',filename+'.ass',infov[bestvideo_p].get('width',1920),infov[bestvideo_p].get('height',1080),font_size=48.0,text_opacity=0.8,duration_marquee=10.0)
        print("ass Downloaded!")
        del_func(str(cid) + '.xml')
    else:
        print("Ignored ass Download.")
    if mode != "ass":
        if filename == "":
            filename = videoname + ".mp4"
        else:
            filename = filename + ".mp4"
        get_file_from_cmd(r'"' + infov[bestvideo_p]['base_url'] + r'"')  # download video
        global bin_ffmpeg_path, order_ffmpeg
        if info_p >= 1:
            get_file_from_cmd(r'"' + infoa[bestaudio_p]['base_url'] + r'"')  # download audio

            ###整合 使用ffmpeg
            order=re.sub("ffmpeg",bin_ffmpeg_path,order_ffmpeg)
            order = re.sub(r"%video%",videoname,order)
            order = re.sub(r"%audio%",audioname,order)
            order = re.sub(r"%filename%",filename,order)
            os.system(order)  # combine video and audio
            ###删除原分段下载文件
            del_func(videoname)
            del_func(audioname)
        else:
            ###整合 使用ffmpeg
            order = re.sub("ffmpeg", bin_ffmpeg_path, order_ffmpeg)
            order = re.sub(r" -i %audio% "," ",order)
            order = re.sub(r"%video%", videoname, order)
            order = re.sub(r"%filename%", filename, order)
            os.system(order)  # combine video and audio
            ###删除原分段下载文件
            del_func(videoname)
        print("video Downloaded!")


    ###结束
    print(filename + ",Downloaded!\nThis part will end after 3s!")
    sleep(3)


###对ss的剧集分解部分
def ssdecoding() :
    r = requests.get(url,headers=info_headers)
    soup = BeautifulSoup(r.content.decode(), 'lxml')
    raw = soup.find_all("script")
    pt1 = 0
    for i in raw:
        if str(i).find("<script>window.__INITIAL_STATE__=") != -1:
            break
        pt1+=1
    page = str(raw[pt1])
    del raw
    ###这里大部分操作copy于dl部分，不再做过多解释
    ###截止到 2021.01.28 ep_info是script的正33到反131
    p1 = json.loads(page[33:-131])
    ulp = p1['epList']
    title=p1['h1Title']
    #最大支持52ep下载
    infoep =[{} for _ in range(len(ulp))]
    info_p=0
    for i in ulp:
        infoep[info_p]['title']=i.get('title',0)
        infoep[info_p]['bvid']=i.get('bvid','')
        infoep[info_p]['cid']=i.get('cid','')
        infoep[info_p]['titleFormat']=i.get('titleFormat','')
        info_p+=1

    print("Result: The ",title," has ",info_p," episodes")
    global choice
    T1=Job('global choice\n'+'choice=input('+"'"+r'\nenter the episodes you wanna download(using","or"-"),if no input during 6s,all episodes will be download.\n'+"')")
    T1.start()
    for i in range(1,8):
        sleep(1)
        if not T1.is_alive():
            break
    del T1
    epc=choice.split(',')
    eplist=[]
    try:
        for i in epc:
            epc2=i.split('-')
            if len(epc2)==1:
                if epc2[0]== "":
                    continue
                if epc2[0]=='0':
                    epc2[0]=str(info_p)
                eplist.append(int(epc2[0]))
            elif len(epc2)==2:
                if epc2[1]=='0':
                    epc2[1]=str(info_p)
                if int(epc2[0])>int(epc2[1]):
                    continue
                for x in range(int(epc2[0]), int(epc2[1]) + 1):
                    eplist.append(x)
            else:
                del eplist
                eplist=[]
                print("None valid input,using default!")
    except Exception:
        eplist=[]
        print("None valid input,using default!")
    if eplist:
        ch = ""
        for i in eplist:
            ch=ch+str(i)+","
        print("you chose:"+ch+"to download")
        del ch
    print("Download will start after 3 seconds")
    sleep(3)
    print("Download started")
    dirchange(re.sub(r'[:\s?/*"`><|\\]', '_', title))
    for p,i in enumerate(infoep):
        if eplist:
            if p+1 not in eplist:
                continue
        if i.get('title', 0)!=0:
            vUrl=""
            filename=""
            if i.get('bvid', "")== "":
                print("This episode has no BV number!")
                print("------------------------------\nDownload Failed!")
                continue
            vUrl='https://api.bilibili.com/x/player/playurl?cid=' + str(i.get('cid','')) + '&bvid=' + i.get('bvid','') + '&qn=120&fnval=80'
            if i.get('titleFormat', '')== "":
                filename=re.sub(r'[:\s?/*"`><|\\]', '_', title)+"_第"+str(i.get('title',0))+"话"
            else:
                filename=re.sub(r'[:\s?/*"`><|\\]', '_', title)+"_"+re.sub(r'[:\s?/*"`><|\\]', '_', i.get('titleFormat',''))
            blbldl(vUrl,filename,i.get('cid', 0))
    dirchange("../")
###考虑到BV号视频下的分p，现用api法对bv视频获取cid实现多p下载



def main(redirect=False):
    try:
        global url,mode
        try:
            if len(sys.argv)==3:
                mode = sys.argv[2]
            if not redirect:
                url = sys.argv[1]
        except Exception:
            print("NO args! Program will exit.")
        eplistc = []
        category_bv = re.search("bv" + re_all, url, re.I)
        if category_bv:
            eplist=api_to_get_cid(category_bv.group(0))
            if len(eplist)!=1:
                dirchange(category_bv.group(0))
                print("this number has "+str(len(eplist))+" episodes.")
                T1 = Job('global choice\n' + 'choice=input(' + "'" + r'\nenter the episodes you wanna download(using","or"-"),if no input during 6s,all episodes will be download.\n' + "')")
                T1.start()
                for i in range(1, 8):
                    sleep(1)
                    if not T1.isAlive():
                        break
                del T1
                epc = choice.split(',')
                eplistc = []
                try:
                    for i in epc:
                        epc2 = i.split('-')
                        if len(epc2) == 1:
                            if epc2[0] == "":
                                continue
                            if epc2[0] == '0':
                                epc2[0] = str(len(eplist))
                            eplistc.append(int(epc2[0]))
                        elif len(epc2) == 2:
                            if epc2[1] == '0':
                                epc2[1] = str(len(eplist))
                            if int(epc2[0]) > int(epc2[1]):
                                continue
                            for x in range(int(epc2[0]), int(epc2[1]) + 1):
                                eplistc.append(x)
                        else:
                            del eplistc
                            eplistc = []
                            print("None valid input,using default!")
                except Exception:
                    eplistc = []
                    print("None valid input,using default!")
                if eplistc:
                    ch = ""
                    for i in eplistc:
                        ch = ch + str(i) + ","
                    print("you chose:" + ch + "to download")
                    del ch
            for p,i in enumerate(eplist):
                if eplistc:
                    if p + 1 not in eplistc:
                        continue
                vUrl = 'https://api.bilibili.com/x/player/playurl?cid=' + str(i.get('cid', 0)) + '&bvid=' +category_bv.group(0) + '&qn=120&fnval=80'
                blbldl(vUrl ,category_bv.group(0)+"_"+str(i.get('ep', 0)),i.get('cid', 0))
            ending()
            return
        del category_bv
        category_ss = re.search("ss" + re_all, url, re.I)
        if category_ss:
            if not re.search(r"bilibili.com", url, re.I):
                url = "https://www.bilibili.com/bangumi/play/" + category_ss.group(0)
            ssdecoding()
            ending()
            return
        del category_ss

        category_av = re.search("av" + re_all, url, re.I)
        if category_av:
            eplist = api_to_get_cid(category_av.group(0))
            if len(eplist)!=1:
                dirchange(category_av.group(0))
                print("this number has "+str(len(eplist))+" episodes.")
                T1 = Job(
                    'global choice\n' + 'choice=input(' + "'" + r'\nenter the episodes you wanna download(using","or"-"),if no input during 6s,all episodes will be download.\n' + "')")
                T1.start()
                for i in range(1, 8):
                    sleep(1)
                    if not T1.is_alive():
                        break
                del T1
                epc = choice.split(',')
                eplistc = []
                try:
                    for i in epc:
                        epc2 = i.split('-')
                        if len(epc2) == 1:
                            if epc2[0] == "":
                                continue
                            if epc2[0] == '0':
                                epc2[0] = str(len(eplist))
                            eplistc.append(int(epc2[0]))
                        elif len(epc2) == 2:
                            if epc2[1] == '0':
                                epc2[1] = str(len(eplist))
                            if int(epc2[0]) > int(epc2[1]):
                                continue
                            for x in range(int(epc2[0]), int(epc2[1]) + 1):
                                eplistc.append(x)
                        else:
                            del eplistc
                            eplistc = []
                            print("None valid input,using default!")
                except Exception:
                    eplistc = []
                    print("None valid input,using default!")
                if eplistc:
                    ch = ""
                    for i in eplistc:
                        ch = ch + str(i) + ","
                    print("you chose:" + ch + "to download")
                    del ch
            for p,i in enumerate(eplist):
                if eplistc:
                    if p + 1 not in eplistc:
                        continue
                vUrl = 'https://api.bilibili.com/x/player/playurl?cid=' + str(i.get('cid', 0)) + '&avid=' + re.search("[^a|v][0-9]*" ,category_av.group(0) , re.I).group(0) + '&qn=120&fnval=80'
                print(vUrl)
                blbldl(vUrl, category_av.group(0) + "_" + str(i.get('ep', 0)),i.get('cid', 0))
            ending()
            return
        del category_av
        category_ep = re.search("ep" + re_all, url, re.I)
        if category_ep:
            if not re.search(r"bilibili.com", url, re.I):
                blbldl("https://www.bilibili.com/bangumi/play/" + category_ep.group(0) ,category_ep.group(0))
            else:
                blbldl(url ,category_ep.group(0),cid=0)
            ending()
            return
        if re.search(r'b23.tv',url):
            if not re.search(r"http", url):
                url = r"http://" + url
            info_header_4short = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'Host': 'b23.tv',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6',}
            r = requests.get(url, headers=info_header_4short,allow_redirects=False)
            if r.status_code==302:
                url = r.headers['Location']
                main(redirect=True)
                return
            else:
                print("wrong short link")
                ending(-1)
                return
    except Exception as e:
        print("\n\nnot a valid bl-video link,please check!")
        print(e)
        ending(-1)
        return

if __name__ == '__main__':
    #url="https://www.bilibili.com/bangumi/play/ep103591"
    #url = "BV1us41127C6"
    main()