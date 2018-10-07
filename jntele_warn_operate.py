# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 21:24:13 2018

@author: lenovo
"""

import pandas as pd
import numpy as np
from pandas import DataFrame
from datetime import datetime

nk_pass_enbid = [
        896767,
        896766,
        896765,
        896764,
        896763,
        896762,
        896754,
        896753,
        896752,
        896751,
        896750,
        896749,
        896748,
        896742,
        896741,
        896740,
        896739,
        896738,
        896731,
        896730,
        896729,]

hw_pass_enbid = []

class LteWarn(object):
    
    def __init__(self,app):
        self.app = app
        
    @staticmethod
    def getTimeStr():
        '''公共函数，获取当前时间字符串'''
        return datetime.now().strftime("%Y%m%d%H%M%S")
    @staticmethod
    def getDateStr():
        return datetime.now().strftime("%Y/%m/%d")

    def getWarnInfo(self,file_hw,
                    file_nkcell,file_nk1,file_nk2,
                    file_fz):
        # 开始处理数据
        status,info = self.getHuaweiWarn(file_hw)
        if not status:
            self.app.showError("处理失败",'华为' + info+'，终止执行')
            return False
        dats_hw = info

        status,info = self.getNokiaWarn(file_nkcell,file_nk1,file_nk2)
        if not status:
            self.app.showError("处理失败",'Nokia' + info+'，终止执行')
            return False
        dats_nk = info
               
        dats = dats_hw.append(dats_nk)
        self.app.printInfo('合计%d条告警信息'%(dats.shape[0]))
        dats_fuze = pd.read_excel(file_fz,sheet_name='BBU表')
        dats_fuze = dats_fuze[['eNBID','责任人',]]
        dats_fuze.columns = ['ENB','FUZE']
        fuzes = []
        for enb in dats['ENB']:
            dats_tmp = dats_fuze[dats_fuze['ENB'] == enb]
            if dats_tmp.shape[0] == 0:
                fuzes.append('未定')
            else:
                fuzes.append(dats_tmp.loc[dats_tmp.index[0],'FUZE'])
        dats['FUZE'] = fuzes
        self.app.printInfo('已添加负责人信息')
        dats_tmp = dats[dats['FUZE'] == '未定']
        self.app.printInfo('未定告警负责人%d条'%(dats_tmp.shape[0]),1)
        self.dats_warn = dats[[
                'ENB',
                'CELL_NAME',
                'RRU_NUM',
                'CELL_TYPE',
                'RRU_PRODU',
                'RRU_WARN',
                'FUZE',
                'DATE',]]
        self.dats_warn.columns = [
                '站点ID',
                '故障小区名(网管名称)',
                '故障RRU数目',
                '制式',
                '网管',
                '告警',
                '无线责任人',
                '故障时间',]
        self.dats_warn.index = range(self.dats_warn.shape[0])
        # self.dats_warn.reset_index()
        return True
    
    def saveWarnInfo(self,filename):
        self.dats_warn.to_excel(filename,header=True,index=False)
        return filename
        
    def getHuaweiWarn(self,file_hw):
        self.app.printInfo('开始处理华为告警信息')
        '''读取华为告警数据'''
        if '.csv' in file_hw:
            dats = pd.read_csv(file_hw,sep =',',engine='python')
        else:
            dats = pd.read_excel(file_hw)
        '''筛选告警数据'''
        cell_status_ok = []
        self.app.printInfo('以【操作状态】判定华为小区在服')
        for (bbu_statu,rru_statu) in zip(dats['网元连接状态'],dats['操作状态']):
            if bbu_statu == '在线':
                if rru_statu == '正常':
                    cell_status_ok.append('ok')
                else:
                    cell_status_ok.append('小区退服')
            else:
                cell_status_ok.append('BBU脱管')
        dats['RRU_WARN'] = cell_status_ok
        dats = dats[dats['RRU_WARN']!='ok']
        dats = dats.sort_values(by=['eNodeB标识','本地小区标识'])
        dats = dats[['eNodeB标识','小区标识','小区名称','LTE网元名称', 'RRU_WARN']]
        dats.columns = ['ENB','CELL_ID','CELL_NAME','BBU_NAME','RRU_WARN']
        self.app.printInfo('华为告警信息%d条'%(dats.shape[0]))
        '''删除无用BBU数据'''
        for pass_enbid in self.getHuaweiPassENB():
            dats=dats[dats['ENB']!=pass_enbid]
        (status,info) = self.getHuaweiCell(dats)
        if not status:
            return status,info
        dats = self._getWarning(info)
        dats['RRU_PRODU'] = ['华为'] * dats.shape[0]
        dats['DATE'] = [LteWarn.getDateStr()] * dats.shape[0]
        dats = dats[['ENB','CELL_NAME','CELL_TYPE','RRU_WARN','RRU_PRODU','RRU_NUM','DATE']]
        self.app.printInfo('华为告警信息已经落实') 
        return True,dats

    def getNokiaWarn(self,file_nkcell,file_nk1,file_nk2,file_num=2):
        self.app.printInfo('开始处理Nokia告警信息')
        if '.csv' in file_nk1:
            self._deleNokiaFirstLine(file_nk1)
            dats = pd.read_csv(file_nk1,sep =',',engine='python')
        else:
            self.app.printInfo('Nokia告警文件%s格式不是CSV'%(file_nk1),2)
            return False,'Nokia告警文件格式不是CSV'
        if file_num==2:
            if '.csv' in file_nk2:
                self._deleNokiaFirstLine(file_nk2)
                dats2 = pd.read_csv(file_nk2,sep =',',engine='python')
            else:
                self.app.printInfo('Nokia告警文件%s格式不是CSV'%(file_nk2),2)
                return False,'Nokia告警文件格式不是CSV'
            dats = dats.append(dats2)
        dats = dats[[
                'Alarm number',
                'Object',
                'Started',]]
        dats_bbu = dats[dats['Alarm number']==71058]# 获取BBU脱管
        dats_cell = dats[dats['Alarm number']==7653]# 获取小区脱管
        dats_cellA = dats[dats['Alarm number']==7650]# 获取小区全脱管
        dats=dats_bbu.append(dats_cellA)
        dats=dats.append(dats_cell)
        dats = dats.drop_duplicates(subset='Object', keep='first', inplace=False)
        self.app.printInfo('Nokia告警信息%d条'%(dats.shape[0]))
        
        dats['ENB'] = [int(cell.split('/')[0].split('-')[1]) for cell in dats['Object']]
        dats_bbu = dats[dats['Alarm number']==71058]
        bbu_ids = dats_bbu['ENB']
        bbu_times = dats_bbu['Started']
        dats_cellA = dats[dats['Alarm number']==7650]
        dats_cell = dats[dats['Alarm number']==7653]
        for enb in bbu_ids:
            dats_cellA = dats_cellA[dats_cellA['ENB'] != enb]
            dats_cell = dats_cell[dats_cell['ENB'] != enb]
        for enb in dats_cellA['ENB']:
            dats_cell = dats_cell[dats_cell['ENB'] != enb]
        self.app.printInfo('已去除Nokia重复告警')
        
        if '.csv' in file_nkcell:
            dats_info = pd.read_csv(file_nkcell)#,sep =',',engine='python')
        else:
            dats_info = pd.read_excel(file_nkcell)
        dats_info = dats_info[dats_info['CITY']=='JN']
        tmp = dats_info.columns.tolist()
        tmp[0] = 'BTSID'
        dats_info.columns = tmp
        dats_info['ID'] = dats_info['BTSID']*256+dats_info['CELLID']
        
        dats = DataFrame(columns=dats_info.columns)
        times = []
        for (enb,tm) in zip(dats_cellA['ENB'],dats_cellA['Started']):
            dats_tmp = dats_info[dats_info['BTSID']==enb]
            dats = dats.append(dats_tmp)
            times.extend([tm]*dats_tmp.shape[0])
        dats['DATE'] = times
        
        dats_cell['CELLID'] = [int(cell.split('-')[-1]) for cell in dats_cell['Object']]
        dats_cell['ID'] = dats_cell['ENB'] *256 + dats_cell['CELLID'] 
        times = []
        dats_loss = DataFrame(columns=dats_info.columns)
        for (cellid,tm) in zip(dats_cell['ID'],dats_cell['Started']):
            dats_tmp = dats_info[dats_info['ID']==cellid]
            dats_loss = dats_loss.append(dats_tmp)
            times.extend([tm]*dats_tmp.shape[0])
        dats_loss['DATE'] = times
        
        dats = dats.append(dats_loss)
        dats['RRU_WARN'] = ['小区退服'] * dats.shape[0]
        
        dats_bbuloss = DataFrame(columns=dats_info.columns)
        times = []
        for enb,tm in zip(bbu_ids,bbu_times):
            dats_tmp = dats_info[dats_info['BTSID']==enb]
            dats_bbuloss = dats_bbuloss.append(dats_tmp)
            times.extend([tm]*dats_tmp.shape[0])
        dats_bbuloss['DATE'] = times
        dats_bbuloss['RRU_WARN'] = ['BBU脱管'] * dats_bbuloss.shape[0]
        dats = dats.append(dats_bbuloss)
        dats = dats[['BTSID', 'LCRID', 'CELLNAME','DATE','RRU_WARN']]
        self.app.printInfo('已获取Nokia告警小区名,共%d小区'%(dats.shape[0]))
        dats['CELLNAME'] = dats['CELLNAME'].fillna('999')
        dats = dats[dats['CELLNAME'] != '999']
        self.app.printInfo('已去除名为空小区,剩余%d'%(dats.shape[0]))
        dats.columns = ['ENB', 'CELL_ID', 'CELL_NAME', 'DATE', 'RRU_WARN']
        '''删除无用BBU数据'''
        for pass_enbid in self.getNokiaPassENB():
            dats=dats[dats['ENB']!=pass_enbid]
            # print(dats[dats['ENB']==pass_enbid].shape[0])
        status,info = self.getNokiaCell(dats)
        if not status:
            return status,info
        dats = self._getWarning(info)
        dats['RRU_PRODU'] = ['诺基亚'] * dats.shape[0]
        dats = dats[['ENB','CELL_NAME','CELL_TYPE','RRU_WARN','RRU_PRODU','RRU_NUM','DATE']]
        #dats['DATE'] = [datetime.strptime(date_str, '%d.%m.%Y  %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S') for date_str in dats['DATE']]
        dats['DATE'] = [datetime.strptime(date_str, '%d.%m.%Y  %H:%M:%S').strftime('%Y/%m/%d') for date_str in dats['DATE']]
        self.app.printInfo('诺基亚告警信息已经落实')        
        return True,dats
    
    def _deleNokiaFirstLine(self,file_name):   
        dats = pd.read_csv(file_name,sep =',',engine='python')
        if dats.shape[1]==1:
            isFirst = True
            with open(file_name,"r",encoding="utf-8") as f_r:
                lines = f_r.readlines()
            with open(file_name,"w",encoding="utf-8") as f_w:
                for line in lines:
                    if isFirst:
                        isFirst = False
                        continue
                    else:
                        f_w.write(line)
        
    def _getWarning(self,dats):

        cell_types = []
        for (rru_type,sys) in zip(dats['CELL_TYPE'],dats['OUT']):
            if 'I' in sys:
                cell_types.append('室分')
            elif rru_type == 'L800':
                cell_types.append('800M')
            elif rru_type == 'L1800':
                cell_types.append('1.8G')
            elif rru_type == 'L2100':
                cell_types.append('2.1G')
            else:
                cell_types.append('未知')
        dats['CELL_TYPE'] = cell_types
        dats = dats.drop(['OUT'],axis=1)
        self.app.printInfo('小区分类信息已经落实')  

        rru_nums = []
        for cell in dats['CELL_NAME']:
            ifSure = True
            for i in range(14):
                if '-C%d-'%(i+2) in cell:
                    rru_nums.append(i+2) 
                    ifSure = False
                    continue
            if ifSure:
                rru_nums.append(1)
        dats['RRU_NUM'] = rru_nums
        self.app.printInfo('小区RRU故障数已经落实') 
        return dats
        
    def getHuaweiCell(self,dats):
        '''核实小区类型'''
        self.app.printInfo('根据CI标记确认小区类型')
        cell_types = []
        for ci in dats['CELL_ID']:
            if(ci>=145 and ci<145+15):
                cell_types.append('LT')
            elif(ci>=80 and ci<81+15)or(ci>=208 and ci<209+15):
                cell_types.append('NB')
            elif(ci>=17 and ci<17+15)or(ci>=241 and ci<241+15):
                cell_types.append('L800')
            elif(ci>=49 and ci<49+31)or(ci>=177 and ci<177+15):
                cell_types.append('L1800')
            elif(ci>=1 and ci<1+15)or(ci>=129 and ci<129+15):
                cell_types.append('L2100')
            else:
                cell_types.append('UNKNOW')    
        dats['CELL_TYPE'] = cell_types

        #self.app.printInfo('核实小区命名有效性')
        back_status = True
        '''是否有未知小区'''
        dats_tmp = dats[dats['CELL_TYPE']=='UNKNOW']
        if(dats_tmp.shape[0]>0):
            self.app.printInfo('有%d个小区未明确系统类型'%(dats_tmp.shape[0]),2)
            for inx in dats_tmp.index:
                self.app.printInfo('[%s][%d]'%(dats.loc[inx,'CELL_NAME'],dats.loc[inx,'CELL_ID']),2)
                back_status = False
        if not back_status:
            return False,'小区标识错误，有未知小区类型'
        '''800M小区命名是否正确'''
        dats_tmp = dats[dats['CELL_TYPE']!='L800']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if '-800M' in name:
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('非800M小区中存在800M命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'非800M小区中存在800M命名小区'
        dats_tmp = dats[dats['CELL_TYPE']=='L800'] 
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if not('800M' in name):
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('800M小区中存在非800M命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'800M小区中存在非800M命名小区'

        '''NB小区命名是否正确'''
        dats_tmp = dats[dats['CELL_TYPE']!='NB']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if 'NB' in name:
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('非NB小区中存在NB命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2) 
        dats_tmp = dats[dats['CELL_TYPE']=='NB']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if not('NB' in name):
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('NB小区中存在非NB命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'NB小区中存在非NB命名小区'
        '''联通小区命名是否正确'''
        dats_tmp = dats[dats['CELL_TYPE']!='LT']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if 'LI' in name or 'ZLO' in name or 'LO' in name:
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('非联通小区中存在联通命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'非联通小区中存在联通命名小区'
        dats_tmp = dats[dats['CELL_TYPE']=='LT']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if not('LI' in name or 'ZLO' in name or 'LO' in name):
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('联通小区中存在非联通命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'联通小区中存在非联通命名小区'
        self.app.printInfo('小区命名有效性已核实')
        
        
        dats = dats[dats['CELL_TYPE']!='LT']
        dats = dats[dats['CELL_TYPE']!='NB']
        self.app.printInfo('去除NB和联通共享小区，剩余%d条'%(dats.shape[0]))
        
        '''区分室分室外'''
        out_status = []
        for name in dats['CELL_NAME']:
            tmps = name.split('-')
            #if len(tmps)<8:
            out_status.append(tmps[7])
        dats['OUT'] = out_status
        dats_tmp = dats[(dats['OUT']!='O')&(dats['OUT']!='I')&(dats['OUT']!='OC1')&(dats['OUT']!='IC1')&(dats['OUT']!='G')]
        if dats_tmp.shape[0] != 0:
            back_status = False
            self.app.printInfo('存在不能区分室分室外的小区%d个'%(dats_tmp.shape[0]),2)
            for inx,name in zip(dats_tmp.index,dats_tmp['小区名称']):
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
            if not back_status:
                return False,'存在不能区分室分室外的小区%d个'%(dats_tmp.shape[0])
        self.app.printInfo('已区分室分室外')
        return True,dats

    def getNokiaCell(self,dats):
        '''核实小区类型'''
        self.app.printInfo('根据CI标记确认小区类型')
        cell_types = []
        for ci in dats['CELL_ID']:
            if(ci>=145 and ci<145+15):
                cell_types.append('LT')
            elif(ci>=81 and ci<81+15)or(ci>=209 and ci<209+15):
                cell_types.append('NB')
            elif(ci>=17 and ci<17+15)or(ci>=241 and ci<241+15):
                cell_types.append('L800')
            elif(ci>=49 and ci<49+31)or(ci>=177 and ci<177+15):
                cell_types.append('L1800')
            elif(ci>=1 and ci<1+15)or(ci>=129 and ci<129+15):
                cell_types.append('L2100')
            else:
                cell_types.append('UNKNOW')        
        dats['CELL_TYPE'] = cell_types
        
        back_status = True
        '''是否有未知小区'''
        dats_tmp = dats[dats['CELL_TYPE']=='UNKNOW']
        if(dats_tmp.shape[0]>0):
            self.app.printInfo('有%d个小区未明确系统类型'%(dats_tmp.shape[0]),2)
            for inx in dats_tmp.index:
                self.app.printInfo('[%s][%d]'%(dats.loc[inx,'CELL_NAME'],dats.loc[inx,'CELL_ID']),2)
                back_status = False
        if not back_status:
            return False,'小区标识错误，有未知小区类型'
        '''800M小区命名是否正确'''
        dats_tmp = dats[dats['CELL_TYPE']!='L800']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if '800M' in name:
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('非800M小区中存在800M命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'非800M小区中存在800M命名小区'
        dats_tmp = dats[dats['CELL_TYPE']=='L800'] 
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if not('800M' in name):
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('800M小区中存在非800M命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'800M小区中存在非800M命名小区'

        '''NB小区命名是否正确'''
        dats_tmp = dats[dats['CELL_TYPE']!='NB']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if 'NB' in name:
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('非NB小区中存在NB命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2) 
        dats_tmp = dats[dats['CELL_TYPE']=='NB']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if not('NB' in name):
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('NB小区中存在非NB命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'NB小区中存在非NB命名小区'
        '''联通小区命名是否正确'''
        dats_tmp = dats[dats['CELL_TYPE']!='LT']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if '联通小区' in name or '联通共享' in name or '共享联通' in name:
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('非联通小区中存在联通命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'非联通小区中存在联通命名小区'
        dats_tmp = dats[dats['CELL_TYPE']=='LT']
        status = True
        for inx,name in zip(dats_tmp.index,dats_tmp['CELL_NAME']):
            if not('联通小区' in name or '联通共享' in name or '共享联通' in name or '(联通)' in name):
                if status:
                    back_status = False
                    status = False
                    self.app.printInfo('联通小区中存在非联通命名小区',2)
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
        if not back_status:
            return False,'联通小区中存在非联通命名小区'
        self.app.printInfo('小区命名有效性已核实')
        
        
        dats = dats[dats['CELL_TYPE']!='LT']
        dats = dats[dats['CELL_TYPE']!='NB']
        self.app.printInfo('去除NB和联通共享小区，剩余%d条'%(dats.shape[0]))
        '''区分室分室外'''
        out_status = []
        for name in dats['CELL_NAME']:
            tmps = name.split('-')
            #if len(tmps)<8:
            out_status.append(tmps[7])
        dats['OUT'] = out_status
        dats_tmp = dats[(dats['OUT']!='O')&(dats['OUT']!='I')&(dats['OUT']!='D')&(dats['OUT']!='G')]
        if dats_tmp.shape[0] != 0:
            back_status = False
            self.app.printInfo('存在不能区分室分室外的小区%d个'%(dats_tmp.shape[0]),2)
            for inx,name in zip(dats_tmp.index,dats_tmp['小区名称']):
                self.app.printInfo('[%s][%d]'%(dats_tmp.loc[inx,'CELL_NAME'],dats_tmp.loc[inx,'CELL_ID']),2)
            if not back_status:
                return False,'存在不能区分室分室外的小区%d个'%(dats_tmp.shape[0])
        self.app.printInfo('已区分室分室外')       
        return True,dats

    def getNokiaPassENB(self):
        return nk_pass_enbid

    def getHuaweiPassENB(self):
        return hw_pass_enbid

    def matchWarnBase(self,file_base,file_warn=1):
        '''匹配告警调度表'''
        self.app.printInfo('开始将故障信息更新到调度表中')
        ''' 处理故障调度表信息 '''
        dats_base = pd.read_excel(file_base)
        inx_base = dats_base.shape[0]
        self.app.printInfo('故障调度表中共有%d条信息'%(inx_base-1))
        dats_base['ID'] = range(inx_base)
        '''预处理日期格式'''
        dats_base['故障时间'] = [self._getDateInfo(dat) for dat in dats_base['故障时间']]
        dats_base['恢复时间'] = [self._getDateInfo(dat) for dat in dats_base['恢复时间']]
        dats_base['预计恢复日期'] = [self._getDateInfo(dat) for dat in dats_base['预计恢复日期']]
        '''确认是否恢复'''
        list_dat = []
        dats_base['恢复时间'] = dats_base['恢复时间'].fillna('')
        for dat in dats_base['恢复时间']:
            if isinstance(dat,str):
                if '已恢复' in dat or '/' in dat:
                    list_dat.append('OK')
                else:
                    list_dat.append('NO')
        dats_base ['STATUS'] = list_dat
        '''筛选判断告警信息'''
        dats_base_ok = dats_base[dats_base['制式']!='800M']
        dats_base_ok = dats_base_ok[dats_base_ok['制式']!='1.8G']
        dats_base_ok = dats_base_ok[dats_base_ok['制式']!='2.1G']
        dats_base_ok = dats_base_ok[dats_base_ok['制式']!='室分']     
        self.app.printInfo('故障调度表中非LTE告警(包含已恢复)共有%d条信息'%(dats_base_ok.shape[0]-1))
        dats_lte = dats_base[dats_base['制式']=='800M']
        dats_lte = dats_lte.append(dats_base[dats_base['制式']=='1.8G'])
        dats_lte = dats_lte.append(dats_base[dats_base['制式']=='2.1G'])
        dats_lte = dats_lte.append(dats_base[dats_base['制式']=='室分'])
        self.app.printInfo('故障调度表中LTE告警(包含已恢复)共有%d条信息'%(dats_lte.shape[0]))
        dats_base_ok = dats_base_ok.append(dats_lte[dats_lte['STATUS']=='OK'])
        self.app.printInfo('故障调度表中已恢复LTE告警不处理')
        '''筛选故障调度表中未恢复LTE基站告警信息'''
        dats_lte = dats_lte[dats_lte['STATUS']=='NO']
        self.app.printInfo('故障调度表中未恢复LTE告警%d条'%(dats_lte.shape[0]))
        ''' 加载当日告警信息 '''
        if file_warn != 1:
            dats_warn = pd.read_excel(file_warn)
        else:
            dats_warn = self.dats_warn
        '''核实恢复告警、未恢复告警、新增告警'''
        dats = dats_lte[['故障小区名(网管名称)','ID']]
        dats.columns = ['CELL_NAME','ID']
        dats_plus = DataFrame(columns=dats_warn.columns)
        inx_plus = 0
        dats_base_tmp = DataFrame(columns=dats_base_ok.columns)
        for inx_warn,cell_name in zip(dats_warn.index,dats_warn['故障小区名(网管名称)']):
            dats_tmp = dats[dats['CELL_NAME']==cell_name]
            if dats_tmp.shape[0] == 0:#新增告警
                dats_plus.loc[inx_plus] = dats_warn.loc[inx_warn]
                inx_plus += 1
            else:
                #旧有告警
                dats_base_tmp = dats_base_tmp.append(dats_lte[dats_lte['故障小区名(网管名称)']==cell_name])
                dats_lte = dats_lte[dats_lte['故障小区名(网管名称)']!=cell_name]
        # 核实恢复告警          
        dats_lte['恢复时间'] = [LteWarn.getDateStr()]*dats_lte.shape[0]
        dats_lte['超时天数'] = ['']*dats_lte.shape[0]
        dats_lte['STATUS'] = ['OK']*dats_lte.shape[0]
        self.app.printInfo('核实故障调度表中已恢复LTE告警%d条'%(dats_lte.shape[0]))
        dats_base_ok = dats_base_ok.append(dats_lte)
        # 核实恢复告警
        dats_base_tmp['恢复时间'] = ['']*dats_base_tmp.shape[0]
        dats_base_tmp['超时天数'] = [self._getDeltaDays(date_str) for date_str in dats_base_tmp['故障时间']]
        dats_base_tmp['超时应罚金额'] = dats_base_tmp['超时天数']*30
        dats_base_tmp['超时天数'] .replace(0, '未知')
        dats_base_tmp['超时应罚金额'].replace(0, '未知')
        dats_base_tmp['STATUS'] = ['NO'] * dats_base_tmp.shape[0]
        self.app.printInfo('核实故障调度表中未恢复LTE告警%d条'%(dats_base_tmp.shape[0])) 
        dats_base_ok = dats_base_ok.append(dats_base_tmp)
        columns_end = dats_base_ok.columns
        # 核实恢复告警
        dats_plus['ID'] = range(inx_base,dats_plus.shape[0]+inx_base)
        dats_plus['STATUS'] = ['NO'] * dats_plus.shape[0]
        self.app.printInfo('核实故障调度表中新增LTE告警%d条'%(dats_plus.shape[0]))
        # dats_base_ok = dats_base_ok.append(dats_plus)
        
        dats_base_ok = pd.concat([dats_base_ok,dats_plus],sort=True)
        '''最终处理数据'''
        
        dats_base_ok = dats_base_ok[columns_end]#调整列序
        dats_base_ok = dats_base_ok.sort_values(by=['ID'])#调整行序      
        dats_base_ok = dats_base_ok.fillna('')#填充
        dats_base_ok.replace('nan', '')#填充
        dats_base_ok.replace('#N/A', '')#填充
        #设置每行格式类型
        list_dat = []
        for dat in dats_base_ok['STATUS']:
            if dat == 'OK':
                list_dat.append(4)
            elif dat == 'NO':
                list_dat.append(3)
            else:
                list_dat.append(3)
        list_dat[0] = 2
        dats_base_ok[1] = list_dat
        #删除多余列
        dats_base_ok = dats_base_ok.drop(['ID','STATUS'],axis=1)
        col_list  = dats_base_ok.columns.tolist()
        self.app.printInfo('已将故障信息更新到调度信息中')
        self.dats_base = dats_base_ok
        return self.dats_base

    def saveWarnBase(self,filename):
        self.dats_base.to_excel(filename,header=True,index=False)
        return filename

    def _getDateInfo(self,dat):
        '''格式化输出Date信息'''
        if isinstance(dat,pd._libs.tslibs.timestamps.Timestamp):
            return dat.date().strftime("%Y/%m/%d")
        elif isinstance(dat,pd._libs.tslibs.nattype.NaTType):
            return ''
        elif isinstance(dat,datetime):
            return dat.strftime("%Y/%m/%d")
        else:
            return dat
    
    def _getDeltaDays(self,date_str):
        '''获取天数差值'''
        if isinstance(date_str,str):
            if '-' in date_str:
                date_happen = datetime.strptime(date_str,'%Y-%m-%d')
            elif '/' in date_str:
                date_happen = datetime.strptime(date_str,'%Y/%m/%d')
            else:
                return 0
        else:
            return 0
        return (datetime.now() - date_happen).days

