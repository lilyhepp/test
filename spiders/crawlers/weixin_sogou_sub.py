#----------  weixin_sogou_sub.py
#---------- 微信搜狗子抓取
import sys,os
import asyncio
from pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  common.tools               import *

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class   CrawlerWeixinSogouSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        self.isUseAgent                = True

        #--调用clickHoverElement()函数时,click的延迟 
        self.clickDelay    = 0.6
        #--调用clickHoverElement()函数时,hover的延迟
        self.hoverDelay    = 0.6


        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }

        #------------------------------------------------------
        #sub
        self.cssContextDict    = {
                                  'mainInfo_title':"#img-content>h2.rich_media_title",
                                  'mainInfo_nickname':"#img-content>div.rich_media_meta_list>span.rich_media_meta_nickname>a",
                                  'mainInfo_publish_time':"#img-content>div.rich_media_meta_list>em",
                                  'mainInfo_content':"#img-content>div.rich_media_content"
                                 }
        
    
        
        #log
        logpath = "WeixinSogou/sub/" + str(index) 
        self.log_inits(logpath,1,1,logging.INFO)

    #--------------------------------------------------------------------------------------
    #----override func waitforPageLoad
    async def waitforPageLoad(self,page):      
        return RetVal.Suc.value

    
    #--------------------------------------------------------------------------------------  
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeixinSogouSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.grabAllPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerWeixinSogouSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    
    #--------------------------------------------------------------------------------------
    #子抓取--按网址抓取    
    async def  dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerWeixinSogouSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.grabAllPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerWeixinSogouSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf

    
    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def grabAllPageData(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeixinSogouSub->grabAllPageData() : enter")
    
        replyBuf     = []
        ret          = 0
   
        #------------------------main info
        ret,replyInfo = await self.grabMainInfo(page,crawlerInfo)
        if ret == RetVal.Suc.value:
            replyBuf.append(replyInfo)
        elif ret == RetVal.FailExitNotFindKeyword.value:
            return ret,[]

        self.printReplyInfo(replyInfo)
           
        if len(replyBuf) > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        
        self.printLogInfo("CrawlerWeixinSogouSub->grabAllPageData() : exit")
        return ret,replyBuf

    

    #----------------------------------------------------------------------------------------
    #----
    async def grabMainInfo(self,page,crawlerInfo):

        self.printLogInfo("CrawlerWeixinSogouSub->grabMainInfo() : enter")
        
        ret  = RetVal.Fail.value
        ret1 = RetVal.Suc.value
        
                      
        cssTitle          = self.cssContextDict["mainInfo_title"]
        cssNickName       = self.cssContextDict["mainInfo_nickname"]
        cssReplyText      = self.cssContextDict["mainInfo_content"]
        cssReplyTime      = self.cssContextDict["mainInfo_publish_time"]
        
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url
        replyInfo.parentContentId      = 0
        crawlerInfo.p_curPageItemNo    = 1
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        
        
        #----------------------------------------------------------------------
        #-----    replyInfo.main_title = 
        ret1,curText = await self.pyteerEx.getElementContext(page,cssTitle)
        replyInfo.main_title = CommonTool.strStripRet(curText)

        #------------------------------------------------------------------
        #----text
        ret1,curText   = await self.pyteerEx.getElementContext(page,cssReplyText)
        replyInfo.text = CommonTool.strStripRet(curText)
         
        result = self.checkStrIncludeKeyword(replyInfo.main_title,replyInfo.text,crawlerInfo.keyword)
        if result != RetVal.Suc.value:
            return RetVal.FailExitNotFindKeyword.value,replyInfo
         
        #-----------------------------------------------
        #-----publisher
        ret1,curText = await self.pyteerEx.getElementContext(page,cssNickName)
        replyInfo.publisher = CommonTool.strStripRet(curText)

        #-------------------------------------------------------------------
        #-----time 搜狗微信点击日期后显示出该文章发布的日期
        ret1 = await self.pyteerEx.clickHoverElement(page,cssReplyTime,self.clickDelay,self.hoverDelay)
        if ret1 == RetVal.Suc.value:
            #----返回日期格式是2019-09-23
            ret1,curText   = await self.pyteerEx.getElementContext(page,cssReplyTime)
            replyInfo.publishTime = self.getReplyTime(CommonTool.strStripRet(curText))
    

        self.printLogInfo("CrawlerWeixinSogouSub->grabMainInfo() : exit")

        self.printReplyInfo(replyInfo,None)
        
        return ret,replyInfo

    
    #----------------------------------------------------------------------------------------
    #---获取时间: 源格式:9月3日 19:30  ;目标格式:2019-09-03 19:30:00 
    def getReplyTime(self,timeText):
        
        if len(timeText) == 0:
            return "";
        ret,dat = CommonTool.verifyDatetime("{} 00:00:00".format(timeText))
        if ret:
            return dat.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ""
    
    
    
    


    