#--------------baidu_tieba_main.py
#--百度贴吧
import sys,os
import asyncio
import sys
import logging
import random
import time
from pyppeteer import launch

sys.path.append("..")

from  struct_def                import *
from crawlers.search_base_sites import *
from pyteerex.pyppeteer_ex      import *
from  log.logger                import Logger
from crawlers.common_data       import *

from crawlers.baidu_tieba_sub   import *
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerTieba(CrawlerBase ):
    #------------------------------------------------------------------------------------
    def __init__(self,num):
       super().__init__(num )

    #------------------------------------------------------------------------------------   
    #
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerTieba->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerTieba->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerTieba->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerTieba->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerTieba->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---关键字抓取
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerTieba->crawlerDefCompoundword():enter ")
        
        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerTiebaMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerTiebaSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.Page.value,colTastList)
        
        #-----add loop
        print(len(colTastList))
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerTieba->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #指定网页抓取
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerTieba->crawlerDefUrl():enter ")
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerTiebaSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.Page.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        
        print("CrawlerTieba->crawlerDefUrl():enter ")
    #------------------------------------------------------------------------------------
    #指定用户抓取
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#-------主抓取类
class   CrawlerTiebaMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
       
        
        #-----------------------------------------------
        #--other
        self.cssPageBtnDict = {
                               'tailPageText':"div.wrap1>div.wrap2>div.footer>span",
                               'prePageBtn':"",
                               'curPageText':"div.wrap2 > div.s_container.clearfix > div.pager.pager-search > span.cur",
                               'curPageBtn':"div.wrap2 > div.s_container.clearfix > div.pager.pager-search > span.cur",
                               'nextPageBtn':"div.wrap2 > div.s_container.clearfix > div.pager.pager-search > a.next",
                               'bottomAllPageNum':"div.pb_footer > div#thread_theme_7 > div.l_thread_info > ul.l_posts_num > li.l_reply_num > span.read"
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox': "div.search_form > form#tb_header_search_form > input#wd1",
                                  'clkButton':"div.search_form > form#tb_header_search_form >  span.search_btn_wrap > a.search_btn.j_search_post",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
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
                                    'main':"div.s_main > div.s_post_list > div.s_post > span.p_title > a.bluelink ",
                                    'sub' :""
                                   }

        #log
        self.log_inits("tieba/main",1,1,logging.INFO)

    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------    
    async def  login(self,page):

        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        return await self.searchWordBase(page,compoundword)
    
    #--------------------------------------------------------------------------------------
    #
    async def  waitforPageLoad(self,page):
        return await self.pyteerEx.waitPage(page,self.cssPageBtnDict["tailPageText"],4)
    
    #--------------------------------------------------------------------------------------
    #
    async def dealMainScrollBefor(self,page,crawlerInfo):
        """
        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : enter")
        #图片文字
        title_link ="https://tieba.baidu.com/p/6204167088?pn=1"

        #title_link = "http://tieba.baidu.com/p/6215325051?pn=1"
        title_str  = " "

        grapItem = GrapTopItemInfo(title_link,title_str )
        await self.topSubItemQueue.put(grapItem )
        
        await asyncio.sleep(60*30)
        """
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #do crawler a web page 
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerTiebaMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []
        title_str  = ""
        title_link = ""
        strUrl     = crawlerInfo.url
        strCompoundword = crawlerInfo.compoundword
        
        
        selector   = self.cssPageBtnDict["curPageText"]
        nPage      = await self.getMainCurPageVal(page,selector)
        
        itemNo = 0
        cssMain = self.cssMainItemHrefText["main"]

        elements = await page.querySelectorAll(cssMain)
        for item in elements:
            itemNo += 1
            ret,title_str  = await self.pyteerEx.getElementContext(item)
            if ret == RetVal.Suc.value:
                title_str = title_str.strip()
            else:
                title_str =  ""

            ret,title_link = await self.pyteerEx.getElementHref(item)
            if ret == RetVal.Suc.value:
                title_link = title_link.strip()
            else:
                title_link =  ""

            #
            if len(title_link.strip()) > 0:

                grapItem = GrapTopItemInfo(title_link,crawlerInfo.keyword,crawlerInfo.compoundword )
                grapItem.main_title   = ""
                grapItem.main_url     = strUrl
                grapItem.serverTaskId = crawlerInfo.serverTaskId
                grapItem.pageNo       = nPage
                grapItem.itemNo       = itemNo
                
                grapTopBuf.append(grapItem)
                
            #--
            self.printGrapInfo(title_str)
            self.printGrapInfo(title_link)
        
        self.printLogInfo("CrawlerTiebaMain->dealSubCrawlerAsItem() : exit")
        
        return RetVal.Suc.value,grapTopBuf

