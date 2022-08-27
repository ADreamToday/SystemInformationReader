# -*- coding: gbk -*-
#coding=gbk

#系统信息查看器
import tkinter
import os
import pyperclip
import tkinter.messagebox 
import systemInfo
import socket
import requests
import json
from fake_useragent import UserAgent
import pynvml

'''
一个刷新按钮
多个复制按钮
多个文本框

一个复制按钮和一个标签组成一个对象
'''


root = tkinter.Tk()


class Base:
    def __init__(self):
        self.info = ""
        pass

    def Copy(self , event):
        try :
            pyperclip.copy(self.Info)
        except AttributeError:
            tkinter.messagebox.showinfo('提示', '未生成信息，无法复制')
        else :
            tkinter.messagebox.showinfo('提示', '已复制到剪切板！')


class cmdBlock(Base):
    def __init__(self , name , cmd):
        self.group = tkinter.LabelFrame(root , text = name ) #盒子
        self.group.pack()

        self.myCmd = cmd    #查询指令
        self.text = tkinter.StringVar() #用于显示的字符串
        self.Info = self.GetInfo()
        self.text.set(self.Info)

        self.aLabel = tkinter.Label(self.group , textvariable = self.text)    #标签内容
        self.aLabel.pack()
        self.aLabel.bind("<Double-Button-1>" , self.Copy)
        

    def GetInfo(self):
        souce = os.popen(self.myCmd)    #获得原始数据
        text = souce.read()
        if self.myCmd == "ver":         #ver
            aList = text.splitlines()
            return aList[1]

        elif self.myCmd == "ipconfig":
            pass



class ABlock(Base):
    def __init__(self , name):
        self.name = name
        #设置盒子
        self.group = tkinter.LabelFrame(root , text = name) #盒子
        self.group.pack()
        #设置标签
        self.text = tkinter.StringVar() #用于显示的字符串
        
        self.text.set("Ready")     #先不显示数据，因为获取数据需要时间
        self.aLabel = tkinter.Label(self.group , textvariable= self.text , height = 2 , width = 55)
        self.aLabel.pack()
        self.aLabel.bind("<Double-Button-1>" , self.Copy)
        self.aLabel.bind("<Button-3>" , self.MoreInfo)

    def GetInfo(self):
        if self.name == "CPU":
            info = systemInfo.GetCpuConstants()
            return info.get("cpu_name" , "error")
            pass 
        elif self.name == "Mem":
            info = systemInfo.GetMemInfo()
            return info.get("memTotal" , "error")
        elif self.name == "Disk":
            info = systemInfo.GetDiskInfo()
            return len(info)    #统计磁盘数，详细信息双击查看
        elif self.name == "operating system" :
            info = systemInfo.GetSystemVersion()
            return info
        elif self.name == "ip(inner)":
            hostname = socket.gethostname()
            info = socket.gethostbyname(hostname)
            return info
        elif self.name == "ip(outer)" :
            exit_code = os.system('ping www.baidu.com > NUL')
            if exit_code:
                info = "No Internet connection!"
            elif exit_code == 0 :
                ua = UserAgent().random
                aHeader = {'User-Agent': ua}
                res = requests.get("https://ip.cn/api/index?ip=&type=0" , headers = aHeader)    #通过网络获取ip
                dic = json.loads(res.text)  #字典化
                info = dic.get("ip")
            return info
        elif self.name == "GPU" :
            pynvml.nvmlInit() # 初始化
            num = pynvml.nvmlDeviceGetCount()
            if num == 1:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                info = pynvml.nvmlDeviceGetName(handle)
            else :
                info = "%d" % num   #不止一块显卡显示数字
            
            pynvml.nvmlShutdown()
            return info
        else :
            return "error"

    def displayInfo(self):
        self.Info = self.GetInfo()  #显示信息后再给info变量
        self.text.set(self.Info)

    def MoreInfo(self , event):
        self.sonWindows = tkinter.Toplevel()
        self.sonWindows.resizable(0,0)
        self.sonWindows.title("详细信息")

        if self.name == "CPU":
            info = systemInfo.GetCpuConstants()
            #核心数
            self.group_core = tkinter.LabelFrame(self.sonWindows , text = "core") 
            self.group_core.pack()
            self.core = tkinter.Label(self.group_core , text = info.get("cpu_core" , "error") , height = 2 , width = 40)
            self.core.pack()

            # 线程数
            self.group_threads = tkinter.LabelFrame(self.sonWindows , text = "threads")
            self.group_threads.pack()
            self.threads = tkinter.Label(self.group_threads , text = info.get("cpu_threads" , "error") , height = 2 , width = 40)
            self.threads.pack()

        elif self.name == "Mem":
            #内存大小（GB）
            info = systemInfo.GetMemInfo()
            memCount = info.get("memTotal" , "error")/1024    #转换成GiB
            self.group_GB = tkinter.LabelFrame(self.sonWindows , text = "Mem(GB)")
            self.group_GB.pack()
            self.GB = tkinter.Label(self.group_GB , text = "%d" % memCount , height = 2 , width = 40)
            self.GB.pack()

        elif self.name == "Disk":
            info = systemInfo.GetDiskInfo()
            for i in info:
                diskname = i.get("path")
                self.gruop_disk = tkinter.LabelFrame(self.sonWindows , text = diskname + "(GB)")
                self.gruop_disk.pack()
                self.disk_size = tkinter.Label(self.gruop_disk , text = ("%d" % (i.get("size").get("total")/1024/1024/1024)) , height = 2 , width = 40)
                self.disk_size.pack()

        elif self.name == "GPU" :
            pynvml.nvmlInit() # 初始化
            num = pynvml.nvmlDeviceGetCount()
            for i in range(num):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                self.group_gpu = tkinter.LabelFrame(self.sonWindows , text = pynvml.nvmlDeviceGetName(handle) + " Mem(GB)")
                self.group_gpu.pack()
                meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                self.gpu_mem = tkinter.Label(self.group_gpu , text = meminfo.total /1024/1024/1024 , height = 2 , width = 40)
                self.gpu_mem.pack()
            pynvml.nvmlShutdown()

        else :
            tkinter.messagebox.showinfo('提示', '该项无详细信息')
            self.sonWindows.destroy()

        self.sonWindows.mainloop()
        

root.resizable(0,0)
root.title("系统信息查看器")


def LoadInfo():
    blockCpu.displayInfo()
    blockDisk.displayInfo()
    blockMem.displayInfo()
    blockOS.displayInfo()
    blockIp.displayInfo()
    blockIp2.displayInfo()
    blockGPU.displayInfo()

    Load["state"] = tkinter.NORMAL

Load = tkinter.Button(root , text = "load" , command = LoadInfo)
Load.pack()

readMe = tkinter.Label(root , text = "ADreamToday开发\n点击load加载所有信息\n双击文字复制信息\n右击查看详细信息\n详细信息不可复制\nN卡版（不支持A卡信息）" , justify = tkinter.LEFT , width = 58 , anchor = tkinter.W)

blockOS     = ABlock("operating system")
blockCpu    = ABlock("CPU")
blockGPU    = ABlock("GPU")
blockMem    = ABlock("Mem")
blockDisk   = ABlock("Disk")
blockIp     = ABlock("ip(inner)")
blockIp2    = ABlock("ip(outer)")
readMe.pack()

blockCpu.displayInfo()
blockDisk.displayInfo()
blockMem.displayInfo()
blockOS.displayInfo()
blockIp.displayInfo()
blockGPU.displayInfo()

root.mainloop()