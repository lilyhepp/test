#----------  zhihu_sub.py
#-- 知乎--子抓取
import sys,os
import asyncio


from pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  common.tools               import *
import datetime

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
class CrawlerZhihuSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        self.strCurYear   = "2019"
        
        #--滚动条滚动的步长
        self.autoScrollStep  = 80
        #--调用clickHoverElement()函数时,click的延迟 
        self.clkh_click_delay    = 0.6
        #--调用clickHoverElement()函数时,hover的延迟
        self.clkh_hover_delay    = 0.6
        
        #---------------------------------------------------------
        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }

        question_entry = ""
        #sub
        self.cssContextDict    = {
                                  #----问题标题(title))
                                  'question_title':"     div.QuestionHeader-main>h1.QuestionHeader-title",
                                  #-------------------------问题回答--------------------------------
                                  #------回答
                                  'answer_item':"div.index-question-list>div.question.question-single>div.question-item>div.all-answers>div.answers>div.answer-items>div.answer-item",
                                  
                                  #------回答人名称
                                  'answer_item_nickname'       :"div.answer-user>a.answer-user-name",
                                  
                                  #------主评论pid的属性名
                                  'answer_item_pid_pro_name'   :"data-ansid",
                                  
                                  #------回答内容
                                  'answer_item_reply_text'     :"div.answer-text>div.answer-text-full>p",
                                  
                                  #------回答时间
                                  'answer_item_reply_time'     :"div.answer-user>a.answer-user-tag",
                                  
                                  #------回答收到的支持数或是点赞数
                                  'answer_item_reply_support'  :"div.answer-text>div.answer-tool>div.comment-tool>a.answer-like-count>span.like-num",
                                  
                                  #------回答里的图片
                                  'answer_item_p_img'          :"img",
                                  
                                  #---------------------------评论回复-------------------------------
                                  #------评论回复按钮
                                  'comment_flag'               :"div.answer-text>div.answer-tool>div.comment-tool>a.show-comment",
                                  
                                  #------评论回复加载更多
                                  'comment_load_more'          :"div.comment-container>div>div.comment-widget>div.load",
                                  
                                  #------评论回复项
                                  'comment_content'            :"div.comment-container>div>div.comment-widget>ul.comment-list>li",
                                  
                                  #------评论人名称
                                  'comment_content_name'      :"div.comment-content>a.uname",
                                  
                                  #-----评论人id属性
                                  'comment_content_pid_pro_name'   :'href',
                                  
                                  #------评论回复内容
                                  'comment_content_text'       :"div.comment-content>div.content-text",
                                  
                                  #------评论时间
                                  'comment_content_reply_time'     :"div.comment-content>div.tools>span",
                                  
                                  #------评论收到的支持数或是点赞数
                                  'comment_content_reply_support'  :"div.comment-content>div.digg-box>a.digg>span",
                                 
                                  'question_name':"div.index-question-list>div.question>div.question-item>h1.question-name>span"
                                 }
        

        
        #log
        logpath = "zhihu/sub/" + str(index) 
        self.log_inits(logpath,1,1,logging.INFO)

    
    #--------------------------------------------------------------------------------------  
    #----override func login  
    async def login(self,page):
       return RetVal.Suc.value
   
   
    #--------------------------------------------------------------------------------------
    #---override func waitforPageLoad
    async def  waitforPageLoad(self,page):
        return RetVal.Suc.value
    
    #-----------------------------------------------------------------------------------------
    #----滚动页面,不需要滚动
    async def autoScrollAsVScroll(self,page,crawlerInfo):
        crawlerInfo.finish_status =  RetVal.GrapSuc.value
        return  RetVal.Suc.value

    #--------------------------------------------------------------------------------------  
    #------子抓取--按楼层抓取
    async def dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerZhihuSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.grabPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerZhihuSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
  
    #--------------------------------------------------------------------------------------
    #-----子抓取--按网址抓取    
    async def dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerZhihuSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.grabPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerZhihuSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    
    
    #----------------------------------------------------------------------------------------
    #---抓取第一条口碑信息:title作为第一条 
    #---
    #---
    async def grapFirstReplyInfo(self,page,crawlerInfo):
        
        self.printLogInfo("CrawlerToutiaoSub->grapFirstReplyInfo() : enter")

        ret = RetVal.Suc.value

        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        crawlerInfo.p_parentPageItemNo = 0
        replyInfo.parentContentId = crawlerInfo.p_parentPageItemNo
        crawlerInfo.p_curPageItemNo = 1
        replyInfo.contentId       = crawlerInfo.p_curPageItemNo
        
        #---title
        selector    = self.cssContextDict["mainInfo_title"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        curText     =  CommonTool.strStripRet(curText)
        replyInfo.main_title   = curText
        crawlerInfo.main_title = curText

        #---publisher
        
        selector    = self.cssContextDict["mainInfo_nickname"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        replyInfo.publisher = CommonTool.strStripRet(curText)
        

        #---time
        selector    =  self.cssContextDict["mainInfo_time"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        curText     =   CommonTool.strStripRet(curText);
        replyInfo.publishTime =  curText
        
        #----context
        selector    = self.cssContextDict["mainInfo_text_entry"]
        curText     = ""
        ret,elementList = await  self.pyteerEx.getElementAll(page,selector)
        for item in elementList:
            ret1,curText1 = await self.pyteerEx.getElementContext(item)
            curText1 =  CommonTool.strStripRet(curText1)
            if curText1:
                curText += curText1
        
        
        #----pic
        selector    = self.cssContextDict["mainInfo_pic_entry"]
        proName     = self.cssContextDict["mainInfo_pic_name"] 
        ret,elementList = await  self.pyteerEx.getElementAll(page,selector)
        for item in elementList:
            ret1,curText1 = await self.pyteerEx.getElementProDef(page,item,proName)
            curText1 =  CommonTool.strStripRet(curText1)
            
            if curText1:
                curText += GrapReplyInfo.getPicWrapStr(curText1)
        
        replyInfo.text = curText
        self.printLogInfo("CrawlerToutiaoSub->grapMainInfo() : exit")
        

        return ret,replyInfo
    #-----------------------------------------------------------------------------------------------
    #-----抓取问题回复和评论回复
    async def grabPageData(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerZhihuSub->grabPageData() : enter")
    
        questionReplyBuf = []
        commentBuf= []
        ret          = 0
        
        #-------------------------------------------------------------------------------------------
        #-----获取问题题目作为title
        ret,curText = await self.pyteerEx.getElementContext(page,self.cssContextDict["question_name"]);
        if ret == RetVal.Suc.value:
            crawlerInfo.main_title = curText.strip()
        
        
        #-----获取问题回复
        selector = self.cssContextDict["answer_item"]
        ret,elementList = await self.pyteerEx.getElementAll(page,selector) #---elementList 问题回复列表
        if ret != RetVal.Suc.value:
            return ret,questionReplyBuf
        
        for item in elementList:
            ret1,replyInfo = await self.grabQuestionReplyInfo(page,item,crawlerInfo)
            if ret1 != RetVal.Suc.value:
                continue
        
            #-----先确认是否有评论回复
            #-----展开评论回复
            ret1 = await self.pyteerEx.clickHoverElement(item,self.cssContextDict["comment_flag"],self.clkh_click_delay,self.clkh_hover_delay)
            if ret1 != RetVal.Suc.value:
                questionReplyBuf.append(replyInfo)
                self.printReplyInfo(replyInfo)
                continue
                     
            ret1 = await self.clickMoreComment(item,self.cssContextDict["comment_load_more"]) #--加载所有的评论回复
            
            #-----获取评论回复
            ret1,commentItemList = await self.pyteerEx.getElementAll(item,self.cssContextDict["comment_content"])
            if ret1 != RetVal.Suc.value:
                questionReplyBuf.append(replyInfo)
                self.printReplyInfo(replyInfo)
                continue            
            
            replyInfo.comments = len(commentItemList) #-----获取当前问题回复的评论回复
            questionReplyBuf.append(replyInfo) 
            self.printReplyInfo(replyInfo)
            
            crawlerInfo.p_parentPageItemNoSub = crawlerInfo.p_curPageItemNo
            crawlerInfo.pid = replyInfo.pid
            for element in commentItemList:
                ret1,commentReplyInfo = await self.grabCommentReplyInfo(page,element,crawlerInfo)
                if ret1 != RetVal.Suc.value:
                    continue
                commentBuf.append(commentReplyInfo)
                self.printReplyInfo(commentReplyInfo)

        #-----合并问题回复和评论回复并返回
        questionReplyBuf.extend(commentBuf)
        if len(questionReplyBuf) > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value    
        
        self.printLogInfo("CrawlerZhihuSub->grabPageData() : exit")
        return ret,questionReplyBuf

    
    #----------------------------------------------------------------------------------------
    #---加载所有评论回复
    async def clickMoreComment(self,element,selector):
        self.printLogInfo("CrawlerZhihuSub->clickMoreComment() : enter")
        while True:
            ret,targetElement = await self.pyteerEx.getElement(element,selector)
            if ret != RetVal.Suc.value:
               self.printLogInfo("CrawlerZhihuSub->clickMoreComment() : leave")
               break
            ret = await self.pyteerEx.clickHoverElement(element,selector,self.clkh_click_delay,self.clkh_hover_delay)
            if ret != RetVal.Suc.value:
               self.printLogInfo("CrawlerZhihuSub->clickMoreComment() : leave")
               break
            
        return RetVal.Suc.value
    
    #----------------------------------------------------------------------------------------
    #---抓取问题回答
    async def grabQuestionReplyInfo(self,page,element,crawlerInfo):

        self.printLogInfo("CrawlerWukongSub->grabQuestionReplyInfo() : enter")
        
        ret  = RetVal.Fail.value
        
        cssNickName       = self.cssContextDict["answer_item_nickname"]
        replyPidName      = self.cssContextDict["answer_item_pid_pro_name"]
        cssReplyText      = self.cssContextDict["answer_item_reply_text"]
        cssReplyTime      = self.cssContextDict["answer_item_reply_time"]
        cssReplySupport   = self.cssContextDict["answer_item_reply_support"]
        
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href    = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        replyInfo.parentContentId      = 0
        crawlerInfo.p_curPageItemNo    += 1 
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        #-----------------------------------------------
        #--publisher
        ret,curText = await self.pyteerEx.getElementContext(element,cssNickName)
        if ret == RetVal.Suc.value:
            replyInfo.publisher = CommonTool.strSplitIndex(curText.strip(),"\n",0)
   

        #--pid property 
        ret,curText = await self.pyteerEx.getElementProDef(page,element,replyPidName,"")
        curText      = curText.strip()
        replyInfo.pid = curText
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(curText,"")
  
        #---时间 格式 01-07 22:37
        ret,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        replyInfo.publishTime = self.generateReplyTime(curText)
            
        #--支持或者点赞数
        ret,curText   = await self.pyteerEx.getElementContext(element,cssReplySupport)
        replyInfo.stars = CommonTool.strToInt(curText)
            
        #---回答内容 多个p标签 里面既有文本值 也有图片
        ret,elementList = await self.pyteerEx.getElementAll(element,cssReplyText)
        replyInfo.text = await self.generateReplyContent(page,elementList)

        #---------------------------------------------------
        
        self.printLogInfo("CrawlerWukongSub->grabQuestionReplyInfo() : exit")
        return RetVal.Suc.value,replyInfo
    
    
    #----------------------------------------------------------------------------------------
    #---抓取评论回复
    async def grabCommentReplyInfo(self,page,element,crawlerInfo):
        self.printLogInfo("CrawlerWukongSub->grabCommentReplyInfo() : enter")
        
        cssNickName       = self.cssContextDict["comment_content_name"]
        replyPidName      = self.cssContextDict["comment_content_pid_pro_name"]
        cssReplyText      = self.cssContextDict["comment_content_text"]
        cssReplyTime      = self.cssContextDict["comment_content_reply_time"]
        cssReplySupport   = self.cssContextDict["comment_content_reply_support"]
        
        
        replyInfo         = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href    = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        replyInfo.parentContentId      = crawlerInfo.p_parentPageItemNoSub
        crawlerInfo.p_curPageItemNo    += 1 
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        
        #-----------------------------------------------
        #--publisher
        ret,curText = await self.pyteerEx.getElementContext(element,cssNickName)
        replyInfo.publisher = CommonTool.strStripRet(curText)

        #--pid property <a href="/user/?uid=2860541453" target="_blank" class="uname">
        ret,curText = await self.pyteerEx.getElementProDef(page,element,replyPidName,cssNickName)
        curText      = curText.strip().replace("/user/?uid=","")
        replyInfo.pid = curText
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(crawlerInfo.pid,curText)

        #---评论内容 
        ret,curText = await self.pyteerEx.getElementContext(element,cssReplyText)
        replyInfo.text = curText.strip()

        #---时间 格式 01-07 22:37
        ret,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        replyInfo.publishTime = self.generateReplyTime(curText)
            
        #--支持或者点赞数
        ret,curText   = await self.pyteerEx.getElementContext(element,cssReplySupport)
        replyInfo.stars = CommonTool.strToInt(curText)
            
        #---------------------------------------------------
        
        self.printLogInfo("CrawlerWukongSub->grabCommentReplyInfo() : exit")
        return RetVal.Suc.value,replyInfo
    
    
    #--------------------------------------------------------------------------
    #-----生成问题回答文本 
    async def generateReplyContent(self,page,elementList):
        if len(elementList) == 0:
            return ""
        replyContent = ""
        for item in elementList:
            ret,curText = await self.pyteerEx.getElementContext(item) #---获取p标签内文本信息
            if ret == RetVal.Suc.value and len(curText) > 0:
                replyContent += "{}{}".format(curText.strip(),"\n")
            
            #------- 获取p标签下的img标签    
            ret,imgElement = await self.pyteerEx.getElement(item, self.cssContextDict["answer_item_p_img"])
            if ret != RetVal.Suc.value:
                continue 
            
            ret,curText =  await self.pyteerEx.getElementProDef(page,imgElement,"src")
            if ret == RetVal.Suc.value and len(curText) > 0:
                replyContent +="{}{}".format(GrapReplyInfo.getPicWrapStr(curText),"\n") 
        return replyContent        
                
    #------------------------------------------------------------------------------------------------
    #---wukong platform has no Paging           
    async def dealSubGotoNextPage(self,page,curGrapNum,maxPageNum):     
        return RetVal.GrapSuc.value,""
    
    #-------------------------------------------------------------------------------------------------
    #---根据回复时间生成标准格式时间 原数据 01-07 22:37 目标格式 2019-01-01 12:00:00
    def generateReplyTime(self,curDateText):
        if len(curDateText) > 0:
            strDatetime = "{}-{}:{}".format(self.strCurYear,curDateText,"00")
            result = self.verifyDate(strDatetime)
            if result == True:
                return strDatetime
            else:
                return "";
        return "";
            
            
    #------------------------------------------------------------------------------------------------
    #---验证传入的字符串是否是有效时间格式 
    def verifyDate(self,datetime_str):
        try:        
    	    datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')        
    	    return True    
        except ValueError:        
    	    return False 

            
        
        


    