#search_base_site.py
import  sys,os
import  asyncio
import  logging
import  random
import  time
from    pyppeteer.errors import *
import  traceback
from    pyppeteer import launch

sys.path.append("..")
sys.path.append(".")

from   pyteerex.pyppeteer_ex  import *
from   log.logger             import *

from   struct_def             import *
from   common.tools           import *
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
class  CrawlerBase(object):
    #----------------------------------------------------------------
    def __init__(self,crawlerSubNum):
        self.subCoroutineNum     = crawlerSubNum+1
        self.topSubItemQueue     = asyncio.Queue()
        self.topSubItemFailQueue = asyncio.Queue()
        self.replyQueue          = asyncio.Queue()
        self.terminateCrawlerList = [0,0]
       
        self.queueDict   = {'subItemQueue': self.topSubItemQueue,
                            'subItemFailQueue': self.topSubItemFailQueue,
                            'subReplyQueue':      self.replyQueue,
                            'isTerminateCrawler': self.terminateCrawlerList,
                           }

        self.browserDict  = {
                                'browser':None,
                            }

    #----------------------------------------------------------------
    #--关键字抓取------以翻页的方式或滚动的方式抓取数据
    #--objList:类对象列表
    #--crawlerTaskInfo: 抓取信息结构
    #--grapTypeFunc:抓取类型对应的函数  =0:关键字抓取-主函数  =1:关键字抓取-子函数
    #--subColNum:子抓取时，子协程函数个数,当为主抓取时，需要传这个参数
    #--isAsPage: =1:以分页的方式抓取数据  =0:以滚动或点击的方式抓取数据
    #--colTastList:返回添加的协程函数list
    def crawlerAsPageOrScroll(self,objList,crawlerTaskInfo,grapTypeFunc,subColNum,isAsPage,colTastList ):

        print("CrawlerBase->crawlerAsPageOrScroll(): enter")

        #关键字--主抓取
        if grapTypeFunc == GrapTypeFuncEm.KeyMain.value:
            for item in objList:
               colTask = item.crawlerMain(crawlerTaskInfo,subColNum,isAsPage) 
               colTastList.append(colTask)
               print(len(colTastList))
        #关键字--子抓取
        elif grapTypeFunc == GrapTypeFuncEm.KeySub.value:
            for item in objList:
                colTask = item.crawlerSub(crawlerTaskInfo,isAsPage) 
                colTastList.append(colTask)
                print(len(colTastList))
        #抓取指定网页
        elif grapTypeFunc == GrapTypeFuncEm.DefUrl.value:
            for item in objList:
                colTask = item.crawlerDefUrl(crawlerTaskInfo,isAsPage) 
                colTastList.append(colTask)
                print(len(colTastList))
        #


        print("CrawlerBase->crawlerAsPageOrScroll(): exit")

    #---------------------------------------------------------------
    #--将协程函数加入到事件循环
    def allColTastToLoop(self,loop,colTastList):
        print("allColTastToLoop ")
        loop.run_until_complete(asyncio.wait(colTastList))

    
    #----------------------------------------------------------------
    #
    def closeBrowser(self,loop):
        
        taskGroup = [ ]
        browser   = self.browserDict["browser"]

        colTask = self.closeBrowserCol(browser)
        taskGroup.append(colTask)

        loop.run_until_complete(asyncio.wait(taskGroup))
    #----------------------------------------------------------------
    #
    async def closeBrowserCol(self,browser):
        if browser is not None:
            pass
            #pyteerEx = PyteerEx(None,None)
            #await pyteerEx.closeBrower(browser)
    
    #------------------------------------------------------------------
    def crawlerAsWaterfall(self):
        pass


