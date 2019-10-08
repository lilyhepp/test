#------------------tianya_main.py
#--天涯论坛--主抓取
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
from crawlers.tianya_sub        import *
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
class CrawlerTianya(CrawlerBase):
    def __init__(self,num):
        super().__init__(num)

    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerTianya->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerTianya->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerTianya->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerTianya->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerTianya->crawlerScroll() :leave")

    #------------------------------------------------------------------------------------
    #---Compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerTianya->crawlerDefCompoundword():enter ")

        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        #----main
        objMain = CrawlerTianyaMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        #----sub
        for i in range(1,subColNum):
            objSub  = CrawlerTianyaSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.Page.value,colTastList)

        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerTianya->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("Tianya->crawlerDefUrl():enter ")
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerTianyaSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.Page.value,colTastList)

        #-----add loop
        self.allColTastToLoop(loop,colTastList)
        
        print("CrawlerTianya->crawlerDefUrl():enter ")
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerTianyaMain(CrawlerSiteScrollMain):
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
                               'prePageBtn':"#main > div.long-pages > a:nth-child(2)",
                               'curPageText':"#main > div.long-pages > strong",
                               'nextPageBtn':"#main > div.long-pages > a:nth-child(10)",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  
                                  'inputBox':  "#searchIndex > form > div > input.searchText",
                                  'clkButton':  "#searchIndex > form > div > input.sousuo",

                                  'noSearchResultTag':"#search_msg+li",# 没有搜索到内容的标签

                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }
        
        #main href text
        self.cssMainItemHrefText = {
                                    'main':"div.s_main > div.s_post_list > div.s_post > span.p_title > a.bluelink ",
                                    
                                    #热门更多
                                    'main_more_href':"div.m-wrap>div.m-con-l>div>div.card-wrap>div.card-top>a.more",
                                    'main_sub':      "#main > div.searchListOne > ul > li h3 a",
                                    
                                   }

        #log
        self.log_inits("tianya/main",2,2,logging.INFO)

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
        #return await self.pyteerEx.waitPage(page,self.cssPageBtnDict["tailPageText"],4)
        self.printLogInfo("CrawlerTiebaMain->waitforPageLoad() : enter")
        
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #
    async def dealMainScrollBefor(self,page,crawlerInfo):

        self.printLogInfo("CrawlerTianyaMain->dealMainScrollBefor() : enter")

        cssList  = []
        selector = self.cssSearchDict["inputBox"]
        cssList.append(selector)       
        ret = await self.pyteerEx.waitPageAll(page,cssList,10)
        if ret == RetVal.Suc.value:
        # 为了处理浏览器重新打开到指定页面时，还是显示搜索不到内容的情况
            loop = 3
            isFirstPage = "&pn=" not in page.url
            selector = self.cssSearchDict["noSearchResultTag"]
            while True:
                ret = await self.pyteerEx.findElement(page,selector)# 查找是否出现没有搜索结果的页面

                if ret == RetVal.Suc.value:# 页面返回没有搜索结果
                    if loop == 0: # 三次刷新结束
                        if isFirstPage == 'False':# 不是首页就当成失败
                            ret = RetVal.Fail.value
                        break
                    else:
                        loop = loop-1
                        await self.pyteerEx.refreshPage(page)
                        await asyncio.sleep(1)    
                else:# 页面返回正常
                    ret = RetVal.Suc.value
                    break
        else:#异常，则直接退出
            ret = RetVal.FailExit.value
            self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : call waitPageAll() fail,and terminate crawler")

        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : exit")
        return ret
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page 
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerTianyaMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []
        #--current page
        nPageNo = await self.getCurPageVal(page)
        crawlerInfo.curPageNo = nPageNo
        
        
        #--other
        self.printLogInfo("CrawlerTianyaMain->dealSubCrawlerAsItem() : crawler other begin page={}".format(nPageNo))

        selector = self.cssMainItemHrefText["main_sub"]
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
               

        self.printLogInfo("CrawlerTianyaMain->dealSubCrawlerAsItem() : crawler other end page={}".format(nPageNo))    
        
        
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
    #   isFinish   = 0：继续抓取下一页
    #   isFinish   = 1: 完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开下一页
    #   isFinish   = 3: 抓取失败，退出     
    async def  dealSubGotoNextPage(self,page,curGrapNum,maxPageNum):

        self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : enter ")
        
        isFinish    = RetVal.GrapSucRepeat.value
        curPageNum  = await self.getCurPageVal(page)
        url_next    = "http://search.tianya.cn/bbs?q=" +  str(parse.quote(self.compoundword_for_url_next)) + "&pn=" + str(curPageNum+1)
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
            
            ret  = await self.pyteerEx.clickNavigate(page,selectorBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])

            if ret == RetVal.Suc.value:
                loop = 3
                selector = self.cssSearchDict["noSearchResultTag"]
                while True:
                    ret = await self.pyteerEx.findElement(page,selector)# 查找是否出现没有搜索结果的页面

                    if ret == RetVal.Suc.value:# 页面返回没有搜索结果
                        if loop == 0: # 三次刷新结束
                            ret = RetVal.Fail.value
                            isFinish   = RetVal.GrapFailRepeat.value
                            break
                        else:
                            loop = loop-1
                            await self.pyteerEx.refreshPage(page)
                            await asyncio.sleep(1)    
                    else:# 页面返回正常
                        ret = RetVal.Suc.value
                        isFinish   = RetVal.GrapSucRepeat.value
                        break
                self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : success to goto next page ")
                #isFinish   = RetVal.GrapSucRepeat.value
            else:
                isFinish   = RetVal.GrapFailRepeat.value #退出
        elif ret == RetVal.Fail.value:     #not find,finish
            isFinish = RetVal.GrapSuc.value
        else:              #异常->退出，并打开下一页page的url
            isFinish = RetVal.GrapFailRepeat.value   #退出

        self.getLogInfo().show("CrawlerSiteScrollBase->dealSubGotoNextPage() : exit ") 

        return isFinish,url_next

    #--------------------------------------------------------------------------------------
    