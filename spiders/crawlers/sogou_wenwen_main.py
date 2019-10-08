#--------sogou_wenwen_main.py
#--------搜狗问问主页抓取
import  sys,os
import  asyncio
from    pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  log.logger                 import  Logger
from  crawlers.common_data       import *
from  crawlers.sogou_wenwen_sub         import *

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerSogouWenWen(CrawlerBase):

    def __init__(self,num):
       super().__init__(num)
       
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerSogouWenWen->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:
    
            print("CrawlerSogouWenWen->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerSogouWenWen->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerSogouWenWen->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerSogouWenWen->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerSogouWenWen->crawlerDefCompoundword():enter ")
        
        subColNum   = self.subCoroutineNum
        colTaskList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerSogouWenWenMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,
                                   GrapScrollEm.Page.value,colTaskList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerSogouWenWenSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,
                                   GrapScrollEm.Page.value,colTaskList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTaskList)

        print("CrawlerSogouWenWen->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerSogouWenWen->crawlerDefUrl():enter ")
        colTaskList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerSogouWenWenSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,
                                   GrapScrollEm.Page.value,colTaskList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTaskList)

        print("CrawlerSogouWenWen->crawlerDefUrl():exit ")
        
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class CrawlerSogouWenWenMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
       
        #-----------------------------------------------
        #--other
        self.cssPageBtnDict = {
                               'prePageBtn':"#pagebar_container>a.pev",
                               'curPageText':"#pagebar_container>span",
                               'curPageBtn':"",
                               'nextPageBtn':"#pagebar_container>a.np",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox':  "div.searchbox>form.searchform>div.querybox>input.query",
                                  'clkButton':  "div.searchbox>form.searchform>div.sbtn1>input.search_bt",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }
       
        

        #main href text
        self.cssMainItems =     {
                                    'main_sub': "#main>div>div.results>div.vrwrap>h3.vrTitle>a",
                                    
                                   }

        #log
        self.log_inits("SogouWenWen/main",1,1,logging.INFO)

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
        
        self.printLogInfo("CrawlerSogouWenWenMain->dealSubCrawlerAsItem() : enter")
        
        grabTopBuf = []
        #--current page
        nPageNo = await self.getCurPageVal(page)
        crawlerInfo.curPageNo = nPageNo
        
        #--other
        self.printLogInfo("CrawlerSogouWenWenMain->dealSubCrawlerAsFloor() : crawler other begin page={}".format(nPageNo))

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
               

        self.printLogInfo("CrawlerSogouWenWenMain->dealSubCrawlerAsItem() : crawler other end page={}".format(nPageNo))    
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
