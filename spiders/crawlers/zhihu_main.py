#-------zhihu_main.py
#-------the main 
import  sys,os
import  asyncio
from    pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  log.logger                 import  Logger
from  crawlers.common_data       import *
from  crawlers.zhihu_sub        import *

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerZhihu(CrawlerBase):

    def __init__(self,num):
       super().__init__(num)
    
    #------------------------------------------------------------------------------------------
    #---------- the entrypoint of the CrawlerWukong Instance  
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerZhihu->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerZhihu->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerZhihu->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerZhihu->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerZhihu->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerZhihu->crawlerDefCompoundword():enter ")
        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerZhihuMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.VScroll.value,colTastList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerZhihuSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.VScroll.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)
        
        print("CrawlerZhihu->crawlerDefCompoundword():leave ")

        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerZhihu->crawlerDefUrl():enter ")
        
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerZhihuSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.VScroll.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerZhihu->crawlerDefUrl():exit ")

        
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#------知乎抓取首页类
class CrawlerZhihuMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        #--以滚动的方式加载页面时，指定调用autoScroll函数的次数
        self.autoScrollCount           = 2
        self.autoScrollOnceDelay       = 1
        #-----------------------------------------------
        #--other
        
        #--搜索按钮、点击搜索
        self.cssSearchDict     = {
                                  'inputBox': "div.SearchBar > div.SearchBar-toolWrapper >form >div>div.Popover>div.SearchBar-input>input",
                                  
                                  'clkButton': "div.SearchBar > div.SearchBar-toolWrapper >form >div>div.Popover>div.SearchBar-input>div.Input-after>button",
                                  
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }
        
        #main href text
        self.cssMainItemHrefText = {
                                    'main_sub':"div.SearchMain>div>div.ListShortcut>div.List>div>div.Card.SearchResult-Card",
                                    'main_sub_item':"div.List-item>div.ContentItem.AnswerItem>h2.ContentItem-title>div>a",
                                   }
        
        #--获取特定元素
        self.cssGetElement    =  {
                                   'loadMoreContent':"div.index-question-list >div.w-feed.search-all >div.w-feed-loadmore >span.w-feed-loadmore-w"
                                 }
        
        
        self.loadMoreContentText = "没有更多内容"
        
        #log
        self.log_inits("zhihu/main",2,2,logging.INFO)
    
    #--------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        self.printLogInfo("CrawlerZhihuMain->searchWord() : enter")
        return await self.searchWordBase(page,compoundword)

    #--------------------------------------------------------------------------------------
    #----waitforPageLoad 
    async def waitforPageLoad(self,page):
        self.printLogInfo("CrawlerZhihuMain->waitforPageLoad() : enter")
        return RetVal.Suc.value
    
    #--------------------------------------------------------------------------------------
    # generate url for subCrawler override 
    async def dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerZhihuMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []   
        crawlerInfo.curPageNo = 1
        
        
        selectorSub  = self.cssMainItemHrefText["main_sub_item"]
        selector     = self.cssMainItemHrefText["main_sub"]
        selector     = self.makeDynamicCss(selector,crawlerInfo.vscroll_grap_count)
        ret,elementList = await self.pyteerEx.getElementAll(page,selector)

        nGrapNo     = crawlerInfo.vscroll_grap_count
        nItemNo     = 0
        

        for item in elementList:
            
            ret,curText = await self.pyteerEx.getElementHref(item,selectorSub) 
            curText     = CommonTool.strStripRet(curText)
            nItemNo     += 1

            if curText:
               nGrapNo += 1
               grapItem = GrapTopItemInfo(curText,crawlerInfo.keyword,crawlerInfo.compoundword)
               grapItem.main_title   = ""
               grapItem.main_url     = ""
               grapItem.serverTaskId = crawlerInfo.serverTaskId
               grapItem.pageNo       = 1
               grapItem.itemNo       = nGrapNo
               
               #grapTopBuf.append(grapItem)
               self.printGrapInfo("CrawlerZhihuMain->dealSubCrawlerAsItem() :sub{} url={} ".format(nGrapNo,curText ))
               
        crawlerInfo.vscroll_grap_count += nItemNo
        
        self.printLogInfo("CrawlerZhihuMain->dealSubCrawlerAsItem() : leave curItemNo={} grap_count={}".format(nItemNo,crawlerInfo.vscroll_grap_count))    
        return RetVal.Suc.value,grapTopBuf
    
    #-------------------------------------------------------------------------------------------
    #---override func dealSubGotoNextPage 
    #---wukong platform has no Paging
    async def dealSubGotoNextPage(self,page,curGrapNum,maxPageNum):     
        return RetVal.GrapSuc.value,""
                