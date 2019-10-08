#--------weixin_sogou_main.py
#--------搜狗微信主页抓取
import  sys,os
import  asyncio
from    pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  log.logger                 import  Logger
from  crawlers.common_data       import *
from  crawlers.weixin_sogou_sub         import *

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerWeixinSogou(CrawlerBase):

    def __init__(self,num):
       super().__init__(num)
       
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerWeixinSogou->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:
    
            print("CrawlerWeixinSogou->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerWeixinSogou->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerWeixinSogou->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerWeixinSogou->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerWeixinSogou->crawlerDefCompoundword():enter ")
        
        subColNum   = self.subCoroutineNum
        colTaskList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerWeixinSogouMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,
                                   GrapScrollEm.Page.value,colTaskList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerWeixinSogouSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,
                                   GrapScrollEm.VScroll.value,colTaskList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTaskList)

        print("CrawlerWeixinSogou->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerWeixinSogou->crawlerDefUrl():enter ")
        colTaskList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerWeixinSogouSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,
                                   GrapScrollEm.VScroll.value,colTaskList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTaskList)

        print("CrawlerWeixinSogou->crawlerDefUrl():enter ")
        
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class CrawlerWeixinSogouMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        self.isUseAgent                = True
       
        #-----------------------------------------------
        #--other
        self.cssPageBtnDict = {
                               'prePageBtn':"div.wrapper>div.main-left>div.news-box>div.p-fy>a.pev",
                               'curPageText':"div.wrapper>div.main-left>div.news-box>div.p-fy>span",
                               'curPageBtn':"",
                               'nextPageBtn':"div.wrapper>div.main-left>div.news-box>div.p-fy>a.np",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox':  "div.header-box>div.header>div.searchbox>form>div.querybox>div.qborder>div.qborder2>input.query",
                                  'clkButton':  "div.header-box>div.header>div.searchbox>form>div.querybox>input.swz",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }
       
        

        #main href text
        self.cssMainItems =     {
                                    'main_sub': "div.wrapper>div.main-left>div.news-box>ul.news-list>li>div.txt-box>h3>a",
                                    #
                                   }

        #log
        self.log_inits("WeixinSogou/main",1,1,logging.INFO)

    #----------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------
    #-----overrider func login      
    async def login(self,page):
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #-----search compoundword
    async def searchWord(self,page,compoundword):
        return await self.searchWordBase(page,compoundword)

    #--------------------------------------------------------------------------------------
    #----override func waitforPageLoad
    async def waitforPageLoad(self,page):      
        return RetVal.Suc.value
    
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page 
    async def dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeixinSogouMain->dealSubCrawlerAsItem() : enter")
        
        grabTopBuf = []
        #--current page
        nPageNo = await self.getCurPageVal(page)
        crawlerInfo.curPageNo = nPageNo
        
        #--other
        self.printLogInfo("CrawlerWeixinSogouMain->dealSubCrawlerAsFloor() : crawler other begin page={}".format(nPageNo))

        selector = self.cssMainItems["main_sub"]
        ret,elementList = await self.pyteerEx.getElementAll(page,selector)
        if ret != RetVal.Suc.value:
            return RetVal.FailExit.value,grabTopBuf 
        
        nItemNo = 0
        for item in elementList:
            ret,curText = await self.pyteerEx.getElementHref(item)
            curText     = CommonTool.strStripRet(curText)
            if curText:
               nItemNo += 1
               grapItem = GrapTopItemInfo(curText,crawlerInfo.keyword,crawlerInfo.compoundword)
               grapItem.main_title   = ""
               grapItem.main_url     = ""
               grapItem.serverTaskId = crawlerInfo.serverTaskId
               grapItem.pageNo       = nPageNo
               grapItem.itemNo       = nItemNo
               
               grabTopBuf.append(grapItem)
               

        self.printLogInfo("CrawlerWeixinSogouMain->dealSubCrawlerAsItem() : crawler other end page={}".format(nPageNo))    
        return RetVal.Suc.value,grabTopBuf
    
    #-----------------------------------------------------------------------------------------
    #-----获取当前page号
    async def getCurPageVal(self,page):

        nPage = 0
        selector = self.cssPageBtnDict["curPageText"]

        ret,curPage  = await self.pyteerEx.getElementContext(page,selector)
        
        if ret == RetVal.Suc.value:
            nPage  = CommonTool.getDigitFromString(curPage.strip())
        elif ret == RetVal.Fail.value:
            nPage = 1
        
        return nPage

