#tools.py
import json
import sys,os
import re

sys.path.append("..")

from  struct_def  import *
from  socket      import *
import datetime
#import socket
import app

class CommonTool(object):
    def __init__(self):
        pass
    @staticmethod
    def strSplitIndex(curText,splitText,index):

        retStr   = ""
        curText  = curText.strip()
        try:
            splitBuf = curText.split(splitText)
            if len(splitBuf) > index:
                retStr = splitBuf[index]
        except Exception:
            pass

        return  retStr
    #-----------------------------------------------------------------
    #
    @staticmethod
    def strSplit(curText,splitText):

        splitBuf = []
        curText  = curText.strip()
        try:
            splitBuf = curText.split(splitText)
        except Exception:
            pass

        return  splitBuf
    #-----------------------------------------------------------------
    #从字符串中分离出数字
    @staticmethod
    def strSplitDigit(curText):

        splitBuf = []
        curText  = curText.strip()
        try:
            splitBuf = re.findall('\d+',curText)
        except Exception:
            pass

        return  splitBuf
    #-----------------------------------------------------------------
    #---去掉空格，回车，换行
    @staticmethod
    def strStripRet(curText):
        curText = curText.strip()
        return curText
    #-----------------------------------------------------------------
    @staticmethod
    def getDigitFromString(digitStr):

        count = 0
        try:
            strVal = re.sub('\D+',"",digitStr)
            count =CommonTool.strToInt(strVal)
        except:
            count = 0

        return count
    #-----------------------------------------------------------------
    @staticmethod
    def getDigitFromStr(digitStr):

        count = 0
        try:
            strVal = re.sub('\D+',digitStr)
            count =CommonTool.strToInt(strVal)
        except:
            count = 0

        return count
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    @staticmethod
    def app_print(msg):
        app.writeLog(msg)
        pass

    @staticmethod
    def app_commitTask(serverTaskId,logInfo=None):
        app.commitTask(serverTaskId)
        return 0
    #-----------------------------------------------------------------
    @staticmethod
    def app_commitBuf(replyBuf,logInfo=None):
        
        ret = 0

        #if logInfo != None:
        #        logInfo.show("CommonTool->app_commitInfo(): enter")
    
        ret1,strJson = JsonEx.makeSpiderJson(replyBuf )
        #if logInfo != None:
        #        logInfo.show("{}".format(strJson))

        if ret1 == 0:
            app.commit(strJson)
            if logInfo != None:
                logInfo.show("CommonTool->app_commitInfo(): call d->app.commit")
            pass
        else:
            ret = 1
            if logInfo != None:
                logInfo.show("CommonTool->app_commitInfo(): makeSpiderJson exception")
            
        return ret 
    
    #-----------------------------------------------------------------
    @staticmethod
    def app_commitInfo(replyInfo,logInfo=None):
        
        replyBuf= []
        replyBuf.append( replyInfo)
        
        return CommonTool.app_commitBuf(replyBuf,logInfo)
    
    
    #-----------------------------------------------------------------
    @staticmethod
    
    def sendSocket(datatype,task_id,jsonBuf=""):
        #app.commit(jsonBuf)
        """
        print("sock0")
        hostaddr = "127.0.0.1"
        port     = 4071
        bJsonBuf = b""

        if datatype == 0:
            print(jsonBuf)
            bJsonBuf1 = str.encode(jsonBuf)
            count     = len(bJsonBuf1) + 5
            bJsonBuf  = (count).to_bytes(4,byteorder = 'big') + b'\x01' + bJsonBuf1
        else:
            count     = 13
            bJsonBuf  = (count).to_bytes(4,byteorder = 'big') + b'\x02' + (task_id).to_bytes(8,byteorder = 'big')
        print("sock1")
        tcpCliSocket = socket(AF_INET,SOCK_STREAM)
        print("sock2")
        tcpCliSocket.connect((hostaddr,port))
        print("sock3")
        tcpCliSocket.send(bJsonBuf)
        print("sock4")
        tcpCliSocket.close()
        print("sock5")
        """
        
    @staticmethod
    #-----------------------------------------------------------------
    def strToInt(strVal):
        val = 0
        
        try :
            val = int(strVal.strip() )
        except ValueError:
            val = 0
        
        return val
        
    @staticmethod
    #---验证传入的字符串是否是有效时间格式 
    #---如果是则返回成功转化的时间数据
    def verifyDatetime(datetime_str):
        try:        
    	    ret = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')        
    	    return True,ret    
        except ValueError:        
    	    return False,None 
 