#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
class   CrawlerSiteScrollBase(object):
    #def __init__(self,crawlerType,curQueue,failQueue):
    def __init__(self,crawlerType,queueDict,configParaInfo):
        #---------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        #--调用clickHoverElement()函数时,click的延迟 
        self.clkh_click_delay    = 1
        #--调用clickHoverElement()函数时,hover的延迟
        self.clkh_hover_delay    = 1
        #----------------------------
        #--是否检查当前网址是首页
        self.isCheckFirstPage          = True
        #base
        self.isFailNewPageAsCurUrl     = True
        #当抓取一页后，是否创建新的浏览器打开下一页
        self.isAllwaysNewPage          = False
        #是否使用代理
        self.isUseAgent                = False
        #是否是无头模式
        self.isHeadless                = False 
        #滚动方式时，失败允许的最大重试次数
        
        #configParaInfo.browserHeadless
        #
        parentDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parentDir = parentDir + "\\..\\browser\\chromium\\chrome.exe" 
        self.browserPath               = parentDir
        #----------------------------------
        #----other
        #crawlerType
        self.crawlerType          = crawlerType

        #queue
        strKey  = "subItemQueue"
        if strKey in queueDict:
            self.topSubItemQueue      = queueDict[strKey]
        else:
            self.topSubItemQueue      = None
        #fail
        strKey  = "subItemFailQueue"
        if strKey in queueDict:
            self.topSubItemFailQueue  = queueDict[strKey]
        else:
            self.topSubItemFailQueue  = None
        #reply
        strKey  = "subReplyQueue"
        if strKey in queueDict:
            self.SubReplyQueue        = queueDict[strKey]
        else:
            self.SubReplyQueue        = None
        
        #isExit 终止爬虫的抓取:当后面抓取的内容中不包含关键字
        strKey = "isTerminateCrawler"
        if strKey in queueDict:
            self.isTerminateCrawlerList    = queueDict[strKey]
        else:
            self.isTerminateCrawlerList    = None
        
        #---配置判断抓取数据为小说的条件
        #--内容的最大字节数
        self.novelMaxWordCount   = 200
        #--连续出现最大字节数次数
        self.novelTerminateCount =  5
        #---------------------------------------
        #---终止子页的抓取数量
        self.terminateSubPageMaxCount = 30
        #---子页抓取数据为空的数量
        self.subPageDataEmptyMaxCount = 20


        #logging
        self.log_grap          = None
        self.log_info          = None
        self.log_exception     = None
        self.curLogLevel       = LogLevel.Debug

        #pyppeteer
        self.pyteerEx          = None
        

        #page ,browser
        self.g_page            = None
        self.g_browser         = None
        #self.g_brower_dict = browerDict
        self.g_brower_dict = {'browser':None}

        #lauch para
        self.browserWidth   = 1500
        self.browserHeight  = 800
        self.lauchOption      = {'headless':self.isHeadless,'dumpio':True,'executablePath':self.browserPath} 
        self.viewPortWnd      = {'width': self.browserWidth, 'height': self.browserHeight}
        self.lauchKwargsAgent = ['--disable-infobars','--proxy-server=http://http-dyn.abuyun.com:9020','--no-sandbox', f'--window-size={self.browserWidth},{self.browserHeight}']
        self.lauchKwargs      = ['--disable-infobars','--no-sandbox', f'--window-size={self.browserWidth},{self.browserHeight}']
        self.lauchKwargsList  = [self.lauchKwargs  ,self.lauchKwargsAgent ]
        
        self.agentPara        = {'username':'H1844297NU1ZVRKD','password':'42B1F1EB068A3494'}
        #---------------------------------------------------------------------------------------------------------
        #css page buttons
        self.cssPageBtnDict = {
                               'prePageBtn':"",
                               'curPageBtn':"",
                               'curPageText':"",
                               'nextPageBtn':""
                              }

        #param next page Navigate
        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.searchEditDelayMin = 30
        self.searchEditDelayMax = 80
        self.clickTimeoutMs     = 25000
        self.cssSearchDict     = {
                                  'inputBox': "",
                                  'clkButton':"",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }
        
        #----------------------------------------------------------
        #--以滚动的方式加载页面时，指定调用autoScroll函数的次数
        self.autoScrollCount           = 10
        #--以滚动的方式加载页面时，指定滚动到底后，下次滚动的延迟,单位秒
        self.autoScrollOnceDelay       = 0.2
        #以滚动-点击页面元素方式加载页面时,定义点击按钮的css值
        self.cssAutoScrollClk = {
                                'clkButton':"",    #css
                                'clickDelay':0.4,  #click delay
                                'hoverDelay':0.4,  #hover delay
                                }
        #----------------------------------------------------------
        #main href text
        self.cssMainItemHrefText = {
                                    'main':"",
                                    'sub' :""
                                   }
    #--------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------
    # func define  
    #--------------------------------------------------------------------------------------
    #
    async def  login(self,page):
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #
    async def autoScrollAsPage(self,page,crawlerInfo):
        ret = await self.pyteerEx.autoScroll(page,self.autoScrollStep )
        return ret

    #--------------------------------------------------------------------------------------
    #
    async def searchWord(self,page,compoundword):
        return RetVal.Suc.value,None

    #--------------------------------------------------------------------------------------
    #
    #
    async def  dealMainScrollBefor(self,page,crawlerInfo):
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #
    async def  dealMainOther(self,page,crawlerInfo):
        return RetVal.Suc.value
    
    #--------------------------------------------------------------------------------------
    #
    async def  dealSubOther(self,page):
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerPage(self,page,crawlerInfo,index):
        
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #检查当前页是否是第一页，不是则获取第一页的url
    # ret = 0: 当前页是首页
    # ret = 1: 当前页不是首页,获取了首页的地址
    # ret = 2: 当前页不是首页,获取首页地址失败
    async def  checkFirstPage(self,page):
        return RetVal.Suc.value,""

    #--------------------------------------------------------------------------------------
    #wait for a page loading
    async def  waitforPageLoad(self,page):
        ret = await self.pyteerEx.waitPage(page,self.cssPageBtnDict["curPageBtn"],4)
        return ret
    #-------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------ 
    #-------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------
    #
    async def closePage(self,page):
        await self.pyteerEx.closePage(page)    
        self.g_page = None

    #-----------------------------------------------------------------
    #        
    async def closeBrowser(self):
        browser = self.g_brower_dict["browser"]
        
        await self.pyteerEx.closeBrower(browser)
        self.g_brower_dict["browser"] = None
        self.g_page    = None
    #-----------------------------------------------------------------
    #
    def setBrowser(self,browser):
        self.g_brower_dict["browser"] = browser
    #-----------------------------------------------------------------
    #
    def getBrowser(self):
        return self.g_brower_dict["browser"]


    #----------------------------------------------------------------
    #---转换url需要更换url 则在子类重写
    def convertUrl(self,originalUrl):
        return originalUrl
        
    #------------------------------------------------------------------
    #----socket 获取跳转后的链接
    def httpRequest(self,host,port,query):
        try:
            request = 'GET ' + query + ' HTTP/1.1\r\n'
            request = request + 'Host: ' + host + ':' + str(port) + '\r\nConnection: Keep-Alive\r\nCache-Control: no-cache\r\n\r\n'
            BUFSIZE = 8192
            ADDR = (host, port)

            tcpCliSock = socket(AF_INET, SOCK_STREAM)
            tcpCliSock.connect(ADDR)
            tcpCliSock.send(request.encode())
            response = tcpCliSock.recv(BUFSIZE).decode()
        except Exception:
            return host + query
        finally:
            tcpCliSock.close()

        return response

    #-----------------------------------------------------------------
    #   递增子页抓取数据为空的数量
    #   
    def IncreSubPageDataEmptyCount(self):
        ret = RetVal.Fail.value
        self.isTerminateCrawlerList[1] += 1
        if self.isTerminateCrawlerList[1] > self.subPageDataEmptyMaxCount:
            self.setIsTerminateCrawler(True)
            ret = RetVal.Suc.value
        return ret
    #-----------------------------------------------------------------
    #   清除子页抓取数据为空的数量
    #   
    def ZeroSubPageDataEmptyCount(self):
        self.isTerminateCrawlerList[1] = 0
    #-----------------------------------------------------------------
    #   判断是否结束主页和子页的抓取
    #   
    def IsTerminateCrawlerAsEmpty(self):
        ret = RetVal.Fail.value
        if self.isTerminateCrawlerList[1] > self.subPageDataEmptyMaxCount:
            self.setIsTerminateCrawler(True)
            ret = RetVal.Suc.value
        
        return ret
        
    

    #-----------------------------------------------------------------
    #   设定是否终止抓取
    #   isTerminate ->  = True:终止抓取  =False:不终止抓取
    def setIsTerminateCrawler(self,isTerminate):
        ret = 0
        if isTerminate:
            ret = 1
        self.isTerminateCrawlerList[0] = ret
    #-----------------------------------------------------------------
    #   设定是否终止抓取
    #   return -> =True:需要停止抓取  =False:不停止抓取
    def getIsTerminateCrawler(self):
        ret = False
        if self.isTerminateCrawlerList[0] == 1:
            ret = True
        return  ret
    #-----------------------------------------------------------------

    def printLogInfo(self,msg,level= LogLevel.Debug):
        self.log_info.show(msg)
    #-----------------------------------------------------------------
    #
    def printGrapInfo(self,msg,level = LogLevel.Normal):
        self.log_grap.show(msg)
    #-----------------------------------------------------------------
    #
    def printExcepInfo(self,msg):
        self.log_exception.show(msg)
     
    #-----------------------------------------------------------------
    def getLogInfo(self):
        return self.log_info
    #----------------------------------------------------------------
    def app_commitBuf(self,replyBuf):
        return CommonTool.app_commitBuf(replyBuf,self.getLogInfo())
    #-----------------------------------------------------------------
    #--------------------------------------------------------------------------------------
    def log_inits(self,sub_dir,grap_type,log_type,grap_level=logging.INFO, log_level=logging.INFO):
        path   = sub_dir + "/grap"
        self.log_grap  = Logger(path,grap_type,grap_level)  #logging.INFO

        path   = sub_dir + "/log"
        self.log_info  = Logger(path,log_type,log_level)

        path   = sub_dir + "/exception"
        self.log_exception  = Logger(path,log_type,log_level)
        
        self.pyteerEx   = PyteerEx(self.log_info,self.log_exception)
    

    
    #--------------------------------------------------------------------------------------
    #search compoundword
    async def  searchWordNewPage(self,page,strCompoundword):
        self.printLogInfo("CrawlerSiteScrollBase->searchWord() : enter")

        strEditCss   = self.cssSearchDict["inputBox"]
        strBtnCss    = self.cssSearchDict["clkButton"]
        editDelayMin = self.cssSearchDict["editDelayMin"]
        editDelayMax = self.cssSearchDict["editDelayMax"]
        waitTimeMs   = self.cssSearchDict["waitTimeoutMs"]
        waitUntill   = self.cssSearchDict["waitUntill"]
        newPage      = None
        browser      = self.getBrowser()
        
        ret,newPage = await self.pyteerEx.searchNavigateNewPage(browser,page,strCompoundword,strEditCss,strBtnCss,editDelayMin,editDelayMax ,waitTimeMs,waitUntill)
        if ret != RetVal.Suc.value:
            key = "inputBox1"
            if key in self.cssSearchDict.keys():
                strEditCss = self.cssSearchDict["inputBox1"]
                strBtnCss  = self.cssSearchDict["clkButton1"]
                ret,newPage = await self.pyteerEx.searchNavigateNewPage(browser,page,strCompoundword,strEditCss,strBtnCss,editDelayMin,editDelayMax ,waitTimeMs,waitUntill)

        self.printLogInfo("CrawlerSiteScrollBase->searchWord() : exit") 
        
        if ret == RetVal.Suc.value:
            self.g_page = newPage

        return ret,newPage   

    #--------------------------------------------------------------------------------------
    #search compoundword
    async def  searchWordBase(self,page,strCompoundword):
        
        self.printLogInfo("CrawlerSiteScrollBase->searchWord() : enter")

        strEditCss   = self.cssSearchDict["inputBox"]
        strBtnCss    = self.cssSearchDict["clkButton"]
        editDelayMin = self.cssSearchDict["editDelayMin"]
        editDelayMax = self.cssSearchDict["editDelayMax"]
        waitTimeMs   = self.cssSearchDict["waitTimeoutMs"]
        waitUntill   = self.cssSearchDict["waitUntill"]
        newPage      = None

        ret = await self.pyteerEx.searchNavigate(page,strCompoundword,strEditCss,strBtnCss,editDelayMin,editDelayMax ,waitTimeMs,waitUntill)
        if ret != RetVal.Suc.value:
            key = "inputBox1"
            if key in self.cssSearchDict.keys():
                strEditCss = self.cssSearchDict["inputBox1"]
                strBtnCss  = self.cssSearchDict["clkButton1"]
                ret = await self.pyteerEx.searchNavigate(page,strCompoundword,strEditCss,strBtnCss,editDelayMin,editDelayMax ,waitTimeMs,waitUntill)

        self.printLogInfo("CrawlerSiteScrollBase->searchWord() : exit")

        return  ret,newPage
    #--------------------------------------------------------------------------------------
    #
    async def  putReplyQueue(self,replyInfo):

        if self.SubReplyQueue is not None:
            await self.SubReplyQueue.put(replyInfo )
            
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #子抓取-抓取整页html
    async def  dealSubCrawlerAsHtml(self,page,crawlerInfo,index):
        ret = RetVal.Suc.value

        return ret,[]
    #--------------------------------------------------------------------------------------
    #子抓取--抓取整页text
    async def  dealSubCrawlerAsText(self,page,crawlerInfo,index):
        ret = RetVal.Suc.value

        return ret,[]
    #--------------------------------------------------------------------------------------
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        ret = RetVal.Suc.value

        return ret,[]
    #-------------------------------------------------------------------------------------
    #子抓取--抓nothing
    async def dealSubCrawlerAsNothing(self,page,crawlerInfo,index):
        ret = RetVal.Suc.value

        return ret,[]
    #-------------------------------------------------------------------------------------
    #子抓取--指定网址抓取
    async def dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):
        ret = RetVal.Suc.value

        return ret,[]
    


    #--------------------------------------------------------------------------------------
    #
    async def crawlerAsCommonMain(self,crawlerInfo,isAsPage):

        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommonMain() : enter") 
        
        crawlerInfo.grap_buf = []
        ret = RetVal.Suc.value

        if isAsPage == GrapScrollEm.Page.value:
            ret = await  self.crawlerAsPage(crawlerInfo)
        elif isAsPage == GrapScrollEm.VScroll.value:
            ret = await self.crawlerAsVScroll(crawlerInfo)
        
        if len(crawlerInfo.grap_buf) > 0:
            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommonMain() : call app_commitBuf to send data to server. buf_len={}".format( len(crawlerInfo.grap_buf)))
            CommonTool.app_commitBuf(crawlerInfo.grap_buf)

        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommonMain() : exit")
        return ret
    #--------------------------------------------------------------------------------------
    #
    async def crawlerAsCommonSub(self,crawlerInfo,isAsPage):

        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommonSub() : enter") 
        
        crawlerInfo.grap_buf = []
        ret = RetVal.Suc.value

        if isAsPage == GrapScrollEm.Page.value:
            ret = await  self.crawlerAsPage(crawlerInfo)
        elif isAsPage == GrapScrollEm.VScroll.value:
            ret = await self.crawlerAsVScroll(crawlerInfo)
        
        #---call commit
        if len(crawlerInfo.grap_buf) > 0:

            self.ZeroSubPageDataEmptyCount()
            """
            #标题包含关键字
            if self.checkTitleIncludeKeyword(crawlerInfo) == RetVal.Suc.value:
                crawlerInfo.keywordInGrapBufCount += 1
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommon() : keyword in title->count={}".format(crawlerInfo.keywordInGrapBufCount))
            #
            else:
                #--内容包含关键字
                if self.checkContextIncludeKeyword(crawlerInfo,crawlerInfo.grap_buf) == RetVal.Suc.value:
                    crawlerInfo.keywordInGrapBufCount += 1
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommon() : keyword in context->count={}".format(crawlerInfo.keywordInGrapBufCount))
                else:  #--找不到关键字，则停止抓取
                    self.setIsTerminateCrawler(True)
                    crawlerInfo.grap_buf.clear()        
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommon() : keyword not in context,break list grap")
            """        
            #-------------------
            #--
            if len(crawlerInfo.grap_buf) > 0: 
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommon() : call app_commitBuf to send data to server. buf_len={}".format( len(crawlerInfo.grap_buf)))
                CommonTool.app_commitBuf(crawlerInfo.grap_buf)
            
            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommon() : grap one list item success and send data to server finish")
        #---------------------
        #----记录为空
        else:
            self.IncreSubPageDataEmptyCount()    
        
        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsCommon() : exit")

        return ret

    #--------------------------------------------------------------------------------------
    #抓取指定的网址   
    async def  crawlerDefUrl(self,crawlerTaskInfo,isAsPage):
        
        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsDefUrl() : enter") 

        crawlerInfo = CrawlerInfo(crawlerTaskInfo.url,crawlerTaskInfo.keyword,crawlerTaskInfo.compoundword,1,crawlerTaskInfo.grap_mapData)
        crawlerInfo.copyAsSpider(crawlerTaskInfo)

        #--novelInfo
        noveInfo = NovelInfo(self.novelTerminateCount,self.novelMaxWordCount, crawlerInfo.keyword)
        crawlerInfo.noveInfo = noveInfo

        ret  = await  self.crawlerAsCommonSub(crawlerInfo,isAsPage)
        
        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsDefUrl() : exit")

        await self.closeBrowser()

        return ret

    #--------------------------------------------------------------------------------------
    #--抓取主页面函数
    #main结束时，要判断队列中任务数，当任务为0时，抓取结束           
    async def  crawlerMain(self,crawlerTaskInfo,subTaskLen,isAsPage):

        self.printLogInfo("CrawlerSiteScrollBase->crawlerMain() : enter")

        crawlerInfo = CrawlerInfo(crawlerTaskInfo.url,crawlerTaskInfo.keyword,crawlerTaskInfo.compoundword,0,crawlerTaskInfo.grap_mapData)
        crawlerInfo.copyAsSpider(crawlerTaskInfo)
        
        ret  = await  self.crawlerAsCommonMain(crawlerInfo,isAsPage)
        
        self.printLogInfo("CrawlerSiteScrollBase->crawlerMain() : grap main item finish,wait to sub grap",LogLevel.Normal)
        
        #wait finish
        ret1 = await self.waitSubQueueFinish(self.topSubItemQueue )
        if ret1 == RetVal.Suc.value:
            self.printLogInfo("CrawlerSiteScrollBase->crawlerMain() : grap sub finish",LogLevel.Normal)
            #-let sub coco exit
            count =  subTaskLen
            while count > 0:
                count -= 1
                grapItem = GrapTopItemInfo("","","",True)
                await self.topSubItemQueue.put(grapItem )


        self.printLogInfo("CrawlerSiteScrollBase->crawlerMain() : all grap success to exit")
        await self.closeBrowser()
        self.printLogInfo("CrawlerSiteScrollBase->crawlerMain() : all grap success to exit1")
        CommonTool.app_commitTask(crawlerTaskInfo.serverTaskId)

        

        return ret     
    
    #--------------------------------------------------------------------------------------
    #--抓取子页面函数           
    async def  crawlerSub(self,crawlerTaskInfo,isAsPage):
        
        self.printLogInfo("CrawlerSiteScrollBase->crawlerSub() : enter")
        keywordInGrapBufCount = 0

        while True:
            
            topSubItem = await self.topSubItemQueue.get( )
            
            if not self.getIsTerminateCrawler() :
                crawlerInfo = CrawlerInfo(topSubItem.url,crawlerTaskInfo.keyword,topSubItem.compoundword,1,crawlerTaskInfo.grap_mapData)
                crawlerInfo.copyAsSpider(crawlerTaskInfo)
                crawlerInfo.copyAsTopItemInfo(topSubItem )

                crawlerInfo.keywordInGrapBufCount = keywordInGrapBufCount
                #--novelInfo
                noveInfo = NovelInfo(self.novelTerminateCount,self.novelMaxWordCount, crawlerInfo.keyword)
                crawlerInfo.noveInfo = noveInfo

                if not topSubItem.is_finish:
                    ret  = await  self.crawlerAsCommonSub(crawlerInfo,isAsPage) 
                    keywordInGrapBufCount = crawlerInfo.keywordInGrapBufCount   
                else:
                    await self.closeBrowser()
                    break
                
            else:
                self.printLogInfo("CrawlerSiteScrollBase->crawlerSub() : set TerminateCrawler ,and wait topSubItem.is_finish")
                if not topSubItem.is_finish:
                    continue  
                else:
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerSub() : terminate current crawler and exit")
                    await self.closeBrowser()
                    break
        #---------------------------------------------------------------------
        #--while true end
            
        self.printLogInfo("CrawlerSiteScrollBase->crawlerSub() : finish and exit")

        return RetVal.Suc.value
    
    #--------------------------------------------------------------------------------------
    #   以向下滚动的方式，浏览数据
    async def  crawlerAsVScroll(self,crawlerInfo):

        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : enter")
        
        #---
        lastPageItemNo     = 0
        preLastPageItemNo  = 0
        isFinish           = RetVal.GrapFailExit.value
        loginFailCount     = 0
        searchFailCount    = 0
        waitPageFailCount  = 0


        is_first         = True
        url              = crawlerInfo.url
        url_cur          =  url
        url_next         =  url
        url_main_last    =  url
        url_sub_last     =  url
        url_main_same_count = 0
        url_sub_same_count  = 0
        url_main_same_limit = 10
        url_sub_same_limit  = 10

        compoundword     = crawlerInfo.compoundword
        gotoUrlFailCount = 0
        ret              = RetVal.Fail.value
        browser          = None
        page             = None

        #-------
        curMainCount     = 0
        mainCountLimit   = 30
        
        
        while True:
            try:
                isFinish   = RetVal.GrapFailExit.value
                curMainCount += 1

                #---------------
                #超过最大次数，则直接退出
                if curMainCount > mainCountLimit:
                    isFinish   = RetVal.GrapFailExit.value
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : url={} fail,max repeat count".format(url_cur),LogLevel.Fail)
                    break

                #----------------
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : begin to open url={}".format(url_cur))
                
                browser, page = await self.openUrl(url_cur,self.lauchOption,self.lauchKwargsList,self.viewPortWnd )
                
                
                if page is None:

                    isFinish = RetVal.GrapFailExit.value
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : open url={} fail,exit".format(url_cur),LogLevel.Fail)
                    break

                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : success to open url")
                
                #-------滚动之前添加操作
                ret = await self.dealMainScrollBefor(page,crawlerInfo)
                if ret != RetVal.Suc.value:
                    if ret == RetVal.SucExit.value:          #针对需要点一下的
                        isFinish = RetVal.GrapSuc.value
                        break
                    elif ret == RetVal.FailExit.value:
                        isFinish = RetVal.GrapFailExit.value
                        break
                    else:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() :dealMainScrollBefor fail,ignore  ",LogLevel.Fail)
                    
                
                #-------login 
                if is_first:
                    #login 
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : begin to login")
                    ret = await self.login(page)
                    if ret != RetVal.Suc.value:
                        loginFailCount += 1
                        if loginFailCount > 3:
                            isFinish = RetVal.GrapFailExit.value
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : login fail,exit",LogLevel.Fail)
                            break
                        else:
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : login fail,repeat count={}".format(loginFailCount),LogLevel.Fail)
                            await self.closeBrowser()
                            continue
                    
                    #search
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : begin to searchWord")
                    ret,newPage = await  self.searchWord(page,compoundword)
                    if ret != RetVal.Suc.value:
                        searchFailCount += 1
                        if searchFailCount > 3:
                            isFinish = RetVal.GrapFailExit.value
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : search fail,exit",LogLevel.Fail)
                            break
                        else:
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : search fail,repeat count={}".format(searchFailCount),LogLevel.Fail)
                            await self.closeBrowser()
                            continue
                    #针对    
                    if newPage is not None:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : get new page count={}".format(searchFailCount),LogLevel.Fail)
                        page = newPage
                    #------
                    loginFailCount  = 0
                    searchFailCount = 0
                
                

                #---------wait load
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : begin to waitforPageLoad")
                ret = await self.waitforPageLoad(page)
                if ret != RetVal.Suc.value:
                    waitPageFailCount += 1

                    if waitPageFailCount > 3:
                        isFinish = RetVal.GrapFailExit.value
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : waitforPage fail,exit",LogLevel.Fail)
                        break
                    else:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsVScroll() : waitforPage fail,repeat count={}".format(waitPageFailCount),LogLevel.Fail)
                        await self.closeBrowser()
                        continue
                    
                waitPageFailCount = 0    
                is_first          = False

               
                #------------------------------------------------------------------------------------------
                #------------------------------------------------------------------------------------------
                # sub page
                curCount = 0
                ret1     = 0
                msg      = ""
                crawlerInfo.url    = page.target.url
                self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll() : begin to sub loop")
                while True:
                    isFinish   = RetVal.GrapSucRepeat.value
                    curCount  += 1
                    
                    #-----scroll,
                    self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll()->loop={} : begin to scroll".format(curCount))
                        
                    ret1     = await self.autoScrollAsVScroll(page,crawlerInfo)
                    isFinish = ret1
                    if ret1  != RetVal.Suc.value:
                        self.printLogInfo("CrawlerSiteScrollBase->mainCrawler()->loop{} : scroll fail".format(curCount),LogLevel.Fail)
                        if ret1 !=  RetVal.Fail.value:
                            isFinish = self.dealCrawlerFail(ret1)   
                            break

                    #------wait 
                    ret1 = await self.waitforPageLoad(page)
                    if ret1 != RetVal.Suc.value:
                        if ret1 == RetVal.FailRepeat.value:
                            isFinish = RetVal.GrapFailRepeat.value
                            break
                        elif ret1 == RetVal.FailExit.value:
                            isFinish = RetVal.GrapFailExit.value
                            break

                    #---------deal crawler 
                    self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll() : dealSubCrawlerPage begin")

                    
                    ret1  = await self.dealSubCrawlerPage(page,crawlerInfo,curCount)
                    if ret1 == RetVal.Suc.value:
                        self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll()->loop{} : dealSubCrawlerPage sucess".format(curCount))
                    
                    else:
                        self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll()->loop{} : dealSubCrawlerPage fail".format(curCount),LogLevel.Fail) 
                    
                        if ret1 !=  RetVal.Fail.value:
                            isFinish = self.dealCrawlerFail(ret1)   
                            break
                    
                    self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll() : dealSubCrawlerPage end")
                    #---------------检查是否终止抓取
                    ret1 = self.getIsTerminateCrawler()
                    if ret1 :
                       isFinish =  RetVal.GrapExitNotFindKeyword.value
                       break
                    #---------   
                    self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll() : dealSubGotoNextPage begin")

                    isFinish = await self.dealGotoNextVScroll(page,crawlerInfo)

                    if isFinish != RetVal.GrapSucRepeat.value:
                        self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll()->loop{} : break current loop isFinish={}".format(curCount,isFinish),LogLevel.Fail)
                        break

                    self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll() : dealSubGotoNextPage end")
                #--------内层while True结束:

                #-----------------------------------------------------------------
                # ----------------------------------------------------------------    
                # --   
                if  isFinish == RetVal.GrapFailRepeat.value:
                    if  self.isFailNewPageAsCurUrl:
                            self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll()->grap fail,and repeat url={}".format(url_cur),LogLevel.Fail)
                            await self.closeBrowser()
                            continue 
                        
                    else:
                        break
                else:
                    break    

            #---------------------------------------------------
            #--处理异常
            except  Exception as e:
                self.printExcepInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll(): main Exception")
                self.printExcepInfo(e)
                self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll(): main Exception")
                self.printLogInfo(e)

                isFinish = RetVal.GrapFailExit.value
                break
        #---------------------------------------------------------
        #--外层while true 结束

        self.showIsFinishMsg(isFinish,False)

        if isFinish == RetVal.GrapSuc.value:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value

        self.printLogInfo("CrawlerSiteScrollBase->mainCrawlerAsVScroll()->: exit")

        return ret

    #--------------------------------------------------------------------------------------
    #以分页的方式抓取数据
    async def  crawlerAsPage(self,crawlerInfo):
        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : enter")

        #---
        lastPageItemNo     = 0
        preLastPageItemNo  = 0
        isFinish           = RetVal.GrapFailExit.value
        loginFailCount     = 0
        searchFailCount    = 0
        waitPageFailCount  = 0


        is_first         = True
        url              = crawlerInfo.url
        url_cur          =  url
        url_next         =  url
        url_main_last    =  url
        url_sub_last     =  url
        url_main_same_count = 0
        url_sub_same_count  = 0
        url_main_same_limit = 10
        url_sub_same_limit  = 10

        compoundword          = crawlerInfo.compoundword
        gotoUrlFailCount = 0
        ret              = RetVal.Fail.value
        browser          = None
        page             = None
        
        
        while True:
            try:
                isFinish   = RetVal.GrapFailExit.value
                
                #---------------
                if url_main_last == url_cur:
                   url_main_same_count += 1
                   if url_main_same_count > url_main_same_limit:
                       isFinish   = RetVal.GrapFailExit.value
                       break
                else:
                    url_main_same_count = 0
                    url_main_last = url_cur

                #----------------
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : begin to open url={}".format(url_cur))
                
                browser, page = await self.openUrl(url_cur,self.lauchOption,self.lauchKwargsList,self.viewPortWnd )
            
                if page is None:

                    isFinish = RetVal.GrapFailExit.value
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : open url={} fail,exit".format(url_cur),LogLevel.Fail)
                    break

                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : success to open url")
                
                #-------滚动之前添加操作
                ret = await self.dealMainScrollBefor(page,crawlerInfo)
                if ret != RetVal.Suc.value:
                    if ret == RetVal.SucExit.value:          #针对需要点一下的
                        isFinish = RetVal.GrapSuc.value
                        break
                    elif ret == RetVal.FailExit.value:
                        isFinish = RetVal.GrapFailExit.value
                        break
                    else:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() :dealMainScrollBefor fail,ignore  ",LogLevel.Fail)
                    
                
                #-------login 
                if is_first:
                    #login 
                    ret = await self.login(page)
                    if ret != RetVal.Suc.value:
                        loginFailCount += 1
                        if loginFailCount > 3:
                            isFinish = RetVal.GrapFailExit.value
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : login fail,exit",LogLevel.Fail)
                            break
                        else:
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : login fail,repeat count={}".format(loginFailCount),LogLevel.Fail)
                            await self.closeBrowser()
                            continue
                    
                    #search
                    ret,newPage = await  self.searchWord(page,compoundword)
                    if ret != RetVal.Suc.value:
                        searchFailCount += 1
                        if searchFailCount > 3:
                            isFinish = RetVal.GrapFailExit.value
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->searchWord() : search fail,exit",LogLevel.Fail)
                            break
                        else:
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->mainCrawler() : search fail,repeat count={}".format(searchFailCount),LogLevel.Fail)
                            await self.closeBrowser()
                            continue
                    #-------
                    if newPage is not None:
                        page = newPage

                    loginFailCount  = 0
                    searchFailCount = 0
                
                #---------wait load
                ret = await self.waitforPageLoad(page)
                if ret != RetVal.Suc.value:
                    waitPageFailCount += 1

                    if waitPageFailCount > 3:
                        isFinish = RetVal.GrapFailExit.value
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->waitforPageLoad() : waitforPage fail,exit",LogLevel.Fail)
                        break
                    else:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->waitforPageLoad() : waitforPage fail,repeat count={}".format(waitPageFailCount),LogLevel.Fail)
                        await self.closeBrowser()
                        continue
                    
                waitPageFailCount = 0  

                #---------scroll
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : begin to scroll")
                
                ret1 = await self.autoScrollAsPage(page,crawlerInfo)

                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : end to scroll") 

                #----------check first page
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : CheckFirstPage begin")
                
                if is_first  and self.isCheckFirstPage:
                    ret,newurl = await self.checkFirstPage(page)
                    if ret == RetVal.FailRepeat.value:
                        url     = newurl
                        url_cur = newurl
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : is not first page,open new first url={}".format(url_cur),LogLevel.Fail)
                        continue
                    elif ret == RetVal.FailExit.value:
                        isFinish = RetVal.GrapFailExit.value
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : checkFirstPage fail,exit ",LogLevel.Fail)
                        break
                    elif ret > RetVal.FailRepeat.value: #找不到首页，不重试
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : checkFirstPage fail,continue ",LogLevel.Fail)
                        await self.closeBrowser()
                        continue
                    

                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : CheckFirstPage end")

                #-----------other
                ret = await self.dealMainOther(page,crawlerInfo)
                if ret != RetVal.Suc.value:
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : dealMainOther() fail",LogLevel.Fail)
                    
                is_first = False
                #------------------------------------------------------------------------------------------
                #------------------------------------------------------------------------------------------
                # sub page
                curCount = 0
                ret1     = 0
                msg      = ""

                while True:
                    isFinish   = RetVal.GrapSucRepeat.value
                    curCount  += 1
                    url_next   = ""
                    
                    #---------------
                    
                    if url_sub_last == url_cur:
                        url_sub_same_count += 1
                        if url_sub_same_count > url_sub_same_limit:
                            isFinish   = RetVal.GrapFailExit.value
                            break
                    else:
                        url_sub_same_count = 0
                        url_sub_last = url_cur
                    
                    #-----scrool
                    if curCount > 1:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop={} : begin to scroll".format(curCount))
                        
                        ret1 = await self.autoScrollAsPage(page,crawlerInfo)
                        if ret1  != RetVal.Suc.value:
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop{} : scroll fail".format(curCount),LogLevel.Fail)
                            if ret1 !=  RetVal.Fail.value:
                                isFinish = self.dealCrawlerFail(ret1)   
                                break

                    #------deal subother
                    #self.printLogInfo("CrawlerSiteScrollBase->mainCrawler() : dealSubOther begin")

                    ret1 = await self.dealSubOther(page)
                    if ret1  != RetVal.Suc.value:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop{} : dealSubOther fail".format(curCount),LogLevel.Fail)
                        if ret1 !=  RetVal.Fail.value:
                            isFinish = self.dealCrawlerFail(ret1)   
                            break
                    

                    #self.printLogInfo("CrawlerSiteScrollBase->mainCrawler() : dealSubOther end")

                    #---------deal crawler 
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : dealSubCrawlerPage begin")

                    crawlerInfo.p_prePageItemNo = crawlerInfo.p_curPageItemNo
                    crawlerInfo.url             = page.target.url
                    ret1  = await self.dealSubCrawlerPage(page,crawlerInfo,curCount)
                    if ret1 == RetVal.Suc.value:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop{} : dealSubCrawlerPage sucess".format(curCount))
                    
                    else:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop{} : dealSubCrawlerPage fail".format(curCount),LogLevel.Fail) 
                    
                        if ret1 !=  RetVal.Fail.value:
                            isFinish = self.dealCrawlerFail(ret1)   
                            break
                    
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : dealSubCrawlerPage end")   
                    
                    #---------------检查是否终止抓取
                    ret1 = self.getIsTerminateCrawler()
                    if ret1 :
                       isFinish =  RetVal.GrapExitNotFindKeyword.value
                       break
                    #---------------go to next page
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : dealSubGotoNextPage begin")

                    isFinish,url_next = await self.dealSubGotoNextPage(page,curCount,crawlerInfo.maxPages)

                    if isFinish != RetVal.GrapSucRepeat.value:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop{} : break current loop isFinish={}".format(curCount,isFinish),LogLevel.Fail)
                        break

                    url_cur = url_next

                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage() : dealSubGotoNextPage end")


                    #------------------wait page
                    self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop={} : call to waitforPageLoad()".format(curCount))

                    ret = await self.waitforPageLoad(page)
                    if ret != RetVal.Suc.value:
                        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->loop{} : go to next page->waitforPageLoad(),fail,break".format(curCount),LogLevel.Fail)
                        isFinish = RetVal.GrapFailRepeat.value
                        break

                #---内循环的while True结束:
                #-----------------------------------------------------------------
                # ----------------------------------------------------------------
                
                # --   
                if  isFinish == RetVal.GrapFailRepeat.value:
                    if  self.isFailNewPageAsCurUrl:
                        if len(url_next) > 5:
                            url_cur = url_next
                            await self.closeBrowser()
                            continue 
                        else:
                            isFinish = RetVal.GrapFailExit.value
                            self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->url is error,grap exit url={}".format(url_next),LogLevel.Fail)
                            break
                    else:
                        break
                else:
                    break    
            #-------------------------------
            #-- 异常处理    
            except  Exception as e:
                self.printExcepInfo("CrawlerSiteScrollBase->crawlerAsPage(): main Exception")
                self.printExcepInfo(e)
                self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage(): main Exception")
                self.printLogInfo(e)

                isFinish = RetVal.GrapFailExit.value
                break
        
        #-------------------------------
        #--外循环的while True结束:

        #------------------------------------------------------------------------------------------
        #--
        self.showIsFinishMsg(isFinish,True)

        if isFinish == RetVal.GrapSuc.value:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value

        self.printLogInfo("CrawlerSiteScrollBase->crawlerAsPage()->: exit")
        return ret
    #--------------------------------------------------------------------------------------
    # 等待队列完成
    def showIsFinishMsg(self,isFinish,isAsPage=True):
        
        funcName = "crawlerAsPage()"
        if not isAsPage:
            funcName = "crawlerAsVScroll()"

        self.printLogInfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #--抓取退出-->成功退出
        if  isFinish == RetVal.GrapSuc.value:
            self.printLogInfo("CrawlerSiteScrollBase->{}->: grap exit,as success".format(funcName))
        #--抓取退出-->失败退出
        elif isFinish == RetVal.GrapFailExit.value:
            self.printLogInfo("CrawlerSiteScrollBase->{}->: grap exit,as fail".format(funcName))
        #--抓取退出-->文本中没有找到关键字，停止抓取，直接退出
        elif isFinish == RetVal.GrapExitNotFindKeyword.value:
            self.printLogInfo("CrawlerSiteScrollBase->{}->: grap exit,as not find keyword".format(funcName))
        #--抓取退出-->文本中找到连载小说，停止抓取，直接退出
        elif isFinish == RetVal.GrapExitAsNovel.value: 
            self.printLogInfo("CrawlerSiteScrollBase->{}->: grap exit,as find novel".format(funcName))  
        #----
        elif isFinish == RetVal.GrapExitCountLimit.value:
            self.printLogInfo("CrawlerSiteScrollBase->{}->: grap exit,as grap count limit".format(funcName))

    #--------------------------------------------------------------------------------------
    # 等待队列完成
    # ret = 0: 成功完成
    # ret = 1: 超时失败  
    async def  waitSubQueueFinish(self,curQueue):

        count       = 0
        last_count  = 0
        delay       = 1

        while True:
            
            count = curQueue.qsize()
            if count == 0:
                break
            elif count >300:
                delay = 60
            elif count >50:
                delay = 30
            elif count > 10:
                delay = 10
            else:
                delay = 3
                
            await asyncio.sleep(delay)
        
        return RetVal.Suc.value
        
    #--------------------------------------------------------------------------------------
    #处理Crawler中，fail的返回值
    def   dealCrawlerFail(self,retVal):
        ret = RetVal.GrapFailRepeat.value
        
        #--抓取重试->失败
        if retVal == RetVal.FailRepeat.value:
            ret = RetVal.GrapFailRepeat.value
        #--退出抓取->失败
        elif retVal == RetVal.FailExit.value:
            ret = RetVal.GrapFailExit.value
        #--退出抓取->抓取内容中没有找到关键字
        elif retVal == RetVal.FailExitNotFindKeyword.value:
            ret = RetVal.GrapExitNotFindKeyword.value
        #--停止抓取->抓取内容判定为小说
        elif retVal == RetVal.FailExitAsNovel.value:
            ret = RetVal.GrapExitAsNovel.value
        #--抓取失败,
        elif retVal == RetVal.FailExitCountLimit.value:
                ret = RetVal.GrapExitCountLimit.value
        
        return ret
    
    #--------------------------------------------------------------------------------------
    # goto to next page
        
    async def  GetNextBtnPageUrl(self,page,strSelector):
        
        url  = ""
        count = 3
        while count > 0:
            count -= 1
            ret,url = await self.pyteerEx.getElementHref(page,strSelector)
        
            if ret == RetVal.Suc.value:
                break

        if len(url) < 5:
            self.printLogInfo("CrawlerSiteScrollBase->GetNextBtnPageUrl : get next button href fail",LogLevel.Fail)
            url = ""

        return url
    
    #--------------------------------------------------------------------------------------
    # 以滚动的方式加载页面时，判断是否需要滚动。当默认的处理不能满足需要时，派生类重写这个函数
    # return:
    #   isFinish   = 0：继续向下滚动
    #   isFinish   = 1: 完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中开始滚动
    #   isFinish   = 3: 抓取失败，退出     
    async def  dealGotoNextVScroll(self,page,crawlerInfo):
        ret  = crawlerInfo.finish_status
        return ret
        

    #--------------------------------------------------------------------------------------
    # goto to next page
    # return:
    #   isFinish   = 0：继续抓取子页的下一页
    #   isFinish   = 1: 子页完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开子页的下一页
    #   isFinish   = 3: 抓取失败，退出     
    async def  dealSubGotoNextPage(self,page,curGrapNum,maxPageNum):

        self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : enter ")
        
        isFinish    = RetVal.GrapSucRepeat.value
        url_next    = ""
        curPageNum  = await self.getCurPageVal(page)
        
        #---
        if curPageNum == 0: #exception
           isFinish = RetVal.GrapFailExit.value
           return  isFinish,url_next
        elif curPageNum >= maxPageNum and maxPageNum>0:
           isFinish = RetVal.GrapSuc.value
           return isFinish,url_next
        
        #-----
        selectorBtn = self.cssPageBtnDict["nextPageBtn"]  
        ret = await self.pyteerEx.findElement(page,selectorBtn)
        #find
        if ret == RetVal.Suc.value:
            self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : success to find next button element ")
            
            url_next = await self.pyteerEx.getElementHref(page,selectorBtn)
            
            ret  = await self.pyteerEx.clickNavigate(page,selectorBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
            if ret == RetVal.Suc.value:
                self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : success to goto next page ")
                isFinish   = RetVal.GrapSucRepeat.value
            else:
                isFinish   = RetVal.GrapFailRepeat.value #退出
        elif ret == RetVal.Fail.value:     #not find,finish
            isFinish = RetVal.GrapSuc.value
        else:              #异常->退出，并打开下一页page的url
            isFinish = RetVal.GrapFailRepeat.value   #退出

        self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : exit ") 

        return isFinish,url_next

    #--------------------------------------------------------------------------------------
    #deal open url fail
    async def  dealOpenUrlFail(self,failCount,isMain=True):
        
        self.printLogInfo("CrawlerSiteScrollBase->dealOpenUrlFail():open url fail count={} ".format(failCount),LogLevel.Fail)
        
        ret = 0
     
        if isMain:
            if failCount < 5:
                await asyncio.sleep(20)
            elif failCount < 10:
                await asyncio.sleep(30) 
            else:
                self.printLogInfo("CrawlerSiteScrollBase->dealOpenUrlFail():open url fail count={} ,and exit".format(failCount),LogLevel.Fail)
                ret = 1            
        else:
            if failCount < 5:
                 await asyncio.sleep(20)
            
            else:
                self.printLogInfo("CrawlerSiteScrollBase->dealOpenUrlFail():open url fail count={} ,and exit".format(failCount),LogLevel.Fail)
                ret = 1    

        return ret     
    
    #------------------------------------------------------------------
    #--open url
    async def  openUrl(self,url,launch_option,launch_kwargsList,browerViewPort):

        self.printLogInfo("CrawlerSiteScrollBase->openUrl() : enter")

        count   = 3
        ret     = 1

        curPage = None
        browser = None
        
        
        while count > 0:

            count -= 1

            try:
                self.printLogInfo("CrawlerSiteScrollBase->openUrl() : count={} url={}".format(count,url))
                #--条件判断
                launch_kwargs    = [launch_kwargsList[0],launch_kwargsList[1]][self.isUseAgent]
                
                browser,curPage  = await self.createBrowserPage(launch_option,launch_kwargs)
                
                if curPage is None:
                    continue
                
                if self.isUseAgent:
                    await   curPage.authenticate(self.agentPara)

                
                await curPage.setViewport(browerViewPort)
                
                await curPage.setUserAgent(
                                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
                
                url = self.convertUrl(url)
                rep  =   await curPage.goto(url)
                
                if rep is not None:
                    ret = await self.pyteerEx.forbidInfoJs(curPage)
                    if ret == RetVal.Suc.value:
                       break
                    else:
                       await self.closeBrowser()
                       continue
                else:
                    
                    await self.closeBrowser()
                    continue
                
            except PageError as e:
                await self.closeBrowser()
                self.printExcepInfo("CrawlerSiteScrollBase->openUrl() : exception=PageError url={}".format(url))
                self.printExcepInfo(e)
                continue
            except Exception as e:
                await self.closeBrowser()
                self.printExcepInfo("CrawlerSiteScrollBase->openUrl() : exception=Exception url={}".format(url))
                self.printExcepInfo(e)
                continue
            
        
        if ret != 0:
           curPage = None

        self.printLogInfo("CrawlerSiteScrollBase->openUrl() : leave")

        return browser,curPage
    
    #------------------------------------------------------------------
    #
    async def  createBrowserPage(self,launch_option,launch_kwargs):
        
        self.printLogInfo("CrawlerSiteScrollBase->createBrowserPage() : enter")

        isSet   = self.isAllwaysNewPage
        isCreateBrowser = True
        isCreatePage    = True
        browser = self.getBrowser()
        page    = self.g_page
        
        #
        if  browser is not None: 
            isCreateBrowser = False
        #
        if not self.isAllwaysNewPage:
            if  page is not None: 
                isCreatePage = False
        else:  #create new
            
            if  page is not None:
                self.closePage(page)
            
        #
        if isCreateBrowser:
            browser    = await launch(launch_option,args=launch_kwargs)
            if browser is not None:
                #await self.pyteerEx.closeBrower(browser)
                pass
            self.setBrowser(browser )
        
        #
        if isCreatePage:
            page    = await browser.newPage()
            self.g_page    = page
        

        self.printLogInfo("CrawlerSiteScrollBase->createBrowserPage() : exit")
        
        return browser, page

    #-------------------------------------------------------------------------------------------
    #获取主回复的pid
    def getMainPid(self,strMainPid,strSplit):
        
        strPid     = ""

        strlist = CommonTool.strSplit(strMainPid,strSplit)
        if len(strlist) > 1:
            strPid = strlist[1]
            strPid.strip()
            
        return strPid

    #-----------------------------------------------------------------------------------------
    #
    async def setReplysToQueue(self,replyInfoList,queueBuf):

        for item in replyInfoList:
            await queueBuf.put(item)
    #----------------------------------------------------------------------------------------
    #
    def printReplyInfo(self,replyInfo,crawlerInfo=None):
        
        if replyInfo == None:
            return
            
        self.printGrapInfo(" ")
        self.printGrapInfo(" ")
        self.printGrapInfo("replyInfo begin-----------------------------------------")
        
        self.printGrapInfo("taskDetailsId={}".format(replyInfo.serverTaskId))
        self.printGrapInfo("contentId={}".format(replyInfo.contentId))
        self.printGrapInfo("parentContentId={}".format(replyInfo.parentContentId))
        self.printGrapInfo("pageNo={}".format(replyInfo.pageNo))
        self.printGrapInfo("ranking={}".format(replyInfo.ranking))
        self.printGrapInfo("snapshot={}".format(replyInfo.snapshots))
        self.printGrapInfo("url={}".format(replyInfo.href))
        self.printGrapInfo("pageUrl={}".format(replyInfo.pageUrl))
        self.printGrapInfo("title={}".format(replyInfo.main_title))
        if crawlerInfo is not None:
            self.printGrapInfo("keyword={}".format(crawlerInfo.keyword))
            self.printGrapInfo("compoundword={}".format(crawlerInfo.compoundword))
        self.printGrapInfo("content={}".format(replyInfo.text))
        self.printGrapInfo("publisher={}".format(replyInfo.publisher))
        self.printGrapInfo("publishTime={}".format(replyInfo.publishTime))
        self.printGrapInfo("reads={}".format(replyInfo.reads))
        self.printGrapInfo("forwards={}".format(replyInfo.forwards))
        self.printGrapInfo("stars={}".format(replyInfo.stars))
        self.printGrapInfo("comments={}".format(replyInfo.comments))
        self.printGrapInfo("hotWords={}".format(replyInfo.hotWords))
        self.printGrapInfo("locateSymbol={}".format(replyInfo.locateSymbol))
        self.printGrapInfo("pid={}".format(replyInfo.pid))
        self.printGrapInfo("sid={}".format(replyInfo.sid))
        self.printGrapInfo(" ")
        self.printGrapInfo("replyInfo end-----------------------------------------")
    
    #----------------------------------------------------------------------------------------
    #
    def printReplyInfoBuf(self,replyInfoBuf,crawlerInfo=None):
        
        for replyInfo in replyInfoBuf:
            self.printGrapInfo(" ")
            self.printGrapInfo(" ")
            self.printGrapInfo("replyInfo begin-----------------------------------------")
            
            self.printGrapInfo("taskDetailsId={}".format(replyInfo.serverTaskId))
            self.printGrapInfo("contentId={}".format(replyInfo.contentId))
            self.printGrapInfo("parentContentId={}".format(replyInfo.parentContentId))
            self.printGrapInfo("pageNo={}".format(replyInfo.pageNo))
            self.printGrapInfo("ranking={}".format(replyInfo.ranking))
            self.printGrapInfo("snapshot={}".format(replyInfo.snapshots))
            self.printGrapInfo("url={}".format(replyInfo.href))
            self.printGrapInfo("pageUrl={}".format(replyInfo.pageUrl))
            self.printGrapInfo("title={}".format(replyInfo.main_title))
            if crawlerInfo is not None:
                self.printGrapInfo("keyword={}".format(crawlerInfo.keyword))
                self.printGrapInfo("compoundword={}".format(crawlerInfo.compoundword))    
            self.printGrapInfo("content={}".format(replyInfo.text))
            self.printGrapInfo("publisher={}".format(replyInfo.publisher))
            self.printGrapInfo("publishTime={}".format(replyInfo.publishTime))
            self.printGrapInfo("reads={}".format(replyInfo.reads))
            self.printGrapInfo("forwards={}".format(replyInfo.forwards))
            self.printGrapInfo("stars={}".format(replyInfo.stars))
            self.printGrapInfo("comments={}".format(replyInfo.comments))
            self.printGrapInfo("hotWords={}".format(replyInfo.hotWords))
            self.printGrapInfo("locateSymbol={}".format(replyInfo.locateSymbol))
            self.printGrapInfo("pid={}".format(replyInfo.pid))
            self.printGrapInfo("sid={}".format(replyInfo.sid))
            self.printGrapInfo(" ")
            self.printGrapInfo("replyInfo end-----------------------------------------")

    #-----------------------------------------------------------------------------------------
    #获取当前page号
    async def getMainCurPageVal(self,page,selecotor):
        
        nPage = 0
        
        ret,curPage  = await self.pyteerEx.getElementContext(page,selecotor)
        if ret == RetVal.Suc.value:
            nPage  = CommonTool.strToInt(curPage.strip() )
        elif ret == RetVal.Fail.value:
            nPage = 1
        
        return nPage

    #-----------------------------------------------------------------------------------------
    #获取当前page号
    async def getCurPageVal(self,page):

        nPage = 0
        selector = self.cssPageBtnDict["curPageText"]

        ret,curPage  = await self.pyteerEx.getElementContext(page,selector)
        if ret == RetVal.Suc.value:
            nPage  = CommonTool.strToInt(curPage.strip() )
        elif ret == RetVal.Fail.value:
            nPage = 1
        
        return nPage

    #-----------------------------------------------------------------------------------------
    # 滚动页面
    async def autoScrollAsVScroll(self,page,crawlerInfo):
        return await self.autoVScrollByScroll(page,crawlerInfo,self.autoScrollStep)

    #-----------------------------------------------------------------------------------------
    #滚动页面---以点击元素的方式
    async def autoVScrollByClick(self,page,crawlerInfo,step):
        
        finish_status = RetVal.GrapSucRepeat.value
        ret        = RetVal.Suc.value
        selector   = self.cssAutoScrollClk["clkButton"]
        maxCount   = self.autoScrollCount 
        nDealy     = self.autoScrollOnceDelay
        clickDelay =  self.cssAutoScrollClk["clickDelay"]                       
        hoverDelay =  self.cssAutoScrollClk["hoverDelay"]       
        curCount   = 0
        
        self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByClick() : enter")

        while curCount < maxCount:
    
            ret1 = await self.pyteerEx.clickHoverElement(page,selector,clickDelay,hoverDelay)
            if ret1 != RetVal.Suc.value:
                if ret1 == RetVal.Fail.value: #找不到
                    ret = RetVal.Suc.value
                    finish_status = RetVal.GrapSuc.value
                    break
                else:
                    ret = RetVal.FailExit.value
                    finish_status = RetVal.GrapFailExit.value
                    break 
            
            #-------
            curCount += 1
        #----------
        crawlerInfo.finish_status = finish_status
        
        self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByClick() : exit")

        return ret

    #-----------------------------------------------------------------------------------------
    #滚动页面---以滚动条的方式,要判断滚动是否结束
    #---返回值:
    #   isFinish   = 0：继续抓取子页的下一页
    #   isFinish   = 1: 整个子页完成抓取  
    #   isFinish   = 2: 退出子循环，在新的browser中打开当前子页的下一页
    #   isFinish   = 3: 抓取失败，退出
    async def autoVScrollByScroll(self,page,crawlerInfo,step):
        
        self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() : enter")
        
        ret           = RetVal.Suc.value
        maxCount      = self.autoScrollCount 
        nDealy        = self.autoScrollOnceDelay
        curCount      = 0
        lastCurPos    = 0
        nSameCount    = 0
        finish_status = RetVal.GrapSucRepeat.value

        ret1,lastCurPos = await self.pyteerEx.getScrollCurPos(page)
        
        while curCount < maxCount:
            
            self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() : curCount={},maxCount={}".format(curCount,maxCount))
            ret1 = await self.pyteerEx.autoScrollCur(page,step)
            if ret1 != RetVal.Suc.value:
                ret           = RetVal.FailExit.value
                finish_status = RetVal.GrapFailExit.value
                self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() :scrollAutoCur fail,  curCount={},maxCount={}".format(curCount,maxCount))
                break
            
            #-------
            await asyncio.sleep(nDealy)
            ret1,curPos = await self.pyteerEx.getScrollCurPos(page)
            self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() :scrollAutoCur end curCount={},curPos={},lastCurPos={}".format(curCount,curPos,lastCurPos))
            if ret1 == RetVal.Suc.value:
                self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() :getScrollIsBottom ,  curCount={},maxCount={}".format(curCount,maxCount))
                if curPos == lastCurPos and curPos > 0:
                    self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() :getScrollIsBottom suc ,  curCount={},maxCount={},curPos={},lastCurPos={}".format(curCount,maxCount,curPos,lastCurPos))
                    ret           = RetVal.Suc.value
                    finish_status = RetVal.GrapSuc.value
                    break
                
            elif ret1 == RetVal.ExceptPyppeteer.value:
                ret = RetVal.FailExit.value
                finish_status = RetVal.GrapFailExit.value
                self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() :getScrollIsBottom exception,  curCount={},maxCount={}".format(curCount,maxCount))
                break

            #-------
            curCount   += 1
            lastCurPos = curPos
        
        self.printLogInfo("CrawlerSiteScrollBase->autoVScrollByScroll() : exit")
        crawlerInfo.finish_status = finish_status

        return ret

    #-----------------------------------------------------------------------------------------
    # 当以滚动的方式加载页面时，生成动态的css值,用于抓取剩余的项
    def makeDynamicCss(self,cssVal,count):
        strVal = "{}:nth-child(n+{}) ".format(cssVal,count)
        #strVal = "{}:nth-of-type(n+{}) ".format(cssVal,count)
        return strVal

    #----------------------------------------------------------------------------------------
    #--检查文本是否包含关键字
    def checkTextIncludeKeyword(self,checkText,keyword):

        ret = RetVal.Fail.value
        keyword      = keyword.upper()
        checkText    = checkText.upper()
        if (len(checkText) >0) and (len(keyword) > 0):

            if checkText.find(keyword) != -1:
                ret = RetVal.Suc.value
        
        return ret
    
    #----------------------------------------------------------------------------------------
    #--检查标题是否包含关键字
    def checkTitleIncludeKeyword(self,crawlerInfo):

        ret = RetVal.Fail.value
        keyword  = crawlerInfo.keyword
        title    = crawlerInfo.main_title
        
        keyword  = keyword.upper()
        title    = title.upper()

        if title.find(keyword) != -1:
            ret = RetVal.Suc.value
        
        return ret
    #--------------------------------------------------------------------------------------
    #--检查正文是否包含关键字
    def checkContextIncludeKeyword(self,crawlerInfo,replyBuf):

        isFind   = RetVal.Fail.value
        keyword  = crawlerInfo.keyword
        
        keyword  = keyword.upper()

        for item in replyBuf:
            curText = item.text
            curText = curText.upper()
            if curText.find(keyword) != -1:
                isFind = RetVal.Suc.value
                break
        
                
        return isFind

    #--------------------------------------------------------------------------------------
    #检查是否包含keyword
    def  checkIncludeKeyword(self,crawlerInfo,replyBuf):

        isFind   = RetVal.Fail.value
        keyword  = crawlerInfo.keyword
        title    = crawlerInfo.main_title
        keyword  = keyword.upper()
        title    = title.upper()

        #--check title
        if title.find(keyword) != -1:
            isFind = RetVal.Suc.value
        else:
            #--check text
            for item in replyBuf:
                curText = item.text
                if curText.find(keyword) != -1:
                    isFind = RetVal.Suc.value
                    break
                
        return isFind
    #--------------------------------------------------------------------------------------
    #检查传入的title和content字符串是否包含keyword
    def checkStrIncludeKeyword(self,title,content,keyword):

        isFind = RetVal.Fail.value
        if len(keyword) == 0:
            return isFind

        keyword  = keyword.upper()
        title    = title.upper()
        content  = content.upper()
        #--check title
        if title.find(keyword) != -1:
            isFind = RetVal.Suc.value
        else:
            #--check text
            if content.find(keyword) != -1:
                isFind = RetVal.Suc.value
                        
        return isFind
    #--------------------------------------------------------------------------------------
    #---当抓取数据时，检查是否终止抓取
    #---return:  
    #         =  RetVal.FailExitAsNovel.value :终止抓取
    #         =  RetVal.Suc.value:            抓取继续
    def IsTerminateGrapAsNovel(self,crawlerInfo,strContent):

        ret = RetVal.Suc.value
        novelInfo = crawlerInfo.novelInfo

        if novelInfo is not None:
            ret = novelInfo.checkIsTerminate(strContent)
        
        return ret
    
    #--------------------------------------------------------------------------------------
    #---获取pageUrl的地址->1>先去除地址中？之后的字符;2>然后去除#之后的字符
    #                 
    #---return:  
    #         =pageUrl
    def getPageUrl(self,strUrl):
        
        strUrl  = strUrl.strip()
        pageUrl = ""
        
        if len(strUrl) > 0:
            pageUrl = CommonTool.strSplitIndex(strUrl,"?",0)
            if len(pageUrl) > 0:
                pageUrl = CommonTool.strSplitIndex(pageUrl,"#",0)
        if len(pageUrl) < 1:
            pageUrl = strUrl

        return pageUrl

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
class   CrawlerSiteScrollMain(CrawlerSiteScrollBase):
    def __init__(self,crawlerType,queueDict,browerDict):
        super().__init__(crawlerType,queueDict,browerDict )
        #--是否检查当前网址是首页
        self.isCheckFirstPage          = False
        #--当主时，是否上传数据
        self.isCommitData              = False
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerPage(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerSiteScrollMain->dealSubCrawlerPage() : enter")

        ret,grapInfoBuf = await self.dealSubCrawlerAsItem(page,crawlerInfo,index)
        if ret == RetVal.Suc.value:
            ret1 = await self.dealSubCrawlerResult(page,crawlerInfo,index,grapInfoBuf )
        
        self.printLogInfo("CrawlerSiteScrollMain->dealSubCrawlerPage() : enter")

        return  ret
    

    #--------------------------------------------------------------------------------------
    #crawler a web page
    async def  dealSubCrawlerResult(self,page,crawlerInfo,index,grapInfoBuf):
        
        self.printLogInfo("CrawlerSiteScrollMain->dealSubCrawlerResult() : enter")
        
        isSubCrawler = 0
        ret = RetVal.Suc.value

        if self.isCommitData:
            if len(grapInfoBuf) > 0:
                crawlerInfo.grap_buf.extend(grapInfoBuf)
                return RetVal.Suc.value
        
        #-----进入页面
        if (crawlerInfo.collect == GrapCollectEm.GetPageNot) and (crawlerInfo.analogClick == 0):
            isSubCrawler = 0        
        else:
            isSubCrawler = 1 

        #-----进入子页面抓取
        if isSubCrawler == 1:
            for item in grapInfoBuf:
                await self.topSubItemQueue.put(item )
        #-----直接上传数据
        else:
            replyInfoBuf = []
            for item in grapInfoBuf:
        #-----直接上传数据
                 replyInfo = GrapReplyInfo()
                 replyInfo.copyAsGrapTopItemInfo(item)
                 replyInfoBuf.append(replyInfo)

            #---------
            if len(replyInfoBuf) >0 :
                #ret1 = self.checkIncludeKeyword(crawlerInfo,replyInfoBuf)
                #if ret1 == RetVal.Suc.value:
                crawlerInfo.grap_buf.extend(replyInfoBuf)

        self.printLogInfo("CrawlerSiteScrollMain->dealSubCrawlerResult() : exit")

        return  ret

    #--------------------------------------------------------------------------------------
    #
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        return RetVal.Suc.value,[]
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
class   CrawlerSiteScrollSub(CrawlerSiteScrollBase):
    def __init__(self,crawlerType,queueDict,browerDict):
        super().__init__(crawlerType,queueDict,browerDict )
        
        #--是否检查当前网址是首页
        self.isCheckFirstPage          = True

    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerPage(self,page,crawlerInfo,index):
  
        self.printLogInfo("CrawlerSiteScrollSub->dealSubCrawlerPage() : enter")

        ret  = RetVal.Suc.value
        replyInfoBuf = []
        #关键字抓取
        if self.crawlerType == GrapTypeEm.Compoundword:
            
            if  crawlerInfo.collect ==  GrapCollectEm.GetPageFloor.value:

                ret,replyInfoBuf = await self.dealSubCrawlerAsFloor(page,crawlerInfo,index)

            elif crawlerInfo.collect ==  GrapCollectEm.GetPageText.value:

                ret,replyInfoBuf = await self.dealSubCrawlerAsHtml(page,crawlerInfo,index)

            elif crawlerInfo.collect ==  GrapCollectEm.GetPageHtml.value:

                ret,replyInfoBuf = await self.dealSubCrawlerAsText(page,crawlerInfo,index)

            elif crawlerInfo.collect ==  GrapCollectEm.GetPageNot.value:
                ret,replyInfoBuf = await self.dealSubCrawlerAsNothing(page,crawlerInfo,index)

        #指定网址抓取
        elif  self.crawlerType == GrapTypeEm.Url:

            ret,replyInfoBuf = await self.dealSubCrawlerAsDefUrl(page,crawlerInfo,index)   
        
        self.printLogInfo("CrawlerSiteScrollSub->dealSubCrawlerPage() :replyInfoBuf->len={} ".format(len(replyInfoBuf)))
        #--------------------------------------------
        if len(replyInfoBuf) > 0:
            crawlerInfo.grap_buf.extend(replyInfoBuf)
            self.printLogInfo("CrawlerSiteScrollSub->dealSubCrawlerPage() :crawlerInfo.grap_buf len={} ".format(len(replyInfoBuf)))
            """
            ret1 = self.checkIncludeKeyword(crawlerInfo,replyInfoBuf)
            if ret1 == RetVal.Suc.value:
                self.printLogInfo("CrawlerSiteScrollSub->dealSubCrawlerPage() : ----find  data keyword in replybuf")

                crawlerInfo.grap_buf.extend(replyInfoBuf)
                self.printGrapInfo("keyword@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@{}".format(len(crawlerInfo.grap_buf)))
                #self.printReplyInfoBuf(crawlerInfo.grap_buf)
                self.printGrapInfo("keyword@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            """    
        self.printLogInfo("CrawlerSiteScrollSub->dealSubCrawlerPage() : exit")

        return ret   

   