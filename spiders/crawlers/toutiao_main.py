#---------------toutiao_main.py
#--头条--主抓取
import  sys,os
import  asyncio
from    pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  log.logger                 import  Logger
from  crawlers.common_data       import *

from  crawlers.toutiao_sub         import *
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerToutiao(CrawlerBase ):

    def __init__(self,num):
       super().__init__(num )
       
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerToutiao->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerToutiao->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerToutiao->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerToutiao->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerToutiao->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerToutiao->crawlerDefCompoundword():enter ")
        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #----main
        objMain = CrawlerToutiaoMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.VScroll.value,colTastList)
        
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerToutiaoSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.VScroll.value,colTastList)
        
        print(len(colTastList))
        print("CrawlerToutiao->crawlerDefCompoundword():leave ")
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerToutiao->crawlerDefUrl():enter ")
        
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerToutiaoSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.VScroll.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerToutiao->crawlerDefUrl():exit ")
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerToutiaoMain(CrawlerSiteScrollMain):
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
        """
        self.cssPageBtnDict = {
                               'tailPageText':"",
                               'prePageBtn':"",
                               'curPageText':"",
                               'curPageBtn':"",
                               'nextPageBtn':"",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"]
                                  
                                 }
        """
        #search button css
        self.cssSearchDict     = {
                                  
                                  'inputBox':   "div.bui-box>div.bui-right>div.search-wrapper>div.search-wrap>div.tt-autocomplete>div.tt-input.tt-input-group>input.tt-input__inner",
                                  'inputBox1':  "",
                                  'clkButton':  "div.bui-box>div.bui-right>div.search-wrapper>div.search-wrap>div.tt-autocomplete>div.tt-input.tt-input-group>div.tt-input-group__append>button.tt-button",
                                  'clkButton1': "",
                                  'editDelayMin' :self.searchEditDelayMin,
                                  'editDelayMax' :self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ],
                                  
                                 }
        #
        self.cssLoginDict      = {
                                 
                                 'accountLogin':"div.UG_box>div.W_unlogin_v4>div.login_box>div.login_innerwrap>div.info_header>div.tab.clearfix>a.W_fb",
                                
                                 'user_name':"div.login_box>div.login_innerwrap>div.W_login_form>div.info_list.username>div.input_wrap>input.W_input",
                                 'password' :"div.login_box>div.login_innerwrap>div.W_login_form>div.info_list.password>div.input_wrap>input.W_input",
                                 'autoLogin':"div.login_box>div.login_innerwrap>div.W_login_form>div.info_list.auto_login >label.W_fl.W_label>input.W_checkbox",
                                 'clk_button':"div.login_box>div.login_innerwrap>div.W_login_form>div.info_list.login_btn>a.W_btn_a.btn_32px",
                                
                                  }

        #main href text
        self.cssMainItemHrefText = {
                                    'main_entry':"div.feedBox >div > div.sections > div.articleCard",
                                    'main_href' :"div.item > div.item-inner>div.normal>div.rbox-inner>div.title-box>a",
                                   }
        #----------------------
        #wait page
        self.cssWaitPage         = {
                                    'element':[  #input
                                                 "div.y-box.container>div.y-left.index-middle>div.searchBar>form>div.y-box>div.y-left.search-content>input" ,


                                              ]

                                   }

        #log
        self.log_inits("toutiao/main",2,2,logging.INFO)

    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------    
    async def  login(self,page):
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        ret,newPage = await self.searchWordNewPage(page,compoundword)
        
        return ret,newPage
        
    #--------------------------------------------------------------------------------------
    #
    async def  waitforPageLoad(self,page):
        
        self.printLogInfo("CrawlerWeiboMain->waitforPageLoad() : enter")

        css = self.cssWaitPage["element"]
        ret = await self.pyteerEx.waitPageAll(page,css,10)
        
        self.printLogInfo("CrawlerWeiboMain->waitforPageLoad() : exit")

        return  ret
    #--------------------------------------------------------------------------------------
    #
    async def dealMainScrollBefor(self,page,crawlerInfo):

        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #do crawler a web page 
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsItem() : enter")
        
        grapTopBuf = []
        #--current page
        selectorHerf = self.cssMainItemHrefText["main_href"] 
        selector     = self.cssMainItemHrefText["main_entry"]
        selector     = self.makeDynamicCss(selector,crawlerInfo.vscroll_grap_count)

        ret,elementList = await self.pyteerEx.getElementAll(page,selector )
        nPageNo = 1
        nItemNo = 0
        nGrapNo = 0
        for item in elementList:
            nItemNo += 1
            ret,curText = await self.pyteerEx.getElementHref(item,selectorHerf)
            if ret == RetVal.Suc.value:
                curText     = CommonTool.strStripRet(curText)
                if curText:
                    #----check
                    self.printGrapInfo("href={}".format(curText))
                    ret1 = self.checkUrlIsSelf(curText)
                    if ret1 ==  RetVal.Fail.value:
                        continue
                    #----
                    nGrapNo += 1
                    grapItem = GrapTopItemInfo(curText,crawlerInfo.keyword,crawlerInfo.compoundword )
                    grapItem.main_title   = ""
                    grapItem.main_url     = ""
                    grapItem.serverTaskId = crawlerInfo.serverTaskId
                    grapItem.pageNo       = nPageNo
                    grapItem.itemNo       = nGrapNo
               
                    grapTopBuf.append(grapItem)
        
        #-----------------
        crawlerInfo.vscroll_grap_count += nItemNo

        self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsItem() : exit nitemNo={},grap_count={}".format(nItemNo,crawlerInfo.vscroll_grap_count))    
        
        return RetVal.Suc.value,grapTopBuf
    
    #--------------------------------------------------------------------------------------
    #----检查链接是否是头条
    def checkUrlIsSelf(self,strUrl):

        ret = RetVal.Fail.value
        strBuf = CommonTool.strSplit(strUrl,"www.toutiao.com" )
        if len(strBuf ) > 1:
            ret = RetVal.Suc.value
        
        return ret
    
