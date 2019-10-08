#main.py
#
#

import json
import sys,os
import threading
import asyncio

curPath    = os.path.dirname(__file__)
curPath1   = curPath + "\\pyppeteerlib"
curPath2   = curPath1 + "\\pyppeteer"
sys.path.append(curPath1)
sys.path.append(curPath2)
#from  enum import Enum
import enum
from   pyppeteer import launch

import re
import g_def
import rx_taskinfo
from   struct_def  import *

from   deal_crawler import *

import wx_taskinfo
from   struct_def  import *
from   log.logger import Logger 
from   common.tools import *
#from  log.logger import LogConfig
#
def testlog( ):
    
    pass
    

def testlog2(grapInfo):
    grapInfo.contentId += 1
           
def main(argv=None):
    print("enter main")
    
    testlog()
    #print(ret1)
    #print(ret2)
    #print(ret3)
    
    #rx_task_thread = threading.Thread(target = rx_taskinfo.rx_task_thread_func)
    #rx_task_thread.start()
    
    #wx_task_thread = threading.Thread(target = wx_taskinfo.wx_taskinfo_func)
    #wx_task_thread.start() 
    
    
    
    ret,data = JsonEx.makeTestJson()
    
    ret,spiderTaskBuf = JsonEx.parseSpiderJson(data)
    if ret == 0:
        for item in spiderTaskBuf:
            
            deal_Crawler_sites(item)
    else:
        pass
        CommonTool.app_print("doWork: JsonEx.parseSpiderJson exception")
        CommonTool.app_print(data)  
    
    #deal_Crawler_sites()
    
    

    #deal_main_compoundword_thread = threading.Thread(target = deal_Crawler_sites,args=(thread_loop,))
    #deal_main_compoundword_thread.start()

    #deal_site_main_item_thread = threading.Thread(target = deal_crawler.deal_site_main_item_thread_func,args = 5)
    #deal_site_main_item_thread.start()

    #deal_site_sub_item_thread = threading.Thread(target = deal_crawler.deal_site_sub_item_thread_func,args = 5)
    #deal_site_sub_item_thread.start() 
    
    #rx_task_thread.join()
    #loop = asyncio.get_event_loop()
    
    

if __name__ == "__main__":
    main()

