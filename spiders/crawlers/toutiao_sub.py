#----------  toutiao_sub.py
#-- 头条--子抓取
import sys,os
import asyncio
import  datetime
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
class   CrawlerToutiaoSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80

        """
        #---------------------------------------------------------
        #----other
        self.cssPageBtnDict = {
                               'tailPageText':"",
                               'firstPageBtn':"",
                               'prePageBtn'  :"",
                               
                               'curPageText':"",
                               'curPageBtn' :"",
                               
                               'nextPageBtn':"",
                               'bottomAllPageNum':""
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        """
        #------------------------------------------------------
        #
        mainInfo_entry    = "div.bui-left.index-middle>div.article-box>"
        main_reply_entry  = "div.bui-left.index-middle>div.detail-comment>div#comment>"
        #sub
        self.cssContextDict    = {
                                  
                                  'mainInfo_nickname':mainInfo_entry + "div.article-sub>span:first-child",
                                  'mainInfo_time'    :mainInfo_entry + "div.article-sub>span:nth-last-child(1)",
                                  'mainInfo_title'   :mainInfo_entry + "h1.article-title",
                                  #文本
                                  'mainInfo_text_entry': mainInfo_entry + "div.article-content>div>p",
                                  #图片
                                  'mainInfo_pic_name'  : "src",
                                  'mainInfo_pic_entry':  mainInfo_entry + "div.article-content>div>div.pgc-img>img",
                                  
                                  #---查看更多按钮
                                  'main_reply_btn_more':main_reply_entry + "a.c-load-more ",
                                  
                                  #---评论回复数量
                                  'main_reply_count':"div.bui-left>div.share-box>a.share-count>span",

                                  #--------------------------------------------------------------------------------------
                                  #---主评论
                                  
                                  #---主评论根目录
                                  'main_reply_entry'    : main_reply_entry +"ul>li.c-item>div.c-content",
                                  #---nickname
                                  'main_reply_nickname' :"div.c-user-info>a.c-user-name",
                                  #---time
                                  'main_reply_time'     :"div.c-user-info>span.c-create-time",
                                  #---pid
                                  'main_reply_pid'      :"div.c-user-info>a.c-user-name",
                                  
                                  #---text,查找多个p
                                  'main_reply_text'     :"p",
                                  #--子回复数  -> ⋅ 21条回复
                                  'main_reply_sub_num'    :"div.c-footer-action>span.c-reply-count",
                                  #---子回复按钮
                                  'main_reply_sub_num_btn':"div.c-footer-action>span.c-reply-count",
                                  #---点赞  ->  13 
                                  'main_reply_support'    :"div.c-footer-action>span.bui-right.c-digg",
                                
                                  #------------------------------------------------------------------------------------
                                  #----子评论
                                  #---共n条子回复按钮
                                  'sub_reply_btn_more': "a.c-load-more",
                                  #----子评论根目录
                                  'sub_reply_entry':    "div.c-reply-comment>div.c-content",
                                  
                                  #----子评论的pid--直接取用户名的href地址-取出id号href="/c/user/69533839235/"
                                  'sub_reply_pid':      "div.c-user-info>a.c-user-name",
                                
                                  #----nickname
                                  'sub_reply_nickname': "div.c-user-info>a.c-user-name",
                                  #----time 格式:3月前
                                  'sub_reply_time':     "div.c-user-info>span.c-create-time",

                                  #----text,取多个p的值
                                  'sub_reply_text':     "p",
                                  
                                  #-------点赞
                                  'sub_reply_support':  "div.c-footer-action>span.bui-right.c-digg",
                                
                                  
                                 }
        
        self.cssLoginDict      ={
                                 'user_name':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-userName >input.pass-text-input.pass-text-input-userName",
                                 'password' :"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-password >input.pass-text-input.pass-text-input-password",
                                 'clk_button':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-submit >input.pass-button.pass-button-submit",
                                 'pageLoginExit':"body.skin_normal>div#passport-login-pop > div.tang-foreground > div.tang-title.tang-title-dragable>div.buttons>a.close-btn "
                                 }
        
        #log
        logpath = "toutiao/sub/" + str(index) 
        self.log_inits(logpath,2,2,logging.INFO)
    

    #----------------------------------------------------------------------------------------
    #--抓取所有回复的信息
    async def grapAllReplyInfo(self,page,crawlerInfo,strTimeYear):

        self.printLogInfo("CrawlerToutiaoSub->grapAllReplyInfo() : enter")
        
        ret = RetVal.Fail.value
        replyBuf  = []
        replyBuf1 = []
        #---------------------------main reply info
        #--click more
        selector  = self.cssContextDict["main_reply_btn_more"]
        ret1 = await self.clickButtonMore(page,selector)

        #-----main info
        selector           = self.cssContextDict["main_reply_entry"]
        ret1,elementList   = await self.pyteerEx.getElementAll(page,selector)

        for item in elementList:
            #----main reply
            crawlerInfo.p_parentPageItemNo = 1
            crawlerInfo.pid                = ""
            ret1,replyInfo = await self.grapItemMainReplyInfo(page,item,crawlerInfo,strTimeYear)
            if ret1 == RetVal.Suc.value:
                replyBuf.append(replyInfo)
                crawlerInfo.pid = replyInfo.pid
                self.printReplyInfo(replyInfo,crawlerInfo)
               
                #判断已抓取的数量是否超过最大抓取数
                crawlerInfo.vscroll_grap_count +=1
                
                if crawlerInfo.vscroll_grap_count >= self.terminateSubPageMaxCount:
                    ret1 = RetVal.FailExitCountLimit.value
                    return ret1, replyBuf
                
                #判断小说
                ret1 = self.IsTerminateGrapAsNovel(crawlerInfo,replyInfo.text)
                if ret1 == RetVal.FailExitAsNovel.value:
                    return ret1, replyBuf
                #----   
                #----sub reply
                """
                if replyInfo.comments > 0:
                   crawlerInfo.p_parentPageItemNoSub = crawlerInfo.p_curPageItemNo
                   ret1,replyBuf1 = await self.grapSubReplyInfo(page,item,crawlerInfo,strTimeYear)
                   if ret1 == RetVal.Suc.value:
                       replyBuf.extend(replyBuf1)
                       self.printReplyInfoBuf(replyBuf1,crawlerInfo)
                """
        #-----------------end for

        if len(replyBuf) > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        
        return ret,replyBuf
        
    #----------------------------------------------------------------------------------------
    #---抓取主信息
    #---时间-是title属性,格式：2019-09-03 19:30,需要手动加00
    #---文本为图片->先抓有多个图片的，没有则抓单个图片的
    async def grapMainInfo(self,page,crawlerInfo):
        
        self.printLogInfo("CrawlerToutiaoSub->grapMainInfo() : enter")

        result         = RetVal.FailExit.value
        loopBreak      = 0

        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = self.getPageUrl(crawlerInfo.url)  

        crawlerInfo.p_parentPageItemNo = 0
        replyInfo.parentContentId = crawlerInfo.p_parentPageItemNo
        crawlerInfo.p_curPageItemNo = 1
        replyInfo.contentId       = crawlerInfo.p_curPageItemNo
        
        curLoop = 1
        while curLoop > 0:
            curLoop -= 1    
            #---title
            selector    = self.cssContextDict["mainInfo_title"]
            ret,curText =  await self.pyteerEx.getElementContext(page,selector)
            curText     =  CommonTool.strStripRet(curText)
            #---判断标题是否正确
            if (ret ==RetVal.Suc.value) and (len(curText) > 0) :
                replyInfo.main_title   = curText
                crawlerInfo.main_title = curText
            else:
                break
        
            #----context
            selector    = self.cssContextDict["mainInfo_text_entry"]
            curText     = ""
            ret,elementList = await  self.pyteerEx.getElementAll(page,selector)

            for item in elementList:
                ret1,curText1 = await self.pyteerEx.getElementContext(item)
                if ret1 == RetVal.Suc.value:
                    curText1 =  CommonTool.strStripRet(curText1)
                    if curText1:
                        curText += curText1
                else: #出错
                    loopBreak = 1
                    break
            #---
            if loopBreak == 1:
                break
                
            #----pic
            selector    = self.cssContextDict["mainInfo_pic_entry"]
            proName     = self.cssContextDict["mainInfo_pic_name"] 
            ret,elementList = await  self.pyteerEx.getElementAll(page,selector)

            for item in elementList:
                ret1,curText1 = await self.pyteerEx.getElementProDef(page,item,proName)
                if ret1 == RetVal.Suc.value:
                    curText1 =  CommonTool.strStripRet(curText1)
                    if curText1:
                        curText += GrapReplyInfo.getPicWrapStr(curText1)
                else: #出错
                    loopBreak = 1
                    break
            #----    
            if loopBreak == 1:
                break
                  
            if len(curText) > 0:
                replyInfo.text = curText
            else:
                break
        
            #----判断文章title和内容是否包含关键词
            ret = self.checkStrIncludeKeyword(crawlerInfo.main_title,replyInfo.text,crawlerInfo.keyword)
            if ret != RetVal.Suc.value:
                result = RetVal.FailExitNotFindKeyword.value
                break

            #---publisher
        
            selector    = self.cssContextDict["mainInfo_nickname"]
            ret,curText =  await self.pyteerEx.getElementContext(page,selector)
            curText     = CommonTool.strStripRet(curText)
            if (ret == RetVal.Suc.value) and (len(curText) > 0):
                replyInfo.publisher = curText
            else:
                break
    
            #---time
            selector    =  self.cssContextDict["mainInfo_time"]
            ret,curText =  await self.pyteerEx.getElementContext(page,selector)
            curText     =   CommonTool.strStripRet(curText);
            if (ret == RetVal.Suc.value) and (len(curText) > 0):
                replyInfo.publishTime =  curText
            else:
                break
        
            #---comments
            ret,curtext = await self.pyteerEx.getElementContext(page,self.cssContextDict["main_reply_count"])
            if ret == RetVal.Suc.value:
                replyInfo.comments = CommonTool.getDigitFromString(curtext.strip())
            else:
                break
            #------------
            result = RetVal.Suc.value
        #---------------------------------------end while
        
        self.printLogInfo("CrawlerToutiaoSub->grapMainInfo() : exit")
        
        return result,replyInfo

    #--------------------------------------------------------------------------------------
    async def  waitforPageLoad(self,page):
        return RetVal.Suc.value
    #-----------------------------------------------------------------------------------------
    # 滚动页面,不需要滚动
    async def autoScrollAsVScroll(self,page,crawlerInfo):
        crawlerInfo.finish_status =  RetVal.GrapSuc.value
        return  RetVal.Suc.value
    
    #--------------------------------------------------------------------------------------  
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerToutiaoSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.dealCompoundwordCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerToutiaoSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    #--------------------------------------------------------------------------------------
    #子抓取--按网址抓取    
    async def  dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerToutiaoSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.dealDefUrlCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerToutiaoSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf

    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def dealDefUrlCrawlerPage(self,page,crawlerInfo,index):
        self.printLogInfo("CrawlerToutiaoSub->dealDefUrlCrawlerPage() : enter")
        
        replyBuf = []
        ret,replyBuf = await self.grapAllPageData(page,crawlerInfo,index)
        
        self.printLogInfo("CrawlerToutiaoSub->dealDefUrlCrawlerPage() : exit")
        return ret,replyBuf

    #--------------------------------------------------------------------------------------
    #----按关键字抓取
    async def  dealCompoundwordCrawlerPage(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerToutiaoSub->dealCompoundwordCrawlerPage() : enter")

        replyBuf = []
        ret,replyBuf = await self.grapAllPageData(page,crawlerInfo,index)
        
        self.printLogInfo("CrawlerToutiaoSub->dealCompoundwordCrawlerPage() : exit")
        
        return ret,replyBuf
    
    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def grapAllPageData(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerToutiaoSub->grapAllPageData() : enter")
    
        replyBuf = []
        replyBuf1= []
        replyBuf2= []
        
        
        strCurTime   = "" 
        ret          = 0
        itemCount    = 0
    
        #---------------------------main info
        ret,replyInfo = await self.grapMainInfo(page,crawlerInfo)
        if ret == RetVal.Suc.value:
            replyBuf.append(replyInfo)
        elif ret == RetVal.FailExit.value:  #--标题为空
            return ret,[]
        elif ret == RetVal.FailExitNotFindKeyword.value: #----若title和内容都没有关键词 则直接退出本次关键词抓取
            return ret,[]
            
        self.printReplyInfo(replyInfo,crawlerInfo)

        #---暂时注释抓取子回复
        #--grap sub info
        """
        ret,replyBuf1 = await self.grapAllReplyInfo(page,crawlerInfo,strCurTime)
        if len(replyBuf1 ) > 0:
            replyBuf.extend(replyBuf1)
        
        self.printLogInfo("CrawlerToutiaoSub->grapAllPageData() : exit")
        """
        return ret,replyBuf
         
    #----------------------------------------------------------------------------------------
    #---抓取主回复的子回复
    async def grapSubReplyInfo(self,page,element,crawlerInfo,strTimeYear):

        self.printLogInfo("CrawlerToutiaoSub->grapSubReplyInfo() : enter")  

        ret  = RetVal.Fail.value
        replyBuf  = []

        #---click 评论数
        selector  = self.cssContextDict["main_reply_sub_num_btn"]
        ret       = await self.pyteerEx.clickHoverElement(element,selector,0.5,0.5)
        
        #---click more
        selector  = self.cssContextDict["sub_reply_btn_more"]
        ret1 = await self.clickButtonMore(element,selector)
        
        #---all sub
        selector          = self.cssContextDict["sub_reply_entry"]
        
        ret,elementList   = await self.pyteerEx.getElementAll(element,selector)
       
        
        for item in elementList:
            ret1,replyInfo = await self.grapItemSubReplyInfo(page,item,crawlerInfo,strTimeYear)
            if ret1 == RetVal.Suc.value:
                replyBuf.append(replyInfo)
        
        #---------
        if len(replyBuf) > 0:
            ret = RetVal.Suc.value
        
        self.printLogInfo("CrawlerToutiaoSub->grapSubReplyInfo() : exit")    
        
        return ret,replyBuf
    #----------------------------------------------------------------------------------------
    #---抓取主回复的子回复
    async def grapItemSubReplyInfo(self,page,element,crawlerInfo,strTimeYear):
        self.printLogInfo("CrawlerToutiaoSub->grapMainReplyInfo() : enter")
        
        ret  = RetVal.Suc.value
        ret1 = RetVal.Suc.value
        
        cssNickName       = self.cssContextDict["sub_reply_nickname"]
        cssReplyPid       = self.cssContextDict["sub_reply_pid"]
        cssReplyText      = self.cssContextDict["sub_reply_text"]
        cssReplyTime      = self.cssContextDict["sub_reply_time"]
        cssReplySupport   = self.cssContextDict["sub_reply_support"]
        
        
        replyInfo         = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href    = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        
        replyInfo.parentContentId      = crawlerInfo.p_parentPageItemNoSub
        crawlerInfo.p_curPageItemNo    += 1
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        #-----------------------------------------------
        #--publisher
        ret1,curText = await self.pyteerEx.getElementContext(element,cssNickName)
        replyInfo.publisher = CommonTool.strStripRet(curText)

        #--pid href
        ret1,curText = await self.pyteerEx.getElementHref(element,cssReplyPid)
        curText       =  curText.strip()
        curText1      =  CommonTool.getDigitFromString(curText)
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(crawlerInfo.pid,curText1)

        #---text
        curText = ""
        ret1,elementList = await self.pyteerEx.getElementAll(element,cssReplyText)
        for item in elementList:
            ret1,curText1   = await self.pyteerEx.getElementContext(item)
            curText += CommonTool.strStripRet(curText1)

        replyInfo.text = curText
        
        #---time 格式: 4月前
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        replyInfo.publishTime = self.getReplyTime(curText,strTimeYear)
               
        #--start
        ret1,curText    = await self.pyteerEx.getElementContext(element,cssReplySupport)
        replyInfo.stars = CommonTool.getDigitFromString(curText)
            
        #---------------------------------------------------
        
        self.printLogInfo("CrawlerToutiaoSub->grapMainReplyInfo() : exit")
        self.printReplyInfo(replyInfo,crawlerInfo)
        
        return ret,replyInfo    


    #----------------------------------------------------------------------------------------
    #---抓取主回复
    async def grapItemMainReplyInfo(self,page,element,crawlerInfo,strTimeYear):

        self.printLogInfo("CrawlerToutiaoSub->grapMainReplyInfo() : enter")
        
        ret  = RetVal.Suc.value
        ret1 = RetVal.Suc.value
        
        cssNickName       = self.cssContextDict["main_reply_nickname"]
        cssReplyPid       = self.cssContextDict["main_reply_pid"]
        cssReplyText      = self.cssContextDict["main_reply_text"]
        cssReplyTime      = self.cssContextDict["main_reply_time"]
        cssReplySupport   = self.cssContextDict["main_reply_support"]
        cssReplyNum       = self.cssContextDict["main_reply_sub_num"]
        
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        replyInfo.parentContentId      = crawlerInfo.p_parentPageItemNo
        crawlerInfo.p_curPageItemNo    += 1
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        #-----------------------------------------------
        #--publisher
        ret1,curText = await self.pyteerEx.getElementContext(element,cssNickName)
        replyInfo.publisher = CommonTool.strStripRet(curText)

        #--pid href
        ret1,curText = await self.pyteerEx.getElementHref(element,cssReplyPid)
        curText       =  curText.strip()
        replyInfo.pid =  CommonTool.getDigitFromString(curText)
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(replyInfo.pid,"")
        
        #---text
        curText = ""
        ret1,elementList = await self.pyteerEx.getElementAll(element,cssReplyText)
        for item in elementList:
            ret1,curText1   = await self.pyteerEx.getElementContext(item)
            curText += CommonTool.strStripRet(curText1)

        replyInfo.text = curText

        #---time 格式:3月前
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        replyInfo.publishTime = self.getReplyTime(curText,strTimeYear)
        
       
            
        #--support
        ret1,curText    = await self.pyteerEx.getElementContext(element,cssReplySupport)
        replyInfo.stars = CommonTool.getDigitFromString(curText)
        
        #--reply num
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyNum)
        self.printLogInfo("CrawlerToutiaoSub->grapMainReplyInfo() : exit")
        replyInfo.comments = CommonTool.getDigitFromString(curText) 
        
        #---------------------------------------------------
        
        self.printLogInfo("CrawlerToutiaoSub->grapMainReplyInfo() : exit")

        return ret,replyInfo

    
    #----------------------------------------------------------------------------------------
    #---获取回复文本: publisher和回复文本是一起抓取的,去掉publisher
    def getReplyTextAsSplit(self,grapText):

        replyText = ""
        splitBuf = ["：",":"]
        
        for item in splitBuf:
            textList = CommonTool.strSplit(grapText,item)
            
            if len(textList) > 1:
                textList.pop(0)
                
                for item in textList:
                    replyText += item.strip()
                    

                break
        
        return replyText
    
    #----------------------------------------------------------------------------------------
    def getTimeType(self,timeText):
        
        timeType = 0

        if timeText.find(u"年") != -1:
            timeType = 1
        elif timeText.find(u"月") != -1:
            timeType = 2
        elif timeText.find(u"天") != -1:
            timeType = 3
        elif timeText.find(u"时") != -1:
            timeType = 4
        elif timeText.find(u"分") != -1:
            timeType = 5
        elif timeText.find(u"秒") != -1:
            timeType = 6

        return timeType
    
    #----------------------------------------------------------------------------------------
    #---获取时间: 源格式:1年前,4月前,1天前,1小时前，1分钟前,1秒之前  ;目标格式:2019-09-03 19:30:00 
    def getReplyTime(self,timeText,strTimeDefault):
        
        strTime    = ""
        replyTime  = None
        curTime    = datetime.datetime.now()
        nVal       = CommonTool.getDigitFromString(timeText)
        

        timeType   = self.getTimeType(timeText)
        self.printLogInfo("CrawlerToutiaoSub->getReplyTime() : timeText={} timeType={} nval={}".format(timeText,timeType,nVal))
        try:
            if timeType   == 1: #年
                replyTime = datetime.datetime(curTime.year-nVal,curTime.month,curTime.day,curTime.hour,curTime.minute,curTime.second )
            elif timeType == 2: #月
                nAllMonth = (curTime.year *12) + curTime.month 
                nAllMonth -= nVal
                nYear     = nAllMonth // 12
                nMonth    = nAllMonth %12
                if nMonth == 0:
                   nMonth = 1
                
                replyTime = datetime.datetime(nYear,nMonth,curTime.day,curTime.hour,curTime.minute,curTime.second ) 
                
            elif timeType == 3: #日
                replyTime = curTime - datetime.timedelta(days=nVal )
            elif timeType == 4: #时
                replyTime = curTime - datetime.timedelta(hours=nVal )
            elif timeType == 5: #分
                replyTime = curTime - datetime.timedelta(minutes=nVal )
            elif timeType == 6: #秒
                replyTime = curTime - datetime.timedelta(seconds=nVal )
            else:               #默认
                replyTime = curTime
            #------------
            strTime =  replyTime.strftime("%Y-%m-%d %H:%M:%S")
        
        except Exception:
            self.printLogInfo("CrawlerToutiaoSub->getReplyTime() : exception")
            strTime = curTime.strftime("%Y-%m-%d %H:%M:%S")
        
        return strTime

    #----------------------------------------------------------------------------------------
    #---点查看更多按钮
    async def clickButtonMore(self,page,selector):

        self.printLogInfo("CrawlerToutiaoSub->clickButtonMore() : enter")

        ret = RetVal.Suc.value
        #selector  = self.cssContextDict["main_reply_btn_more"]

        count = 2000
        while count > 0:
            count -= 1

            ret = await self.pyteerEx.clickHoverElement(page,selector,0.5,0.5)
            if ret == RetVal.Suc.value:
                self.printLogInfo("CrawlerToutiaoSub->clickButtonMore() : find more button")
                continue
            else:
                break
        
        ret = RetVal.Suc.value
        
        self.printLogInfo("CrawlerToutiaoSub->clickButtonMore() : exit")

        return ret

    """
    #--------------------------------------------------------------------------------------
    # goto to next page
    # return:
    #   isFinish   = 0：继续抓取下一页
    #   isFinish   = 1: 完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开下一页
    #   isFinish   = 3: 抓取失败，退出      
    async def  dealSubGotoNextPage(self,page,pageNo,maxPageNum):
        isFinish   = RetVal.GrapSuc.value
        url_next    = ""
        return isFinish,url_next    
    """
    

    #--------------------------------------------------------------------------------------
    #
    async def dealMainScrollBefor(self,page,crawlerInfo):
        
        ret    = RetVal.FailExit.value
        strUrl = page.target.url
        strBuf = CommonTool.strSplit(strUrl,"www.toutiao.com" )
        if len(strBuf ) > 1:
            ret = RetVal.Suc.value
        
        """
        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : enter")
        
        cssList  = []
        selector = self.cssSearchDict["inputBox"]
        cssList.append(selector)
        selector = self.cssSearchDict["inputBox1"]
        cssList.append(selector)
        
        ret = await self.pyteerEx.waitPageAll(page,cssList,10)

        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : exit ret={}".format(ret))
        """
        return ret
    
    
    
    
    
    
    


    