class JsonEx(object):
    def __init__(self):
        pass
    
    @staticmethod
    #-----------------------------------------------------------------
    #--str2 = unicode( str, errors='ignore')  -> 'utf8' codec can't decode byte ...
    #serverTaskId, origin, keyword, compoundword, maxPages, hotWord, snapshot, collect, analogClick, analogBrowse
    def makeTestJson():
        ret      = 0
        strJson  = ""
        mainDict = {}
        subBuf = []
        
        grapReplyInfoBuf= [ 1,2 ]

        for item  in    grapReplyInfoBuf:
            subDict = {}
            subDict["taskDetailsId"] = 1
            subDict["origin"]       = 10
            subDict["keyword"]      = "p30"
            subDict["compoundword"] = "p30" 
            subDict["maxPages"]     = 0
            subDict["hotWord"]      = 0
            subDict["snapshot"]     = 0
            subDict["collect"]      = 3
            subDict["analogClick"]  = 1
            subDict["analogBrowse"] = 0
               
            subBuf.append(subDict )
        
        #-----------------
        mainDict["data"] = subBuf
        
        try:
            strJson = json.dumps(mainDict )
        except Exception as e: 
            ret = 1
            print("makeSpiderJson:exception ") 
        
        return ret,strJson


    @staticmethod
    #-----------------------------------------------------------------
    #--str2 = unicode( str, errors='ignore')  -> 'utf8' codec can't decode byte ...
    def loads(strJson):
        
        strDict = None
        try:
            strJson1 = json.dumps(eval(strJson))
            strDict  = json.loads(strJson1,encoding='utf-8')
        except Exception as e:
            strDict = None 

        return strDict
    
    @staticmethod
    #-----------------------------------------------------------------
    #serverTaskId, contentId, parentContentId, pageNo, ranking, snapshots, url, title, content, publisher, publishTime, 
    # reads, forwards, stars, comments, hotWords, locateSymbol
    def makeSpiderJson(grapReplyInfoBuf):
        
        ret      = 0
        strJson  = ""
        mainDict = {}
        subBuf = []

        for item  in    grapReplyInfoBuf:
            subDict = {}
            
            subDict["taskDetailsId"]   = item.serverTaskId
            subDict["contentId"]       = item.contentId
            
            subDict["parentContentId"] = item.parentContentId
            subDict["pageNo"]          = item.pageNo
            subDict["ranking"]         = item.ranking

            subDict["snapshot"]        = item.snapshots
            subDict["url"]             = item.href
            subDict["pageUrl"]         = item.pageUrl
            subDict["title"]           = item.main_title
            subDict["content"]         = item.text
            
            subDict["publisher"]       = item.publisher
            subDict["publishTime"]     = item.publishTime

            subDict["reads"]           = item.reads
            subDict["forwards"]        = item.forwards
            subDict["stars"]           = item.stars
            subDict["comments"]        = item.comments
            subDict["hotWords"]        = item.hotWords
            subDict["locateSymbol"]    = item.locateSymbol 
            

            
            subBuf.append(subDict )
        
        #-----------------
        mainDict["data"] = subBuf
        
        try:
            strJson = json.dumps(mainDict )
        except Exception as e: 
            ret = 1
            print("makeSpiderJson:exception ") 
        
        #print(strJson)
        return ret,strJson
           

    @staticmethod
    #-----------------------------------------------------------------
    def parseSpiderJson(jsonStr):
    
        ret     = 1
        dataBuf = [ ]
        key = "data"

        try:
            jsonDict = json.loads(jsonStr,encoding='utf-8')
            print(jsonDict )

            if jsonDict is not None:
                if key in jsonDict.keys():
                    #print(jsonDict["data"])
                    for item in jsonDict["data"]:

                        spider = SpiderTaskInfo()
                        #
                        key1 = "taskDetailsId"
                        if key1 in item.keys():
                            spider.serverTaskId = item[key1]
                            print("spider.serverTaskId= " ,spider.serverTaskId)
                        
                        #
                        key1 = "origin"
                        if key1 in item.keys():
                            spider.origin = item[key1]
                            print("spider.origin= " ,spider.origin)
                        #
                        key1 = "keyword"
                        if key1 in item.keys():
                            spider.keyword = item[key1]
                            print("spider.keyword= " ,spider.keyword) 
                        #
                        key1 = "compoundword"
                        if key1 in item.keys():
                            spider.compoundword = item[key1]
                            print("spider.compoundword= " ,spider.compoundword)   
                        
                        #
                        key1 = "maxPages"
                        if key1 in item.keys():
                            spider.maxPages = item[key1] 
                            print("spider.maxPages= " ,spider.maxPages)
                        #
                        key1 = "hotWord"
                        if key1 in item.keys():
                            spider.hotWord = item[key1] 
                            print("spider.hotWord= " ,spider.hotWord)
                        #
                        key1 = "targetUrl"
                        if key1 in item.keys():
                            spider.targetUrl = item[key1]
                            print("spider.targetUrl= " ,spider.targetUrl)     
                        #
                        key1 = "snapshot"
                        if key1 in item.keys():
                            spider.snapshot = item[key1]
                            print("spider.snapshot= " ,spider.snapshot) 
                        #
                        key1 = "collect"
                        if key1 in item.keys():
                            spider.collect = item[key1]
                            print("spider.collect= " ,spider.collect) 
                        #
                        key1 = "analogClick"
                        if key1 in item.keys():
                            spider.analogClick = item[key1] 
                            print("spider.analogClick= " ,spider.analogClick)
                        #
                        key1 = "analogBrowse"
                        if key1 in item.keys():
                            spider.analogBrowse = item[key1] 
                            print("spider.analogBrowse= " ,spider.analogBrowse)

                        dataBuf.append(spider )

        except Exception as e: 
            print("parseSpiderJson:exception ")
        
        if len(dataBuf) > 0:
            ret = 0
        
        return ret,dataBuf
    