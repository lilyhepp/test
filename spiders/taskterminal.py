# spiders.taskterminal python script

# App API:
# 1. app.writeLog("...")
# 2. app.commit(data)
import sys,os

curPath    = os.path.dirname(__file__)
curPath1   = curPath + "\\pyppeteerlib"
curPath2   = curPath1 + "\\pyppeteer"
sys.path.append(curPath1)
sys.path.append(curPath2)

from   struct_def  import  *
from   deal_crawler import *
from   common.tools import *


def doWork(data):
    # parse json data: serverTaskId, origin, keyword, compoundword, maxPages, hotWord, snapshot, collect, analogClick, analogBrowse
    print("enter doWork")
    
    #ret,data = JsonEx.makeTestJson()
    ret,spiderTaskBuf = JsonEx.parseSpiderJson(data)
    if ret == 0:
        for item in spiderTaskBuf:
            deal_Crawler_sites(item)
    else:
        CommonTool.app_print("doWork: JsonEx.parseSpiderJson exception")
        CommonTool.app_print(data) 
    
    result = 0
    description = ""

    print("exit doWork")

    return result, description
    
#if __name__ == __doWork__:
 #   dowork()
    
    
