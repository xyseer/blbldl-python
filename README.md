# blbldl-python

made by xyseer

本程序使用pyqt5编写，并使用了danmu2ass进行弹幕下载
感谢danmu2ass作者以及aria2c，ffmpeg两款工具的开发作者！

这是一个使用python编写的b站视频下载工具，使用aria2c进行多线程快速下载，由于b站音视频是分开提供的，下载的音频与视频链接还要使用ffmpeg进行合并。

没有使用已有的you-get工具是因为想使用多线程下载加快速度，此版本还可以通过添加cookie来实现一些其他功能。

本工具开发核心目的之一是希望可以轻松跨平台，目前经测试除Windows外，macOS，常用linux发行版系统，群辉DSM下都可以正常下载大部分视频。

由于开发时刚接触Qt及多线程相关技术，故本程序很多地方都完全不符合正确的开发规则，不建议根据本代码进行相关知识学习。这只是作者在入门阶段自己练手的产出。

本项目所用api，图片均为互联网上开放资源。

本工具可以正常工作，由于代码可维护性极差，因此基本不会再进行任何更新。

==========================================================

# blbldl-python

made by xyseer

It was developed by using pyqt5 as its framework and *danmu2ass* tool to download danmu.
Thanks to the authors of danmu2ass, aria2c and ffmpeg!

This is a tool made with python in order to download videos from bilibili. It uses *aria2c* to download with multiple threads. Due to bilibili provide contents by seperating the video and audio streams, It also has to use *ffmpeg* to combine them.

I didn't choose you-get to download videos because I want more fast speed by using multiple threads. What's more it can also accept cookie for more services.

The aim I develop this was to make it work across platforms. So I tested it in Windows, MacOS, some popular Linux distributions and DSM of Synology. It can work in most cases as long as you have *Python, aria2c and ffmpeg* on these platforms.

When I developed this tool I was a rookie. There are too many problems in Qt and multiple threads tasks. So DON'T reference any codes if you wanna learn something from it. This is just a suck tool came from a rookie man.

The images and apis of this project are all open in the Internet.

It works well in most cases. Due to its extremely poor maintainability, this project may no longer update any more.