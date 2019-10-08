#---------------common_data.py
import  asyncio
import  logging
import  random
import  time
from pyppeteer.errors import *
import traceback
from pyppeteer import launch

import sys,os

sys.path.append("..")
sys.path.append(".")

from   pyteerex.pyppeteer_ex  import *
from   log.logger             import *
 
from   struct_def import *

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------- 
class   GrapDataDict(object):
    def __init__(self,grapData):
        if not grapData:
            self.dataDict   = {}
        else:
            self.dataDict  = self.fill(grapData)
    
    #----------------------------------------
    #set dataDict = empty
    def setDataDictEmpty(self):
        self.dataDict   = {}


    #----------------------------------------
    #create dict
    def fill(self,dataList):

        self.dataDict.clear()

        for item in dataList:
            strKey = self.createKey(item.pid,item.sid)
            if  strKey:
                if not strKey in self.dataDict:
                    self.dataDict[strKey] = item
    
    #-----------------------------------------------------
    #
    def getData(self,strPid,strSid):
        
        ret     = 1
        retData = None

        strKey  = self.createKey(strPid,strSid)
        if strKey:
            if strKey in self.dataDict:
                retData = self.dataDict[strKey]
                ret = 0
        
        return ret,retData

    #----------------------------------------------------
    # 
    def isExistKey(self,strPid,strSid):
        
        ret = False

        strKey = self.createKey(strPid,strSid)
        if strKey in self.dataDict:
            ret = True
        
        return ret
    #----------------------------------------------------
    # ret = 0: key不存在
    # ret = 1: key存在,但是记录的时间不同,读内容
    # ret = 2: key存在，时间相同
    def isExistKeyEx(self,strUrl,strPid,strSid,strTime):
        
        ret       = 0
        replyInfo = None
        
        #empty
        if not self.dataDict:
            ret = 0
            return ret,None
        
        #not empty
        strKey = self.createKey(strPid,strSid)

        if strKey in self.dataDict:
            replyInfo = self.dataDict[strKey]
            ret  = 1
        
        if ret == 1:
            if strTime == replyInfo.reply_time:
                ret = 2
        
        return ret,replyInfo


    #-----------------------------------------
    #create  key
    #key = 主回复pid + 子回复sid
    def createKey(self,strPid,strSid):
        strKey = ""

        if  strPid:
            strKey = "{}-{}".format(strPid,strSid)

        return strKey