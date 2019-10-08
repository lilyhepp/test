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
from crawlers.sina_iask_sub     import *
from pyteerex.pyppeteer_ex      import *
from  log.logger                import Logger
from crawlers.common_data       import *
from urllib import parse
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerSinaIask(CrawlerBase ):
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
        objMain = CrawlerSinaIaskMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerSinaIaskSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
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

        objSub  = CrawlerSinaIaskSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
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
class   CrawlerSinaIaskMain(CrawlerSiteScrollMain):
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
                               'curPageText':"#searchPage a.active",
                               'curPageBtn':"#searchPage a.active",
                               'nextPageBtn':".btn-page[desc='xiayiye']",
                               'bottomAllPageNum':" "
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox': "#J_search",
                                  'clkButton':"#serach_btn",
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
                                    'main':"p.title-text > a",
                                    #'sub' :"dt.dt.mb-4.line > a.ti"
                                   }

        #log
        self.log_inits("sina_iask/main",1,1,logging.INFO)

        self.compoundword_for_url_next = "" # 用于下一页url地址的拼接
    #-------------------------------------------------------------------------------------
    
    
    #--------------------------------------------------------------------------------------  
    async def dealMainScrollBefor(self,page,crawlerInfo):

        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #
    async def  waitforPageLoad(self,page):

        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        self.compoundword_for_url_next = compoundword
        ret,newPage = await self.searchWordNewPage(page,compoundword)
        return ret,newPage
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerSinaIaskMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []
        strUrl     = crawlerInfo.url
        strCompoundword = crawlerInfo.compoundword
        strKeyword      = crawlerInfo.keyword
        
        selector   = self.cssPageBtnDict["curPageText"]
        nPage      = await self.getMainCurPageVal(page,selector)



        cssMain = self.cssMainItemHrefText["main"]
        propertyName = "href"
        elements = await page.querySelectorAll(cssMain)
        
        itemNo = 0
        for item in elements:
            itemNo += 1
            ret           = 1
            title_link    = ""
            
            result,title_link = await self.pyteerEx.getElementProDef(page,item,propertyName)
            
            if len(title_link.strip()) > 0:
               title_link = "https://iask.sina.com.cn" + title_link
               grapItem = GrapTopItemInfo(title_link,strKeyword,strCompoundword)
               grapItem.main_title   = ""
               grapItem.main_url     = strUrl
               grapItem.serverTaskId = crawlerInfo.serverTaskId
               grapItem.pageNo       = nPage
               grapItem.itemNo       = itemNo
               
               grapTopBuf.append(grapItem)
               
        
        self.printLogInfo("CrawlerSinaIaskMain->dealSubCrawlerAsItem() : exit")
        
        return RetVal.Suc.value,grapTopBuf
#--------------------------------------------------------------------------------------
    # goto to next page
    # return:
    #   isFinish   = 0：继续抓取子页的下一页
    #   isFinish   = 1: 子页完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开子页的下一页
    #   isFinish   = 3: 抓取失败，退出     
    async def  dealSubGotoNextPage(self,page,curGrapNum,maxPageNum):

        self.getLogInfo().show("CrawlerSinaIaskMain->dealSubGotoNextPage() : enter ")
        
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
            self.getLogInfo().show("CrawlerSinaIaskMain->dealSubGotoNextPage() : success to find next button element ")
            
            url_next = "https://iask.sina.com.cn/search?searchWord=" + str(parse.quote(self.compoundword_for_url_next)) + "&page=" + str(curPageNum+1)
            
            ret  = await self.pyteerEx.clickNavigate(page,selectorBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
            loop = 3
            while True:
                if await self.getCurPageVal(page) == curPageNum+1:#有可能返回值不是成功，但是已经到了下一页
                    self.getLogInfo().show("CrawlerSinaIaskMain->dealSubGotoNextPage() : success to goto next page ")
                    isFinish   = RetVal.GrapSucRepeat.value
                    break
                else:
                    if loop == 0:# 三次刷新结束
                        isFinish   = RetVal.GrapFailRepeat.value #退出
                        break
                    loop -= 1
                    await self.pyteerEx.refreshPage(page)
                    await asyncio.sleep(2)

            # if ret == RetVal.Suc.value:
            #     self.getLogInfo().show("CrawlerSinaIaskMain->dealSubGotoNextPage() : success to goto next page ")
            #     isFinish   = RetVal.GrapSucRepeat.value
            # else:
            #     isFinish   = RetVal.GrapFailRepeat.value #退出
        elif ret == RetVal.Fail.value:     #not find,finish
            isFinish = RetVal.GrapSuc.value
        else:              #异常->退出，并打开下一页page的url
            isFinish = RetVal.GrapFailRepeat.value   #退出

        self.getLogInfo().show("CrawlerSinaIaskMain->dealSubGotoNextPage() : exit ") 

        return isFinish,url_next

