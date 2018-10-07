# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 23:08:58 2018

@author: lenovo
"""

from jntele_warn_operate import LteWarn
#########################################################
from jntele_warn_style import SheetStyle
#########################################################
from tkinter import *
import tkinter.messagebox
import tkinter.scrolledtext
import tkinter.filedialog
import pandas as pd
from pandas import DataFrame
import os
import threading

#import time


class App:
    
    def  __init__(self):
        self.root = Tk()#主窗口
        self.initUI()#初始化UI
        self.setUICenter()#居中UI
        self._loadFileInfo()#加载文件信息
        # self.operate = LteWarn(self)#数据处理函数
        # self.style = SheetStyle(self)#格式处理函数
    def run(self):#启动界面
        self.root.mainloop()
        
    def initUI(self):#初始化UI
        ''''''
        self.root.title("济南电信基站故障处理")
        # self.root.resizable(width=False, height=False) #宽不可变, 高可变,默认为True
        self.root.iconbitmap('logo.ico')
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)#绑定关闭处理函数
        
        '''模块一，加载告警模块'''
        lfm_up = LabelFrame(self.root, text='告警数据')
        fm_up1 = Frame(lfm_up)
        Label(fm_up1,text='华为告警文件：').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
        Label(fm_up1,text='诺基亚告警文件1：').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
        Label(fm_up1,text='诺基亚告警文件2：').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
        fm_up1.pack(side=LEFT)
        fm_up2 = Frame(lfm_up)
        self.text_hw = Entry(fm_up2,width=30)
        self.text_hw.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
        self.text_nk1 = Entry(fm_up2,width=30)
        self.text_nk1.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
        self.text_nk2 = Entry(fm_up2,width=30)
        self.text_nk2.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
        fm_up2.pack(side=LEFT)
        fm_up3 = Frame(lfm_up)
        self.button_hw = Button(fm_up3,text='加载',width=5)
        self.button_hw.pack()#side=TOP,anchor=W,fill=Y)
        self.button_hw.bind("<ButtonRelease-1>",self.button_hw_event)
        self.button_nk1 = Button(fm_up3,text='加载',width=5)
        self.button_nk1.pack()#side=TOP,anchor=W,fill=Y)
        self.button_nk1.bind("<ButtonRelease-1>",self.button_nk1_event)
        self.button_nk2 = Button(fm_up3,text='加载',width=5)
        self.button_nk2.pack()#side=TOP,anchor=W,fill=Y)
        self.button_nk2.bind("<ButtonRelease-1>",self.button_nk2_event)
        fm_up3.pack(side=LEFT)
        lfm_up.pack(side=TOP,fill=NONE,pady=4,padx = 4)
        '''模块二，加载基础模块'''
        lfm_md = LabelFrame(self.root, text='基础数据')
        fm_md1 = Frame(lfm_md)
        Label(fm_md1,text='诺基亚小区文件： ').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
    #    Label(fm_md1,text='诺基亚BBU文件： ').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
        Label(fm_md1,text='基站负责文件：').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
        fm_md1.pack(side=LEFT)
        fm_md2 = Frame(lfm_md)
        self.text_nkcell = Entry(fm_md2,width=30)
        self.text_nkcell.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
#        self.text_nkbbu = Entry(fm_md2,width=30)
#        self.text_nkbbu.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
        self.text_bbuinfo = Entry(fm_md2,width=30)
        self.text_bbuinfo.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
        fm_md2.pack(side=LEFT)
        fm_md3 = Frame(lfm_md)
        self.button_nkcell = Button(fm_md3,text='加载',width=5)
        self.button_nkcell.pack()#side=TOP,anchor=W,fill=Y)
        self.button_nkcell.bind("<ButtonRelease-1>",self.button_nkcell_event)
#        self.button_nkbbu = Button(fm_md3,text='加载',width=5)
#        self.button_nkbbu.pack()#side=TOP,anchor=W,fill=Y)
#        self.button_nkbbu.bind("<ButtonRelease-1>",self.button_nkbbu_event)
        self.button_bbuinfo = Button(fm_md3,text='加载',width=5)
        self.button_bbuinfo.pack()#side=TOP,anchor=W,fill=Y)
        self.button_bbuinfo.bind("<ButtonRelease-1>",self.button_bbuinfo_event)
        fm_md3.pack(side=LEFT)
        lfm_md.pack(side=TOP,fill=NONE,pady=2,padx = 2)
        #########################################################
        '''模块二点五，加载告警文件'''
        lfm_md2 = LabelFrame(self.root, text='告警文件')
        fm_md21 = Frame(lfm_md2)
        Label(fm_md21,text='告警文件：          ').pack(side=TOP,anchor=W,pady=4)#,fill=Y)
        fm_md21.pack(side=LEFT)
        fm_md22 = Frame(lfm_md2)
        self.text_warn = Entry(fm_md22,width=30)
        self.text_warn.pack(side=TOP,anchor=W,fill=Y,pady=4,padx = 2)
        fm_md22.pack(side=LEFT)
        fm_md23 = Frame(lfm_md2)
        self.button_warn = Button(fm_md23,text='加载',width=5)
        self.button_warn.pack()#side=TOP,anchor=W,fill=Y)
        self.button_warn.bind("<ButtonRelease-1>",self.button_warn_event)
        fm_md23.pack(side=LEFT)
        lfm_md2.pack(side=TOP,fill=NONE,pady=2,padx = 2)
        #########################################################
        
        '''模块三，加载处理按钮'''
        fm_exe = Frame(self.root)
        Label(fm_exe,width=20).pack(side=LEFT)
        self.button_exe = Button(fm_exe,text=' 处理 ')
        self.button_exe.pack(side=LEFT)
        #self.button_exe.config(state=DISABLED)
        self.button_exe.bind("<ButtonRelease-1>",self.button_exe_event)

        self.check_match = IntVar()
        checkMatch = Checkbutton(fm_exe, text = "匹配告警", variable = self.check_match,
                 onvalue = 1, offvalue = 0)
        checkMatch.select()
        checkMatch.pack(side=RIGHT)#,anchor=E)
        
        self.check_save = IntVar()
        checkSave = Checkbutton(fm_exe, text = "保存告警", variable = self.check_save,
                 onvalue = 1, offvalue = 0)
        checkSave.select()
        checkSave.pack(side=RIGHT)#,anchor=E)

        fm_exe.pack()
        
#        self.button_match = Button(self.root,text='匹配故障表')
#        self.button_match.pack()
#        self.button_analysis = Button(self.root,text='故障分析')
#        self.button_analysis.pack()
        '''模块四，显示处理信息'''
        lfm_dw = LabelFrame(self.root, text='处理信息')
        self.text_info = tkinter.scrolledtext.ScrolledText(lfm_dw,width=49,height=10)#,state = 'HIDDEN')
        self.text_info.config(state=DISABLED)
        self.text_info.pack()
        lfm_dw.pack(side=TOP,fill=NONE,pady=4,padx = 4)
        
        
        
    def setUICenter(self):#将UI居中

        #time.sleep(0.1)
        w = 380#self.root.winfo_width()#
        h = 460#self.root.winfo_height()#
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    # 绑定文件加载按钮
    def button_hw_event(self,event):
        self._getFileName(self.text_hw)
    def button_nk1_event(self,event):
        self._getFileName(self.text_nk1)
    def button_nk2_event(self,event):
        self._getFileName(self.text_nk2)
    def button_nkcell_event(self,event):
        self._getFileName(self.text_nkcell)
#    def button_nkbbu_event(self,event):
#        self._getFileName(self.text_nkbbu)
    def button_bbuinfo_event(self,event):
        self._getFileName(self.text_bbuinfo)
    def button_warn_event(self,event):
        self._getFileName(self.text_warn)
    # 处理按钮程序
    def button_exe_event(self,event):
        '''处理告警信息'''
        if self.button_exe['state'] == DISABLED:
            return
        self.button_exe.config(state=DISABLED)
        thread = threading.Thread(target=self.operateThread)
        thread.setDaemon(True)
        thread.start()
        #self.operateThread()
    
          
    def onClosing(self):# 退出时处理数据  
        self._saveFileInfo()
        self.root.destroy()
        
        
    def _loadFileInfo(self):# 加载文件数据
        filename = 'filedata.csv'
        if not os.path.exists(filename):
            return
        try:
            df = pd.read_csv(filename)#,engine='python')
            df = df.fillna('')
            self.text_hw.insert(0,df.loc[0,'INFO'])
            self.text_nk1.insert(0,df.loc[1,'INFO'])
            self.text_nk2.insert(0,df.loc[2,'INFO'])
            self.text_nkcell.insert(0,df.loc[3,'INFO'])
    #        self.text_nkbbu.insert(0,df.loc[4,'INFO'])
            self.text_bbuinfo.insert(0,df.loc[4,'INFO'])
            self.text_warn.insert(0,df.loc[5,'INFO'])
        except Exception as e:
            self.showError("异常信息",e)
            
    def _saveFileInfo(self):# 保存加载文件
        df = DataFrame(columns = ['INFO'])
        df.loc[0] = self.text_hw.get()
        df.loc[1] = self.text_nk1.get()
        df.loc[2] = self.text_nk2.get()
        df.loc[3] = self.text_nkcell.get()
#        df.loc[4] = self.text_nkbbu.get()
        df.loc[4] = self.text_bbuinfo.get()
        df.loc[5] = self.text_warn.get()
        df.to_csv('filedata.csv',header=True,index=True) 
        
    def _getFileName(self,entry):# 获取文件名称并格式
        '''获取并显示文件名字'''
        filename = tkinter.filedialog.askopenfilename()
        if '.csv' in filename or '.xlsx' in filename or '.xls' in filename:
            entry.delete(0,END)
            entry.insert(0,filename)
        else:
            self.showError("文件选择错误","请选择合适的文件格式！")
            
    def _isFileExist(self,filename,info):# 判定文件是否存在
        '''判断文件是否存在'''
        if os.path.exists(filename):
            return True
        else:
            self.showError("文件不存在",info + "不存在！")
            return False
        
    def _enableButton(self,status=True):  # 使能处理按钮 
        if status:
            self.button_exe.config(state = NORMAL)
            
    def printInfo(self,info,status=0): # 输出告警信息
        if status == 0:
            level = '[INFO]'
        elif status == 1:
            level = '[WARN]'
        elif status == 2:
            level = '[ERRO]'
        elif status == 3:
            level = '[UN]'
        else:
            return
        self.text_info.config(state=NORMAL)
        self.text_info.insert(END, level +info + '\n')
        self.text_info.config(state=DISABLED)
        #print(level +info)
        
        
    def showError(self,title,info):# 显示错误信息
        tkinter.messagebox.showinfo(title,info)
        #print('[%s]%s'%(title,info))

    def operateThread(self):# 处理进程程序
        try:
            # 初步核实文件格式
            file_hw = self.text_hw.get()
            if not self._isFileExist(file_hw,'华为告警文件'):
                return
            file_nk1 = self.text_nk1.get()
            if not self._isFileExist(file_nk1,'诺基亚告警文件1'):
                return
            file_nk2 = self.text_nk2.get()
            if not self._isFileExist(file_nk2,'诺基亚告警文件2'):
                return
            file_nkcell = self.text_nkcell.get()
            if not self._isFileExist(file_nkcell,'诺基亚小区信息文件'):
                return
    #        file_nkbbu = self.text_nkbbu.get()
    #        if not self._isFileExist(file_nkbbu,'诺基亚BBU信息文件'):
    #            return
            file_bbuinfo = self.text_bbuinfo.get()
            if not self._isFileExist(file_bbuinfo,'基站分区负责文件'):
                return
            if self.check_match.get() == 1:
                file_warn_base = self.text_warn.get()
                if not self._isFileExist(file_warn_base,'告警文件'):
                    return
            '''生成告警信息'''
            operate = LteWarn(self)
            style = SheetStyle(self)
            status = operate.getWarnInfo(file_hw,
                                            file_nkcell,file_nk1,file_nk2,
                                            file_bbuinfo)
            if not status:
                return

            '''判断是否保存'''
            if self.check_save.get() == 1:
                fname=tkinter.filedialog.asksaveasfilename(initialfile='故障'+ LteWarn.getTimeStr() + '.xlsx',
                                                            filetypes=[("Excel文件",".xlsx")])
                if len(fname) == 0:
                    self.printInfo('告警信息未保存')
                    return
                else:
                    if not '.xlsx' in fname:
                        fname = fname + '.xlsx'
                    operate.saveWarnInfo(fname)
                    self.printInfo('告警信息已保存到：' + fname)
                    os.popen(fname)
            '''判断是否匹配告警文件'''
            if self.check_match.get() == 1:
                operate.matchWarnBase(file_warn_base)
                fname=tkinter.filedialog.asksaveasfilename(initialfile='故障汇总'+ LteWarn.getTimeStr() + '.xlsx',
                                                           filetypes=[("Excel文件",".xlsx")])
                if len(fname) == 0:
                   self.printInfo('故障汇总信息未保存')
                   return
                else:
                    if not '.xlsx' in fname:
                        fname = fname + '.xlsx'
                    operate.saveWarnBase(fname)
                    style.setWarnSheetStyle(fname)
                    # self.printInfo('故障汇总信息已保存到：' + fname)
                    os.popen(fname)
        except Exception as e:
            self.showError("异常信息",e)      
        finally:
            self._enableButton()
if __name__ == '__main__':        
    App().run()
    