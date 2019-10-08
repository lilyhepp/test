#------------------so_wenda_main.py
#--360问答--主抓取
import sys,os
import asyncio

from urllib import parse

from pyppeteer import launch


sys.path.append("..")

from struct_def                 import *
from crawlers.search_base_sites import *
from pyteerex.pyppeteer_ex      import *
from log.logger                 import Logger
from crawlers.common_data       import *
from crawlers.so_wenda_sub        import *
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
class CrawlerSoWenda(CrawlerBase):
    def __init__(self,num):
        super().__init__(num)

    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerSoWenda->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerSoWenda->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerSoWenda->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerSoWenda->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerSoWenda->crawlerScroll() :leave")

    #------------------------------------------------------------------------------------
    #---Compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerSoWenda->crawlerDefCompoundword():enter ")

        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        #----main
        objMain = CrawlerSoWendaMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        #----sub
        for i in range(1,subColNum):
            objSub  = CrawlerSoWendaSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.Page.value,colTastList)

        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerSoWenda->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("SoWenda->crawlerDefUrl():enter ")
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerSoWendaSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.Page.value,colTastList)

        #-----add loop
        self.allColTastToLoop(loop,colTastList)
        
        print("CrawlerSoWenda->crawlerDefUrl():enter ")
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerSoWendaMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
       
        #-----------------------------------------------
        #--other
        self.cssPageBtnDict = {
                               'tailPageText':"",
                               'prePageBtn':"#qaresult-page .pages a.pre",
                               'curPageText':"#qaresult-page .pages b",
                               'nextPageBtn':"#qaresult-page .pages a.next",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  
                                  'inputBox':  "#js-sh-ipt",
                                  'clkButton':  ".s-btn.js-suggest-search-btn",

                                  'noSearchResultTag':"#noanswer",# 没有搜索到内容的标签

                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }
        
        #main href text
        self.cssMainItemHrefText = {
                                    'main':".item.js-normal-item .qa-i-hd a"                                                                     
                                   }

        #log
        self.log_inits("so_wenda/main",2,2,logging.INFO)

        self.compoundword_for_url_next = "" # 用于下一页url地址的拼接

    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------    


    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        self.compoundword_for_url_next = compoundword
        return await self.searchWordBase(page,compoundword)

    #--------------------------------------------------------------------------------------
    #
    async def  waitforPageLoad(self,page):
        self.printLogInfo("CrawlerSoWendaMain->waitforPageLoad() : enter")
        contentAreaTagCss = "#js-qa-list"
        ret = await self.pyteerEx.waitPage(page,contentAreaTagCss,4)#内容区域是否加载出来
        self.printLogInfo("CrawlerSoWendaMain->waitforPageLoad() : exit")
        return ret
    #--------------------------------------------------------------------------------------
    #
    async def dealMainScrollBefor(self,page,crawlerInfo):

        self.printLogInfo("CrawlerSoWendaMain->dealMainScrollBefor() : enter")

        self.printLogInfo("CrawlerSoWendaMain->dealMainScrollBefor() : exit")
        return RetVal.Suc.value
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page 
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerSoWendaMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []
        #--current page
        nPageNo = await self.getCurPageVal(page)
        crawlerInfo.curPageNo = nPageNo
        
        
        #--other
        self.printLogInfo("CrawlerSoWendaMain->dealSubCrawlerAsItem() : crawler other begin page={}".format(nPageNo))

        selector = self.cssMainItemHrefText["main"]
        ret,elementList = await self.pyteerEx.getElementAll(page,selector )
        nItemNo = 0
        for item in elementList:
            ret,curText = await self.pyteerEx.getElementHref(item)
            
            curText     = CommonTool.strStripRet(curText)
            if curText:
               nItemNo += 1
               grapItem = GrapTopItemInfo(curText,crawlerInfo.keyword,crawlerInfo.compoundword )
               grapItem.main_title   = ""
               grapItem.main_url     = ""
               grapItem.serverTaskId = crawlerInfo.serverTaskId
               grapItem.pageNo       = nPageNo
               grapItem.itemNo       = nItemNo
               
               grapTopBuf.append(grapItem)
               

        self.printLogInfo("CrawlerSoWendaMain->dealSubCrawlerAsItem() : crawler other end page={}".format(nPageNo))    
        
        
        return RetVal.Suc.value,grapTopBuf
    
    #-----------------------------------------------------------------------------------------
    #获取当前page号
    async def getCurPageVal(self,page):

        nPage = 0
        selector = self.cssPageBtnDict["curPageText"]

        ret,curPage  = await self.pyteerEx.getElementContext(page,selector)
        
        if ret == RetVal.Suc.value:
            nPage  = CommonTool.getDigitFromString(curPage.strip())
        elif ret == RetVal.Fail.value:
            nPage = 1
        
        return nPage
    #--------------------------------------------------------------------------------------
# goto to next page
    # return:
    #   isFinish   = 0：继续抓取子页的下一页
    #   isFinish   = 1: 子页完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开子页的下一页
    #   isFinish   = 3: 抓取失败，退出     
    async def  dealSubGotoNextPage(self,page,curGrapNum,maxPageNum):

        self.getLogInfo().show("CrawlerSoWendaMain->dealSubGotoNextPage() : enter ")
        
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
            self.getLogInfo().show("CrawlerSoWendaMain->dealSubGotoNextPage() : success to find next button element ")
            
            url_next = await self.pyteerEx.getElementHref(page,selectorBtn)

            if len(url_next) == 2:
                url_next = url_next[1]
            
            ret  = await self.pyteerEx.clickNavigate(page,selectorBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
            if ret == RetVal.Suc.value:
                self.getLogInfo().show("CrawlerSoWendaMain->dealSubGotoNextPage() : success to goto next page ")
                isFinish   = RetVal.GrapSucRepeat.value
            else:
                isFinish   = RetVal.GrapFailRepeat.value #退出
        elif ret == RetVal.Fail.value:     #not find,finish
            isFinish = RetVal.GrapSuc.value
        else:              #异常->退出，并打开下一页page的url
            isFinish = RetVal.GrapFailRepeat.value   #退出

        self.getLogInfo().show("CrawlerSoWendaMain->dealSubGotoNextPage() : exit ") 

        return isFinish,url_next

    #--------------------------------------------------------------------------------------
    