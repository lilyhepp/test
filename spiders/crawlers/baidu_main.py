import asyncio
import sys,os
from pyppeteer import launch

sys.path.append("..")

from  struct_def import *
from crawlers.search_base_sites import *
from pyteerex.pyppeteer_ex      import *
from  log.logger import Logger
from crawlers.common_data import *

from crawlers.baidu_sub   import *
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerBaidu(CrawlerBase ):

    def __init__(self,num):
       super().__init__(num )
    
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerBaidu->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerBaidu->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerBaidu->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerBaidu->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerBaidu->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerBaidu->crawlerDefCompoundword():enter ")

        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerBaiduMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)
        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = BaiduSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.Page.value,colTastList)

        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerBaidu->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):
        pass
       
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerBaiduMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数

        #--滚动条滚动的步长
        self.autoScrollStep            = 80
      

        #-----------------------------------------------
        #--other
        
        self.cssPageBtnDict = {
                               'prePageBtn':"",
                               'curPageText':"div#wrapper >div#wrapper_wrapper>div#container>div#page > strong >span.pc",
                               'curPageBtn': "div#wrapper >div#wrapper_wrapper>div#container>div#page > strong >span.pc",
                               'nextPageBtn':" div#wrapper >div#wrapper_wrapper>div#container>div#page >a:nth-last-child(1)",# a.n ",
                               'nextPageName':"下一页>",
                               'bottomAllPageNum':""
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox': "div.head_wrapper >div.s_form >div.s_form_wrapper  > form.fm>span.bg.s_ipt_wr > input.s_ipt",
                                  'clkButton':"div.head_wrapper >div.s_form >div.s_form_wrapper  > form.fm>span.bg.s_btn_wr > input.bg.s_btn ",
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
                                    'main'      :"div#wrapper >div#wrapper_wrapper>div#container>div#content_left>div.OPIkYb._Nnxjv.dsMGpC ",
                                    'main-href' :"div.DgBqzs>h3.t.VboUvI.iKTgQD >a.RNrEDP",
                                    'main-title':"div.DgBqzs>h3.t.VboUvI.iKTgQD >a.RNrEDP",
                                    'main-text' :"div.c-abstract.UeCrux.mrpjTw >div.c-row.c-gap-top-small>div.c-span18.c-span-last>div  ",
                                    #-------
                                    'other'      :"div#wrapper >div#wrapper_wrapper>div#container>div#content_left>div.result.c-container  ",
                                    'other-href' :"h3.t>a",
                                    'other-title':"h3.t>a",
                                    'other-text' :"div.c-abstract",
                                    #-------hotword
                                    'hotword':"div#wrapper >div#wrapper_wrapper>div#container>div#rs>table>tbody>tr",
                                    'hotwordSub':"th",
                                    'hotwordSubText':"a",

                                   }


        #log
        self.log_inits("baidu/main",2,2,logging.INFO)

    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------    
    
    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        return await self.searchWordBase(page,compoundword)
    
    #--------------------------------------------------------------------------------------
    #get hotword
    async def getHotword(self,page):
        
        self.printLogInfo("CrawlerTiebaMain->getHotword() : enter")

        hotText     = ""
        selector    = self.cssMainItemHrefText["hotword"]
        selectorSub = self.cssMainItemHrefText["hotwordSub"] 
        selectorText = self.cssMainItemHrefText["hotwordSubText"] 

        ret,elementList = await self.pyteerEx.getElementAll(page,selector)
        
        for item in elementList:
            
            ret1,elementListSub = await self.pyteerEx.getElementAll(item,selectorSub)
            for itemSub in elementListSub:
               
               ret2,curText = await self.pyteerEx.getElementContext(itemSub,selectorText)
               
               if ret2 == RetVal.Suc.value:
                   
                   hotText = hotText + GrapReplyInfo.dealStr(curText) +";"

        self.printLogInfo("CrawlerTiebaMain->getHotword() : exit")

        return hotText   

    #--------------------------------------------------------------------------------------
    # goto to next page
    # return:
    #   isFinish   = 0：继续抓取下一页
    #   isFinish   = 1: 完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开下一页
    #   isFinish   = 3: 抓取失败，退出     
    async def  dealSubGotoNextPage(self,page,curPageIndex,maxPageNum):
        self.getLogInfo().show("CrawlerBaiduMain->dealSubGotoNextPage()->index={}: enter ".format(curPageIndex))
        
        isFinish    = RetVal.GrapSucRepeat.value
        nAllPageNum = 0
        ret         = RetVal.Suc.value
        strRet      = ""
        url_next    = ""
        
        cssCurPage        = self.cssPageBtnDict["curPageText"]
        selectorNextBtn   = self.cssPageBtnDict["nextPageBtn"]
        nextPageName      = self.cssPageBtnDict["nextPageName"]
        
        #all page
        ret1,element = await self.pyteerEx.getElement(page,selectorNextBtn)
        if ret1 == RetVal.Suc.value:
            ret2,strName = await self.pyteerEx.getElementContext(element)
            if ret2 == RetVal.Suc.value:   #get name
                if strName == nextPageName:
                    
                    url_next = await self.pyteerEx.getElementHref(element)

                    await self.pyteerEx.hovers(element)
                    
                    ret2  = await self.pyteerEx.clickNavigate(page,selectorNextBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
                    if ret2 == RetVal.Suc.value:
                        isFinish   = RetVal.GrapSucRepeat.value
                    else:
                        isFinish   = RetVal.GrapFailRepeat.value
                else:
                    self.getLogInfo().show("CrawlerBaiduMain->dealSubGotoNextPage()->index={}: has not next page ".format(curPageIndex))
                    isFinish = RetVal.GrapSuc.value  
            else:
                isFinish   = RetVal.GrapFailRepeat.value
            
            
        elif ret1 ==  RetVal.Fail.value:   #only one page
            isFinish   = RetVal.GrapSuc.value
        elif ret1 >RetVal.Fail.value:
            isFinish   = RetVal.GrapFailRepeat.value

        self.getLogInfo().show("CrawlerBaiduMain->dealSubGotoNextPage()->index={}: exit ".format(curPageIndex))  

        return isFinish,url_next  
    

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
        
        self.printLogInfo("CrawlerBaiduMain->dealSubCrawlerAsItem() : enter")

        hotWordText    = ""
        grapTopBuf  = []
        title_str  = ""
        title_link = ""
        strUrl     = crawlerInfo.url
        strCompoundword = crawlerInfo.compoundword
        curPageNo  = 0
        subItemNo  = 0
        
        #----get hot words
        if crawlerInfo.hotWord > 0:
           hotWordText = await self.getHotword(page)

        #----current page
        curPageNo = await self.getCurPageVal(page)
        
        #-------------
        cssMain = self.cssMainItemHrefText["main"]
        ret,elements = await self.pyteerEx.getElementAll(page,cssMain)
        
        for item in elements:
            subItemNo += 1

            selector     = self.cssMainItemHrefText["main-href"]
            ret,strHref  = await self.pyteerEx.getElementHref(item,selector)
            isValid      = self.checkUrlValid(strHref)
            if not isValid:
                continue

            grapInfo     =  GrapTopItemInfo(strHref,crawlerInfo.keyword,crawlerInfo.compoundword)
            
            grapInfo.main_url   = ""
            grapInfo.pageNo     = curPageNo
            grapInfo.itemNo     = subItemNo
            grapInfo.hotWords   = hotWordText

            selector     = self.cssMainItemHrefText["main-title"]
            ret,strVal   = await self.pyteerEx.getElementContext(item,selector)
            grapInfo.main_title =  GrapReplyInfo.dealStr(strVal)     

            selector     = self.cssMainItemHrefText["main-text"]
            ret,strVal  = await self.pyteerEx.getElementContext(item,selector)
            grapInfo.main_text =  GrapReplyInfo.dealStr(strVal)    
            
            
            grapTopBuf.append(grapInfo)

        #------------------
        cssMain = self.cssMainItemHrefText["other"]
        ret,elements = await self.pyteerEx.getElementAll(page,cssMain)
        
        for item in elements:
            subItemNo += 1

            selector     = self.cssMainItemHrefText["other-href"]
            ret,strHref  = await self.pyteerEx.getElementHref(item,selector)
            
            grapInfo     =  GrapTopItemInfo(strHref,crawlerInfo.keyword,crawlerInfo.compoundword)
            
            grapInfo.main_url   = ""
            grapInfo.pageNo     = curPageNo
            grapInfo.itemNo     = subItemNo
            grapInfo.hotWords   = hotWordText

            selector     = self.cssMainItemHrefText["other-title"]
            ret,strVal   = await self.pyteerEx.getElementContext(item,selector)
            grapInfo.main_title =  GrapReplyInfo.dealStr(strVal)     

            selector     = self.cssMainItemHrefText["other-text"]
            ret,strVal  = await self.pyteerEx.getElementContext(item,selector)
            grapInfo.main_text =  GrapReplyInfo.dealStr(strVal)  
            
            grapTopBuf.append(grapInfo)
        
        

        

        curCount = 0
        for item in grapTopBuf:
            curCount += 1

            self.printGrapInfo(" ")
            self.printGrapInfo("--------------------------")
            self.printGrapInfo("href={}".format(item.url))
            self.printGrapInfo("main_href={}".format(item.main_url))
            self.printGrapInfo("main_title={}".format(item.main_title))
            self.printGrapInfo("main_text={}".format(item.main_text))
            self.printGrapInfo("pageNo={}".format(item.pageNo))
            self.printGrapInfo("itemNo={}".format(item.itemNo))
            self.printGrapInfo("hotwords={}".format(item.hotWords))
        
        self.printLogInfo("CrawlerBaiduMain->dealSubCrawlerAsItem() : exit")
        return RetVal.Suc.value,grapTopBuf
    
    #--------------------------------------------------------------------------------------
    #
    def  checkUrlValid(self,strUrl):
        
        return RetVal.Suc.value