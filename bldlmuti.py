import multiprocessing
import os
import time
import subprocess
class Job2(multiprocessing.Process):

    def __init__(self, target=None, arg="", *args, **kwargs):
        super(Job2, self).__init__(*args, **kwargs)
        self.__flag = multiprocessing.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = multiprocessing.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self._target = target
        if kwargs is None:
            kwargs = {}
        self._args = args
        self.e=arg
        self._kwargs = kwargs

    def run(self):
        while self.__running.is_set():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            try:
                if self._target:
                    self._target(self.e)
            except Exception as e:
                print("failed to create new thread", self.e, self._target, e)
            finally:
                # Avoid a refcycle if the thread is running a function with
                # an argument that has a member that points to the thread.
                del self._target, self._args, self._kwargs
            self.stop()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False
    def get_running(self):
        return self.__running.is_set()
# def rruunn(a):
#     subprocess.Popen('color b0\nblbldl "'+a+'" ass+\ncolor 0b',creationflags=subprocess.CREATE_NEW_CONSOLE)

def add_new_mission(link):
    print(link)
    with open("a.txt","r+") as e:
        print(time.asctime(time.localtime(time.time()))+":new thread START,link:"+link)
    with open("a.bat","w") as e:
        e.write('blbldl "'+link+'" ass+\n')
    p=subprocess.Popen(["a.bat"],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    while p.poll() is None:
        try:
            print(p.stdout.readline().decode("gbk"))
            if p.stdout.readline().decode().find("ERR")!=-1:
                with open("a.txt", "r+") as e:
                    print(time.asctime(time.localtime(time.time())) + ":link:" + link+" has ERR!")
        except Exception:
            continue
    with open("a.txt", "r+") as e:
        print(time.asctime(time.localtime(time.time())) + ":new thread END,link:" + link)

def listen_mod(linklist):
    bufferlist=[]
    while len(linklist)>0 or len(bufferlist)>0:
        if len(bufferlist)<4 and len(linklist)>0:
            n=Job2(add_new_mission, linklist[0])
            n.start()
            bufferlist.append(n)
            del n
            print(bufferlist)
            linklist.pop(0)
            time.sleep(4)
        print(linklist)
        for i in bufferlist:
            if not i.get_running():
                bufferlist.remove(i)
                break
if __name__ =="__main__":
    p=input("add to queue:")
    linklist = []
    while p!="start":
        linklist.append(p)
        print("success!")
        p=input("add to queue:")
    mt=Job2(listen_mod,linklist)
    mt.start()
    while mt.get_running():
        time.sleep(30)
        print(time.asctime(time.localtime(time.time()))+":Queue is still running...")
