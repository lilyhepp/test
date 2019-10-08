#---------------weibo_main.py
#--微博--主抓取
import  sys,os
import  asyncio
import  datetime
from    pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  log.logger                 import  Logger
from  crawlers.common_data       import *

from  crawlers.weibo_sub         import *
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class CrawlerWeibo(CrawlerBase ):

    def __init__(self,num):
       super().__init__(num )
       
    def crawlerScroll(self,loop,crawlerTaskInfo,configParaInfo):
        print("CrawlerWeibo->crawlerScroll() :enter")

        if crawlerTaskInfo.grap_type   ==  GrapTypeEm.Compoundword:

            print("CrawlerWeibo->crawlerScroll() :GrapTypeEm.Compoundword")
            crawlerTaskInfo.grap_mapData = GrapDataDict([])
            self.crawlerDefCompoundword(loop,crawlerTaskInfo,configParaInfo)

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.Url:

            print("CrawlerWeibo->crawlerScroll() :GrapTypeEm.Url")
            crawlerTaskInfo.grap_mapData = GrapDataDict(crawlerTaskInfo.grap_data )
            self.crawlerDefUrl(loop,crawlerTaskInfo,configParaInfo )

        elif crawlerTaskInfo.grap_type ==  GrapTypeEm.User:
            
            print("CrawlerWeibo->crawlerScroll() :GrapTypeEm.User")
            self.crawlerDefUser(loop,crawlerTaskInfo,configParaInfo )

        print("CrawlerWeibo->crawlerScroll() :leave")
        
    #------------------------------------------------------------------------------------
    #---compoundword
    def crawlerDefCompoundword(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerWeibo->crawlerDefCompoundword():enter ")
        
        subColNum   = self.subCoroutineNum
        colTastList = []
        ObjMainList = []
        ObjSubList  = []
        queueDict   = self.queueDict
        
        #--微博加“”
        #crawlerTaskInfo.compoundword = '"{}"'.format(crawlerTaskInfo.compoundword)
        #----main
        objMain = CrawlerWeiboMain(crawlerTaskInfo.grap_type,queueDict,configParaInfo)
        ObjMainList.append(objMain)

        self.crawlerAsPageOrScroll(ObjMainList,crawlerTaskInfo,GrapTypeFuncEm.KeyMain.value,subColNum,GrapScrollEm.Page.value,colTastList)
        
        """
        #-----sub
        for i in range(1,subColNum):
            objSub  = CrawlerWeiboSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,i)
            ObjSubList.append(objSub)

        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.KeySub.value,0,GrapScrollEm.Page.value,colTastList)
        """
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerWeibo->crawlerDefCompoundword():leave ")
        
    #------------------------------------------------------------------------------------
    #crawler defined url
    def crawlerDefUrl(self,loop,crawlerTaskInfo,configParaInfo):

        print("CrawlerWeibo->crawlerDefUrl():enter ")
        colTastList = []
        ObjSubList  = []
        queueDict   = self.queueDict

        objSub  = CrawlerWeiboSub(crawlerTaskInfo.grap_type,queueDict,configParaInfo,1)
        ObjSubList.append(objSub)
        
        self.crawlerAsPageOrScroll(ObjSubList,crawlerTaskInfo,GrapTypeFuncEm.DefUrl.value,0,GrapScrollEm.Page.value,colTastList)
        
        #-----add loop
        self.allColTastToLoop(loop,colTastList)

        print("CrawlerWeibo->crawlerDefUrl():enter ")
    #------------------------------------------------------------------------------------
    #crawler defined user
    def crawlerDefUser(self,loop,crawlerInfo,configParaInfo):

        pass
    
#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerWeiboMain(CrawlerSiteScrollMain):
    def __init__(self,crawlerType,queueDict,configParaInfo):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #---------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        self.isCommitData              = True
        #-----------------------------------------------
        #--other
        self.cssPageBtnDict = {
                               'tailPageText':"",
                               'prePageBtn':"div.m-wrap>div.m-con-l>div.m-page>div>a.prev",
                               'curPageText':"div.m-wrap>div.m-con-l>div.m-page>div>span.list>a.pagenum",
                               'curPageBtn':"div.m-wrap>div.m-con-l>div.m-page>div>span.list>a.pagenum",
                               'nextPageBtn':"div.m-wrap>div.m-con-l>div.m-page>div>a.next",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox1': "div.WB_miniblog_fb >div#weibo_top_public>div.WB_global_nav.WB_global_nav_v2>div.gn_header.clearfix>div.gn_search_v2 > input.W_input",
                                  'inputBox':  "div.WB_miniblog_fb >div#plc_top>div.WB_global_nav >div.gn_header.clearfix>div.gn_search_v2 > input.W_input",
                                  'clkButton1': "div.WB_miniblog_fb >div#weibo_top_public>div.WB_global_nav.WB_global_nav_v2>div.gn_header.clearfix>div.gn_search_v2 > a.W_ficon",
                                  'clkButton':  "div.WB_miniblog_fb>div#plc_top>div.WB_global_nav >div.gn_header.clearfix>div.gn_search_v2 > a.W_ficon ",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
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
                                    'main':"div.s_main > div.s_post_list > div.s_post > span.p_title > a.bluelink ",
                                    
                                    #
                                    'main_more_href':"div.m-wrap>div.m-con-l>div>div.card-wrap>div.card-top>a.more",
                                    #-------------------------------------
                                    #----列表子项
                                    'main_sub'      :"div.m-wrap>div.m-con-l>div>div.card-wrap",
                                    #展开全文按钮及按钮文本
                                    'main_sub_btn_all':"div.card>div.card-feed>div.content>p.txt>a",
                                    'main_sub_btn_all_text':"展开全文",
                                    #内容
                                    'main_sub_text':   "div.card>div.card-feed>div.content>p.txt",
                                    #发布者
                                    'main_sub_publish':"div.card>div.card-feed>div.content>div.info>div.menu+div>a.name",
                                    #发布时间:格式->09月28日 22:57
                                    'main_sub_time':   "div.card>div.card-feed>div.content>p.from>a:nth-child(1)",
                                    #转发数--》格式: 转发 41
                                    'main_sub_forward': "div.card>div.card-act>ul>li:nth-child(2)>a",
                                    #评论数-->格式:  评论 23
                                    'main_sub_comment': "div.card>div.card-act>ul>li:nth-child(3)>a",
                                    #点赞数-->格式:118
                                    'main_sub_stars': "div.card>div.card-act>ul>li:nth-child(4)>a>em",


                                    #--热点标题
                                    'main_sub_hot':   "div.card-top>h4.title>a",
                                    'main_sub_text':  "div.card>div.card-feed>div.content>p.txt",

                                    'main_sub_url':   "div.card>div.card-feed>div.content>p.from>a:nth-child(1)",
                                    #
                                   }

        #log
        self.log_inits("weibo/main",1,1,logging.INFO)

    #----------------------------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------    
    async def  login(self,page):

        
        self.printLogInfo("CrawlerWeiboMain->login() : enter")
        
        delayMin = 15
        delayMax = 30
        #--select account
        selector = self.cssLoginDict["accountLogin"]
        ret = await self.pyteerEx.clickHoverElement(page,selector)
        if ret != RetVal.Suc.value:
            return ret
        
        #--input user name
        curText = "15986730292"
        selector = self.cssLoginDict["user_name"]
        ret = await self.pyteerEx.inputText(page,selector,curText,delayMin,delayMax)
        if ret != RetVal.Suc.value:
            return ret

        #--input password
        curText = "xfyms2019"
        selector = self.cssLoginDict["password"]
        ret = await self.pyteerEx.inputText(page,selector,curText,delayMin,delayMax)
        if ret != RetVal.Suc.value:
            return ret

        #--input autologin
        """
        selector = self.cssLoginDict["autoLogin"]
        ret = await self.pyteerEx.clickHoverElement(page,selector)
        if ret != RetVal.Suc.value:
            return ret
        """

        #--click
        selector = self.cssLoginDict["clk_button"]
        ret = await self.pyteerEx.clickNavigate(page,selector)
        if ret != RetVal.Suc.value:
            return ret
        
        self.printLogInfo("CrawlerWeiboMain->login() : exit ret ={}".format(ret))
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #search compoundword
    async def searchWord(self,page,compoundword):
        return await self.searchWordBase(page,compoundword)

    #--------------------------------------------------------------------------------------
    #
    async def  waitforPageLoad(self,page):
        #return await self.pyteerEx.waitPage(page,self.cssPageBtnDict["tailPageText"],4)
        self.printLogInfo("CrawlerTiebaMain->waitforPageLoad() : enter")
        """
        cssList  = []
        selector = self.cssSearchDict["inputBox"]
        cssList.append(selector)
        selector = self.cssSearchDict["inputBox1"]
        cssList.append(selector)
        
        ret = await self.pyteerEx.waitPageAll(page,cssList,25)

        self.printLogInfo("CrawlerTiebaMain->waitforPageLoad() : exit")
        return ret
        """
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #
    async def dealMainScrollBefor(self,page,crawlerInfo):

        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : enter")

        cssList  = []
        selector = self.cssSearchDict["inputBox"]
        cssList.append(selector)
        selector = self.cssSearchDict["inputBox1"]
        cssList.append(selector)
        
        ret = await self.pyteerEx.waitPageAll(page,cssList,20)

        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : exit")
        return ret



        #await asyncio.sleep(20)
        """
        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : enter")
        #图片文字
        title_link ="https://tieba.baidu.com/p/6204167088?pn=1"

        #title_link = "http://tieba.baidu.com/p/6215325051?pn=1"
        title_str  = " "

        grapItem = GrapTopItemInfo(title_link,"",title_str )
        await self.topSubItemQueue.put(grapItem )
        
        await asyncio.sleep(60*30)
        """
        return RetVal.Suc.value
    #--------------------------------------------------------------------------------------
    #do crawler a web page 
    async def  dealSubCrawlerAsItem(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsItem() : enter")

        #await asyncio.sleep(60)
        grapTopBuf = []
        result     = RetVal.Suc.value
        
        #--current page
        nPageNo = await self.getCurPageVal(page)
        crawlerInfo.curPageNo = nPageNo
        crawlerInfo.pageNo    = nPageNo
        
        self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsFloor() : crawler begin page={}".format(nPageNo))
        
        selector = self.cssMainItemHrefText["main_sub"]
        ret,elementList = await self.pyteerEx.getElementAll(page,selector )
        nItemNo = 0

        for item in elementList:
            nItemNo += 1
            crawlerInfo.itemNo = nItemNo
            #----
            ret,replyInfo = await self.grapMainSubInfo(page,item,crawlerInfo)
            if ret == RetVal.Suc.value:
                ret1 = self.checkStrIncludeKeyword(crawlerInfo.main_title,replyInfo.text,crawlerInfo.keyword)
                if ret1 == RetVal.Suc.value:
                    grapTopBuf.append(replyInfo)
                else: #找不到关键字
                    crawlerInfo.keywordInGrapBufCount += 1
                    if crawlerInfo.keywordInGrapBufCount >= self.subPageDataEmptyMaxCount: #退出抓取
                        result = RetVal.FailExitNotFindKeyword.value
                        self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsItem() : not find max keyword,grap exit")
                        break
            else:
                continue      
            
            """
            isCheckTitle = 0
            ret1,curText = await self.pyteerEx.getElementContext(item,selectorHot )
            if ret1 == RetVal.Suc.value:
                self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsFloor() : hot name={}".format(curText))
                if curText == "热门":
                    isCheckTitle = 1

            #-----check title and text
            if isCheckTitle == 1:
               
                ret1,curText  = await self.pyteerEx.getElementContext(item,selectorText )
                curText       = curText.strip()
                self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsFloor() : check hot title keyword={}".format(keyword))
                self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsFloor() : check hot title={}".format(curText))
                if self.checkTextIncludeKeyword(curText,keyword ) != RetVal.Suc.value:
                    continue
                else:
                    self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsFloor() : in curText find keyword")
               
            
            #------get url
            ret,curText = await self.pyteerEx.getElementHref(item,selectorUrl)
            
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
            """   

        self.printLogInfo("CrawlerWeiboMain->dealSubCrawlerAsItem() : crawler other end page={}".format(nPageNo))    
        
        return result,grapTopBuf

    #-----------------------------------------------------------------------------------------
    #click "展开全文"
    async def clickAllTextButton(self,page):

        selector = self.cssMainItemHrefText["main_sub_btn_all"]
        curCount = 300

        while curCount > 0:
            curCount -= 1

            ret = await self.pyteerEx.clickHoverElement(page,selector,1,1)
            if ret == RetVal.Fail.value:
                break

    #-----------------------------------------------------------------------------------------
    #抓取信息
    #--------------------------------------------------------------------------------------
    #---获取pageUrl的地址->1>先去除地址中？之后的字符;2>然后去除#之后的字符
    #                 
    #---return:  
    #         =pageUrl
    def getPageUrl(self,strUrl):
        return 'https://s.weibo.com/weibo/'

    #-----------------------------------------------------------------------------------------
    #抓取信息
    async def grapMainSubInfo(self,page,element,crawlerInfo):
        self.printLogInfo("CrawlerWeiboSub->grapMainReplyInfo() : enter")
        
        ret    = RetVal.Suc.value
        ret1   = RetVal.Suc.value
        result = RetVal.FailExit.value
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href    = crawlerInfo.url
        replyInfo.pageUrl = self.getPageUrl(crawlerInfo.url)
        
        
        curStep = 1
        while curStep > 0:
            curStep -=1
            
            self.clickAllTextButton(page)
            #-----------------------------------------------
            #--publisher
            selector     = self.cssMainItemHrefText["main_sub_publish"]
            ret,curText = await self.pyteerEx.getElementContext(element,selector)
            if ret == RetVal.Suc.value:
                curText             = CommonTool.strStripRet(curText)
                replyInfo.publisher = curText
            else:
                break
            #-----------------------------------------------
            #--text
            selector     = self.cssMainItemHrefText["main_sub_text"]
            ret,curText  = await self.pyteerEx.getElementContext(element,selector)
            if ret == RetVal.Suc.value:
                curText             = CommonTool.strStripRet(curText)
                replyInfo.text = curText
            else:
                break
            
            #--publisher_time -> 格式:09月28日 22:57
            selector     = self.cssMainItemHrefText["main_sub_time"]
            ret,curText  = await self.pyteerEx.getElementContext(element,selector)
            self.printLogInfo("CrawlerWeiboSub->grapMainReplyInfo() : time={}".format(curText))
            if ret == RetVal.Suc.value:
                curText             = CommonTool.strStripRet(curText)
                replyInfo.publishTime = self.getPublishTime(curText)
                self.printLogInfo("CrawlerWeiboSub->grapMainReplyInfo() : time={}".format( replyInfo.publishTime))
            else:
                break
            
            #--转发数
            selector     = self.cssMainItemHrefText["main_sub_forward"]
            ret,curText  = await self.pyteerEx.getElementContext(element,selector)
            if ret == RetVal.Suc.value:
                curText             = CommonTool.getDigitFromString(curText.strip())
                replyInfo.forwards  = curText
            else:
                break
            
            #--评论数
            selector     = self.cssMainItemHrefText["main_sub_comment"]
            ret,curText  = await self.pyteerEx.getElementContext(element,selector)
            if ret == RetVal.Suc.value:
                curText               = CommonTool.getDigitFromString(curText.strip())
                replyInfo.comments = curText
            else:
                break
            
            #--点赞数 格式:118
            selector     = self.cssMainItemHrefText["main_sub_stars"]
            ret,curText  = await self.pyteerEx.getElementContext(element,selector)
            if ret == RetVal.Suc.value:
                curText               = CommonTool.getDigitFromString(curText.strip())
                replyInfo.stars = curText
            else:
                break

            #--------end
            result = RetVal.Suc.value
        #--------------------------------------------------end while

        if result == RetVal.Suc.value:
            #-----注释
            """
            replyInfo.parentContentId      = crawlerInfo.p_parentPageItemNo
            crawlerInfo.p_curPageItemNo    += 1
            replyInfo.contentId            = crawlerInfo.p_curPageItemNo
            """
            #-----不抓取回复的设定值
            replyInfo.parentContentId      = 0
            crawlerInfo.p_curPageItemNo    = 1
            replyInfo.contentId            = crawlerInfo.p_curPageItemNo
            
            self.printReplyInfo(replyInfo,crawlerInfo)
        #---------------------------------------------------
        
        self.printLogInfo("CrawlerWeiboSub->grapMainReplyInfo() : exit")
        
        return result,replyInfo
        
        
        

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
    
    #-----------------------------------------------------------------------------------------
    #获取发布时间-->
    #   时间分下面几种情况：
    #       1>针对热点: 
    #                >不是当前年->格式:2018年04月28日 12:52; 
    #                     :需要补秒
    #                >当前年->格式: 09月21日 08:10
    #                     :需要补年    
    #       2>非热点:
    #                >5分钟前
    #                >今天14:19
    #                >09月28日 23:46
    #                >2018年08月14日 22:18         
    def getPublishTime(self,timeStr):
        
        curTime    = datetime.datetime.now()
        nType      = 0
        timeRet    = ""
        replyTime  = None
        
        self.printLogInfo("CrawlerWeiboSub->getPublishTime() : {}".format(timeStr))


        try:
            if timeStr.find("今天") != -1:
                curBuf = CommonTool.strSplit(timeStr," ")
                curText = curBuf[len(curBuf)-1]
                curText = CommonTool.strSplitIndex(curText.strip()," ",0)

                curText = CommonTool.strSplitIndex(curText.strip(),":",0)
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : hou={}".format(curText))
                nHour   = CommonTool.getDigitFromString(curText)
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : hou={}".format(nHour))
                curText = CommonTool.strSplitIndex(timeStr,":",1)
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : hou={}".format(curText))
                nMinute = CommonTool.getDigitFromString(curText)
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : hou={}".format(nMinute))

                replyTime = datetime.datetime(curTime.year,curTime.month,curTime.day,nHour,nMinute,0 )
            
            elif (timeStr.find("年") != -1) and (timeStr.find("月") != -1 ):
                nType   = 1
                strBuf  = CommonTool.strSplit(timeStr,"年")
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : year={} len={}".format(strBuf[0],len(strBuf)))
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : year={}".format(strBuf[1]))
                if len(strBuf) == 2:
                    strMonth = strBuf[1].strip()
                    timeRet = self.getTimeFromMonth(strMonth,strBuf[0])
                else:
                    timeRet = "{}-{}-{} {}".format(1970,1,1,"00:00:00")
            elif (timeStr.find("月") != -1) and (timeStr.find("日") != -1 ):
                nType = 1
                self.printLogInfo("CrawlerWeiboSub->getPublishTime() : hou={}".format(timeStr))
                
                


                timeRet = self.getTimeFromMonth(timeStr,"{}".format(curTime.year))
            elif timeStr.find("分钟") != -1:
                curText = CommonTool.strSplitIndex(timeStr.strip()," ",0)
                nVal = CommonTool.getDigitFromString(curText)
                replyTime = curTime - datetime.timedelta(minutes=nVal )
            elif timeStr.find("秒钟") != -1:
                curText = CommonTool.strSplitIndex(timeStr.strip()," ",0)
                nVal = CommonTool.getDigitFromString(curText)
                replyTime = curTime - datetime.timedelta(seconds=nVal )
            elif timeStr.find("小时前") != -1:
                curText = CommonTool.strSplitIndex(timeStr.strip()," ",0)
                nVal = CommonTool.getDigitFromString(curText)
                replyTime = curTime - datetime.timedelta(hours=nVal )
            elif timeStr.find("天前") != -1:
                curText = CommonTool.strSplitIndex(timeStr.strip()," ",0)
                nVal = CommonTool.getDigitFromString(curText)
                replyTime = curTime - datetime.timedelta(days=nVal )

        except Exception:
            self.printLogInfo("CrawlerToutiaoSub->getReplyTime() : exception")
            timeRet = "{}-{}-{} {}".format(1970,1,1,"00:00:00")
            nType = 1
        
        if nType != 1:
            if replyTime is not None:
               timeRet =  replyTime.strftime("%Y-%m-%d %H:%M:%S")
            else:
               timeRet = "{}-{}-{} {}".format(1970,1,1,"00:00:00")
        
        return timeRet

    #---------------------------------------------------------
    #----格式: 9月3日 19:30  ;目标格式:2019-09-03 19:30:00 
    def getTimeFromMonth(self,timeText,strTimeYear):
        
        strDate  = "00-00-00 00:00:00"
        strList  = CommonTool.strSplit(timeText," ")
        count    = len(strList)
        if count > 1:
            str1 = strList[0]
            strTime = strList[count-1].strip()
            monthDayBuf = CommonTool.strSplitDigit(str1)

            if len(monthDayBuf) == 2:
                #--
                strMonth = monthDayBuf[0]
                if len(strMonth) == 1:
                    strMonth = "0{}".format(strMonth)
                #--
                strDay   = monthDayBuf[1]
                if len(strDay) == 1:
                    strDay = "0{}".format(strDay)
                #--
                if len(strTime) == 5:
                    strTime = strTime + ":00"
                else:
                    strTime = "00:00:00"

                #----
                strDate = "{}-{}-{} {}".format(strTimeYear,strMonth,strDay,strTime)
        
        return strDate




    

