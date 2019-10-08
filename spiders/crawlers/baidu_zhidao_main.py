#-----baidu_zhidao_main.py
#---百度知道
import asyncio
import sys
import logging
import random
import time
from pyppeteer import launch
import sys,os
sys.path.append("..")

from  struct_def                import *
from crawlers.search_base_sites import *
from crawlers.baidu_zhidao_sub  import *
from pyteerex.pyppeteer_ex      import *
from  log.logger                import Logger
from crawlers.common_data       import *
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerZhidao(CrawlerBase ):
    #------------------------------------------------------------------------------------------
    #
    def __init__(self,num):
       super().__init__(num )

    #------------------------------------------------------------------------------------------
    #  
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:
            
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:

            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )
    
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):
        
        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerZhidaoMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerZhidaoSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.Page.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):
        
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerZhidaoSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.Page.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):
        pass


#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerZhidaoMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)

        #-----------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        
        
        #------------------------------------------------
        
        self.cssPageBtnDict = {
                               'tailPageText':"div.container>div.search-box.line>form.search-form",
                               'prePageBtn':"",
                               'curPageText':"div.page-main-inner > div.line > div.list-wraper>div.list-inner>div.widget-pager.clearfix >div.pager > b",
                               'curPageBtn':"div.page-main-inner > div.line > div.list-wraper>div.list-inner>div.widget-pager.clearfix >div.pager > b",
                               'nextPageBtn':"div.page-main-inner > div.line > div.list-wraper>div.list-inner>div.widget-pager.clearfix >div.pager > a.pager-next",
                               'bottomAllPageNum':" "
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox': "div.search-block.clearfix > div.search-cont.clearfix > form.search-form > input.hdi",
                                  'clkButton':"div.search-block.clearfix > div.search-cont.clearfix > form.search-form > button.btn-global",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load"]
                                 }
        #
        self.cssLoginDict      = {
                                 'menuLogin':"div.userbar >ul>li.u_login>div.u_menu_item>a[real='noreferrer'] ",
                                 'typeLogin':"div.pass-login-pop-content>div.pass-login-pop-form>div.tang-pass-footerBar>p.tang-pass-footerBarULogin.pass-link",
                                 'nameLogin':"div.pass-login-pop-content>div.pass-login-pop-form>div.tang-pass-footerBar>p[style='display: block;' ",
                                 'user_name':"div.pass-login-pop-form>div.tang-pass-login>form.pass-form.pass-form-normal>p.pass-form-item.pass-form-item-userName>input[name='userName']",
                                 'password' :"div.pass-login-pop-form>div.tang-pass-login>form.pass-form.pass-form-normal>p.pass-form-item.pass-form-item-password>input[name='password']",
                                 'clk_button':"div.pass-login-pop-form>div.tang-pass-login>form.pass-form.pass-form-normal>p.pass-form-item.pass-form-item-submit>input.pass-button.pass-button-submit",
                                 
                                 'user_name':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-userName >input.pass-text-input.pass-text-input-userName",
                                 'password' :"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-password >input.pass-text-input.pass-text-input-password",
                                 'clk_button':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-submit >input.pass-button.pass-button-submit",
                                  }

        #main href text
        self.cssMainItemHrefText = {
                                    'main':"div.line > div.list-wraper > div.list-inner > div.list > dl.dl",
                                    'sub' :"dt.dt.mb-4.line > a.ti"
                                   }

        #log
        self.log_inits("zhidao/main",1,1,logging.INFO)

    #-------------------------------------------------------------------------------------
    
    
    #--------------------------------------------------------------------------------------  
    async def dealMainScrollBefor(self,page,crawlerInfo):
        """
        title_link = "https://zhidao.baidu.com/question/141629464313063085.html?fr=iks&word=p30&ie=gbk"
        title_str  = " "

        grapItem = GrapTopItemInfo(title_link,"",title_str, )
        await self.topSubItemQueue.put(grapItem )
        
        await asyncio.sleep(60*30)
        """
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #
    async def  waitforPageLoad(self,page):
        return await self.pyteerEx.waitPage(page,self.cssPageBtnDict["tailPageText"],4)
    #--------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        return await self.searchWordBase(page,compoundword)
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerZhidaoMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []
        strUrl     = crawlerInfo.url
        strCompoundword = crawlerInfo.compoundword
        strKeyword      = crawlerInfo.keyword
        
        selector   = self.cssPageBtnDict["curPageText"]
        nPage      = await self.getMainCurPageVal(page,selector)



        cssMain = self.cssMainItemHrefText["main"]
        cssSub  = self.cssMainItemHrefText["sub"]
        elements = await page.querySelectorAll(cssMain)
        
        itemNo = 0
        for item in elements:
            itemNo += 1
            ret           = 1
            title_str     = ""
            title_link    = ""
            
            itemSub       = await item.querySelector(cssSub)

            if itemSub is not None:
                ret,title_str  = await self.pyteerEx.getPropertyJs(itemSub,'textContent')
                ret,title_link = await self.pyteerEx.getPropertyJs(itemSub,'href')
                self.log_grap.show(title_str)
                self.log_grap.show(title_link)
            
            if len(title_link.strip()) > 0:
               grapItem = GrapTopItemInfo(title_link,strKeyword,strCompoundword)
               grapItem.main_title   = ""
               grapItem.main_url     = strUrl
               grapItem.serverTaskId = crawlerInfo.serverTaskId
               grapItem.pageNo       = nPage
               grapItem.itemNo       = itemNo
               
               grapTopBuf.append(grapItem)
               
        
        self.printLogInfo("CrawlerZhidaoMain->dealSubCrawlerAsItem() : exit")
        
        return RetVal.Suc.value,grapTopBuf

