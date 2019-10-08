#----------  sogou_wenwen_sub.py
#---------- 搜狗问问子抓取
import sys,os
import asyncio
from pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  common.tools               import *
import re

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class CrawlerSogouWenWenSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 40

        #--调用clickHoverElement()函数时,click的延迟 
        self.clickDelay    = 0.6
        #--调用clickHoverElement()函数时,hover的延迟
        self.hoverDelay    = 0.6

        #-----------------------------------------------
        #--other
        self.cssPageBtnDict = {
                               'prePageBtn':"div.main>div.section>div.replay-wrap.common_answers>div.page-num.page_wrap>a.btn-page-prev",
                               'curPageText':"div.main>div.section>div.replay-wrap.common_answers>div.page-num.page_wrap>span.cur",
                               'curPageBtn':"",
                               'nextPageBtn':"div.main>div.section>div.replay-wrap.common_answers>div.page-num.page_wrap>a.btn-page-next",
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }

        #------------------------------------------------------
        #question
        self.cssContextDict    = {
                                  'mainInfo_title':"#question_title>span.detail-tit",
                                  'mainInfo_nickname':"",
                                  'mainInfo_publish_time':"",
                                  'mainInfo_content':"#question_content>pre.detail-tit-info"
                                 }

        self.cssFirstLevelReplyInfoDict = {
                                                'best_replyInfo_item':"#bestAnswers>div.replay-section.answer_item",
                                                'common_replyInfo_item':"div.main>div.section>div.replay-wrap.common_answers>div.replay-section",
                                                
                                                #------匿名用户
                                                'replyInfo_nickname':"div.replay-info>div.user-name-box>span.user-name", 
                                                
                                                #------实名用户
                                                'replyInfo_nickname1':"div.replay-info>div.user-name-box>a.user-name",   
                                                'replyInfo_publish_time':"div.replay-info>div.user-txt",
                                                'replyInfo_content':"div.replay-info>pre.replay-info-txt",
                                                'replyInfo_reply_support':"div.replay-info>div.ft-bar>div.ft-btn-box >a.btn-up>span.up-tag",            
                                                
                                                #-----------------------------------------------------
                                                'replyInfo_item_count':"div.main>div.section>div.load-more>a.btn-load-more",
                                                'replyInfo_item_count1':"div.main>div.section>div.replay-wrap.common_answers>h2.section-tit>span"
                                                }
        
    
        
        #log
        logpath = "SogouWenWen/sub/" + str(index) 
        self.log_inits(logpath,1,1,logging.INFO)

    #--------------------------------------------------------------------------------------
    #----override func waitforPageLoad
    async def waitforPageLoad(self,page):      
        return RetVal.Suc.value

    
    #--------------------------------------------------------------------------------------  
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerSogouWenWenSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.grabAllPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerSogouWenWenSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))
        
        return ret,replyInfoBuf


    
    #--------------------------------------------------------------------------------------
    #子抓取--按网址抓取    
    async def  dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerSogouWenWenSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.grabAllPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerSogouWenWenSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf

    
    #----------------------------------------------------------------------------------------
    #---抓取指定网页内容 参考document CrawlerTips.xlsx
    #---1、抓取问题信息：问题描述、问题内容等
    #---2、一级回复信息
    #---3、二级回复信息(暂时不用抓取)
    #---4、这里需要额外处理最佳回答 以及分页的情况
    async def grabAllPageData(self,page,crawlerInfo,index):
                
        self.printLogInfo("CrawlerSogouWenWenSub->grabAllPageData() : enter")
    
        replyBuf     = []
        ret          = 0
   
        #--------question info
        ret,replyInfo = await self.grabQuestionInfo(page,crawlerInfo)
        if ret == RetVal.FailExitNotFindKeyword.value:
            return ret,[]
        elif ret == RetVal.FailExit.value:
            return ret,[]
        replyBuf.append(replyInfo)

        #--------first level replyInfo
        #--------best answer grab at the first page
        curPage = await self.getCurPage(page)
        if  curPage == 1:
            ret,element = await self.pyteerEx.getElement(page,self.cssFirstLevelReplyInfoDict["best_replyInfo_item"])
            if ret == RetVal.Suc.value:
                ret,replyInfo = await self.grabFirstLevelReplyInfo(element,crawlerInfo)
                if ret != RetVal.Suc.value:
                    return RetVal.FailExit.value,replyBuf
                replyBuf.append(replyInfo)
                crawlerInfo.vscroll_grap_count +=1 #----累计抓取一级回复个数

        #-------common answer
        ret,elementList = await self.pyteerEx.getElementAll(page,self.cssFirstLevelReplyInfoDict["common_replyInfo_item"])
        if ret != RetVal.Suc.value:
            #replyBuf.append(replyInfo)
            return RetVal.Suc.value,replyBuf

        ret,firstRepleyInfoBuf = await self.grabFirstLevelReplyIteration(elementList,crawlerInfo)
        if ret != RetVal.Suc.value:
            self.printLogInfo("CrawlerSogouWenWenSub->grabAllPageData() : exit")
            replyBuf.extend(firstRepleyInfoBuf)
            return ret,replyBuf

        replyBuf.extend(firstRepleyInfoBuf)
        self.printLogInfo("CrawlerSogouWenWenSub->grabAllPageData() : exit")
        return RetVal.Suc.value,replyBuf
    

    #----------------------------------------------------------------------------------------
    #----抓取问题信息作为根回复
    async def grabQuestionInfo(self,page,crawlerInfo):

        self.printLogInfo("CrawlerSogouWenWenSub->grabQuestionInfo() : enter")        
                      
        cssTitle          = self.cssContextDict["mainInfo_title"]
        #cssNickName       = self.cssContextDict["mainInfo_nickname"]
        cssReplyText      = self.cssContextDict["mainInfo_content"]
        commonReplyInfoCount      = self.cssFirstLevelReplyInfoDict["replyInfo_item_count"]
        commonReplyInfoCount1     = self.cssFirstLevelReplyInfoDict["replyInfo_item_count1"]
        bestReplyInfo  = self.cssFirstLevelReplyInfoDict["best_replyInfo_item"] 
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = self.getPageUrl(crawlerInfo.url)
        replyInfo.parentContentId      = 0
        crawlerInfo.p_curPageItemNo    = 1
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        
        
        #----------------------------------------------------------------------
        #-----title 问答类平台必须有标题，可选是否有问题描述
        ret1,curText = await self.pyteerEx.getElementContext(page,cssTitle)
        if ret1 != RetVal.Suc.value:
            return RetVal.FailExit.value,replyInfo
        replyInfo.main_title = CommonTool.strStripRet(curText)

        #------------------------------------------------------------------
        #------text
        ret1,curText   = await self.pyteerEx.getElementContext(page,cssReplyText)
        replyInfo.text = CommonTool.strStripRet(curText)
         
        ret1 = self.checkStrIncludeKeyword(replyInfo.main_title,replyInfo.text,crawlerInfo.keyword)
        if ret1 != RetVal.Suc.value:
            return RetVal.FailExitNotFindKeyword.value,replyInfo

        

        #----------------------------------------------------------------------------
        #-----comments
        #-----有最佳答案
        count = 0
        ret1 = await self.pyteerEx.findElement(page,bestReplyInfo,2)
        if ret1 == RetVal.Suc.value:
            count +=1
        #-----有普通回答
        ret1,curText = await self.pyteerEx.getElementContext(page,commonReplyInfoCount)
        if ret1 == RetVal.Suc.value:
            count += CommonTool.getDigitFromString(curText.strip())
            ret = await self.pyteerEx.clickHoverElement(page,commonReplyInfoCount,self.clickDelay,self.hoverDelay)
        else:
            ret1,curText = await self.pyteerEx.getElementContext(page,commonReplyInfoCount1)
            if ret1 == RetVal.Suc.value:
                count += CommonTool.getDigitFromString(curText.strip())
        
        replyInfo.comments = count

        """ 
        #-----------------------------------------------
        #-----publisher
        ret1,curText = await self.pyteerEx.getElementContext(page,cssNickName)
        replyInfo.publisher = CommonTool.strStripRet(curText)

        #-------------------------------------------------------------------
        #-----time 
        ret1 = await self.pyteerEx.clickHoverElement(page,cssReplyTime,self.clickDelay,self.hoverDelay)
        if ret1 == RetVal.Suc.value:
            #----返回日期格式是2019-09-23
            ret1,curText   = await self.pyteerEx.getElementContext(page,cssReplyTime)
            replyInfo.publishTime = self.getReplyTime(CommonTool.strStripRet(curText))
        """

        self.printLogInfo("CrawlerSogouWenWenSub->grabQuestionInfo() : exit")

        self.printReplyInfo(replyInfo,None)
        
        return RetVal.Suc.value,replyInfo


    #---------------------------------------------------------------------------------------
    #---迭代循环抓取一级回复
    async def grabFirstLevelReplyIteration(self,elementList,crawlerInfo):

        self.printLogInfo("CrawlerSogouWenWenSub->grabFirstLevelReplyIteration() : enter")
        replyBuf     = []

        for element in elementList:
            ret,replyInfo = await self.grabFirstLevelReplyInfo(element,crawlerInfo)
            if ret != RetVal.Suc.value:
                self.printLogInfo("CrawlerSogouWenWenSub->grabFirstLevelReplyIteration() : exit")
                return RetVal.FailExit.value,replyBuf
            
            replyBuf.append(replyInfo)
            crawlerInfo.vscroll_grap_count +=1
            #---子页一级回复抓取上限 抓取数达到上限后，不再抓取后面的一级回复
            if self.terminateSubPageMaxCount == crawlerInfo.vscroll_grap_count:
                self.printLogInfo("CrawlerSogouWenWenSub->grabFirstLevelReplyIteration() : exit")
                return RetVal.FailExitCountLimit.value,replyBuf

        self.printLogInfo("CrawlerSogouWenWenSub->grabFirstLevelReplyIteration() : exit")
        return RetVal.Suc.value,replyBuf

    #----------------------------------------------------------------------------------------
    #----抓取一级回复信息
    async def grabFirstLevelReplyInfo(self,element,crawlerInfo):
        #----匿名用户
        cssNickName       = self.cssFirstLevelReplyInfoDict["replyInfo_nickname"]
        #----实名用户
        cssNickName1       = self.cssFirstLevelReplyInfoDict["replyInfo_nickname1"]
        cssReplyText      = self.cssFirstLevelReplyInfoDict["replyInfo_content"]
        cssReplyTime      = self.cssFirstLevelReplyInfoDict["replyInfo_publish_time"]
        cssReplySupport   = self.cssFirstLevelReplyInfoDict["replyInfo_reply_support"]

        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = self.getPageUrl(crawlerInfo.url)
        replyInfo.parentContentId      = 1
        crawlerInfo.p_curPageItemNo    += 1
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        
        #------------------------------------------------------------------
        #----text
        ret,curText = await self.pyteerEx.getElementContext(element,cssReplyText)
        if ret != RetVal.Suc.value:
            return RetVal.FailExit.value,None    
        replyInfo.text = CommonTool.strStripRet(curText)

        #-----------------------------------------------
        #-----publisher
        ret,curText = await self.pyteerEx.getElementContext(element,cssNickName)
        if ret != RetVal.Suc.value:
            ret,curText = await self.pyteerEx.getElementContext(element,cssNickName1)
            if ret != RetVal.Suc.value:
                return RetVal.FailExit.value,None 
        replyInfo.publisher = CommonTool.strStripRet(curText)

        #-------------------------------------------------------------------
        #-----time 返回文本是2018-12-25 回答  
        ret,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        if ret != RetVal.Suc.value:
            return RetVal.FailExit.value,None 
        replyInfo.publishTime = self.getReplyTime(CommonTool.strStripRet(curText))
        
        #-----------------------------------------------
        #-----stars
        ret,curText = await self.pyteerEx.getElementContext(element,cssReplySupport)
        if ret != RetVal.Suc.value:
            return RetVal.FailExit.value,None 
        replyInfo.stars = CommonTool.getDigitFromString(curText.strip())

        self.printReplyInfo(replyInfo,None)
        return RetVal.Suc.value,replyInfo

    #------------------------------------------------------------------------------
    #-----获取当前页数
    async def getCurPage(self,page): 
        nPage = 0
        selector = self.cssPageBtnDict["curPageText"]
        ret,curPage  = await self.pyteerEx.getElementContext(page,selector)
        if ret == RetVal.Suc.value:
            nPage  = CommonTool.getDigitFromString(curPage.strip())
        elif ret == RetVal.Fail.value:
            nPage = 1
        return nPage

    #-----------------------------------------------------------------------------
    #-----获取回复时间
    def getReplyTime(self,replyDate):
        match = re.search(r'\d{4}-\d{2}-\d{2}', replyDate)
        ret,dat = CommonTool.verifyDatetime("{} 00:00:00".format(match.group()))
        if ret:
            return dat.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ""
    
    #----------------------------------------------------------------
    #---转换url 需要更换url 则在子类重写
    """
    <meta content="always" name="referrer"><script>window.location.replace("https://wenwen.sogou.com/z/q908861067.htm")</script><noscript><META http-equiv="refresh" content="0;URL='https://wenwen.sogou.com/z/q908861067.htm'"></noscript>
    """
    def convertUrl(self,originalUrl):
        if len(originalUrl) == 0:
            return originalUrl
        try:
            url = originalUrl.replace("https://www.sogou.com","")
            response = self.httpRequest('www.sogou.com',80,url)
            if len(response) == 0:
                return originalUrl
            ret = response.split('("')
            if len(ret) != 2:
                return originalUrl
            ret = ret[1].split('")')
            return ret[0]
        except Exception:
            return originalUrl