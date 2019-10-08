#----------  wukong_sub.py
#---------- 悟空问答--子抓取
#---------- 问题 问题回答 回答评论


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
class CrawlerWukongSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        self.strCurYear   = "2019"
        
        
        #--滚动条滚动的步长
        self.autoScrollStep  = 80
        #--调用clickHoverElement()函数时,click的延迟 
        self.clickDelay    = 0.6
        #--调用clickHoverElement()函数时,hover的延迟
        self.hoverDelay    = 0.6
        
        #---------------------------------------------------------
        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }

      
        #sub
        self.cssContextDict    = {
                                  
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
                                 
                                  #------问题名称
                                  'question_name':"div.index-question-list>div.question>div.question-item>h1.question-name>span",
                                 
                                  #------问题内容
                                  'question_text':"div.index-question-list>div.question>div.question-item>div.question-text",
                                 }
        

        
        #log
        logpath = "wukong/sub/" + str(index) 
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
    #----滚动页面,子页内所有回复已加载，暂时不需要滚动
    async def autoScrollAsVScroll(self,page,crawlerInfo):
        crawlerInfo.finish_status =  RetVal.GrapSuc.value
        return  RetVal.Suc.value

    #--------------------------------------------------------------------------------------  
    #------子抓取--按楼层抓取
    async def dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWukongSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.grabPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerWukongSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
  
    #--------------------------------------------------------------------------------------
    #-----子抓取--按网址抓取    
    async def dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerWukongSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.grabPageData(page,crawlerInfo,index)

        self.printLogInfo("CrawlerWukongSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    

    #-----------------------------------------------------------------------------------------------
    #-----抓取问题回答和评论回复
    async def grabPageData(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWukongSub->grabPageData() : enter")
    
        questionReplyBuf = []
        commentBuf       = []
        ret              = 0
        
        #-------------------------------------------------------------------------------------------
        #-----获取问题描述作为title
        ret,curText = await self.pyteerEx.getElementContext(page,self.cssContextDict["question_name"]);
        if ret == RetVal.Suc.value:
            crawlerInfo.main_title = curText.strip()
        
        #-----问题描述和问题内容作为根回复 
        #-----若问题描述和问题内容都没有关键词 则退出子页抓取
        rootReply = await self.generateRootReplyInfo(page,crawlerInfo)
        result = self.checkStrIncludeKeyword(rootReply.main_title,rootReply.text,crawlerInfo.keyword)
        if result != RetVal.Suc.value:
            return RetVal.FailExitNotFindKeyword.value,[]
        

        #-----问题回答作为二级根节点
        selector = self.cssContextDict["answer_item"]
        ret,elementList = await self.pyteerEx.getElementAll(page,selector) 
        if ret != RetVal.Suc.value:
            self.printReplyInfo(rootReply,crawlerInfo)
            questionReplyBuf.append(rootReply)
            return ret,questionReplyBuf


        rootReply.comments = len(elementList)
        questionReplyBuf.append(rootReply)

        for item in elementList:
            ret1,replyInfo = await self.grabQuestionReplyInfo(page,item,crawlerInfo)
            if ret1 != RetVal.Suc.value:
                continue
        
            #---子页问题回复抓取上限 抓取数达到上限后，不再抓取后面的回答项目
            if self.terminateSubPageMaxCount == crawlerInfo.vscroll_grap_count:
                return RetVal.FailExitCountLimit.value,questionReplyBuf

            crawlerInfo.vscroll_grap_count +=1

            #-----先确认是否有评论回复
            commentCount = await self.generateCommentCount(item)
            replyInfo.comments = commentCount
            questionReplyBuf.append(replyInfo) 
     
            #if commentCount == 0:
                #continue
            
            """ 2019.09.27 注释 不需要抓取回答的子回复
            #-----展开评论回复
            ret1 = await self.pyteerEx.clickHoverElement(item,self.cssContextDict["comment_flag"],self.clickDelay,self.hoverDelay)
            if ret1 != RetVal.Suc.value:
                continue
            
            #-----加载所有的评论回复  
            ret1 = await self.clickMoreComment(item,self.cssContextDict["comment_load_more"]) 
            
            #-----获取评论回复
            ret1,commentItemList = await self.pyteerEx.getElementAll(item,self.cssContextDict["comment_content"])
            if ret1 != RetVal.Suc.value:
                continue            
            
            crawlerInfo.p_parentPageItemNoSub = crawlerInfo.p_curPageItemNo
            crawlerInfo.pid = replyInfo.pid
            for element in commentItemList:
                ret1,commentReplyInfo = await self.grabCommentReplyInfo(page,element,crawlerInfo)
                if ret1 != RetVal.Suc.value:
                    continue
                commentBuf.append(commentReplyInfo)
                self.printReplyInfo(commentReplyInfo,crawlerInfo)
            """
        #-----合并问题回复和评论回复并返回
        questionReplyBuf.extend(commentBuf)

        if len(questionReplyBuf) > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value    
        
        self.printReplyInfoBuf(questionReplyBuf,crawlerInfo)
        self.printLogInfo("CrawlerWukongSub->grabPageData() : exit")
        return ret,questionReplyBuf

    #----------------------------------------------------------------------------------------
    #----获取问题作为根节点回复
    async def generateRootReplyInfo(self,page,crawlerInfo):       
        self.printLogInfo("CrawlerWukongSub->generateRootReplyInfo() : enter")
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.main_title = crawlerInfo.main_title
        replyInfo.href    = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        replyInfo.parentContentId      = 0
        crawlerInfo.p_curPageItemNo    = 1 
        replyInfo.contentId            = crawlerInfo.p_curPageItemNo
        
        ret,curText = await self.pyteerEx.getElementContext(page,self.cssContextDict["question_text"])
        if ret == RetVal.Suc.value:
            replyInfo.text = curText.strip()
            
        self.printLogInfo("CrawlerWukongSub->generateRootReplyInfo() : exit")
        return replyInfo
        
    

    #----------------------------------------------------------------------------------------
    #----获取当前问题回答下的评论回复数
    async def generateCommentCount(self,element):
        
        ret,curText = await self.pyteerEx.getElementContext(element,self.cssContextDict["comment_flag"])
        if ret != RetVal.Suc.value:
            return 0
        return CommonTool.getDigitFromString(curText.strip())
    
    
    #----------------------------------------------------------------------------------------
    #----加载所有评论回复
    async def clickMoreComment(self,element,selector):
        self.printLogInfo("CrawlerWukongSub->clickMoreComment() : enter")
        while True:
            ret,targetElement = await self.pyteerEx.getElement(element,selector)
            if ret != RetVal.Suc.value:
               self.printLogInfo("CrawlerWukongSub->clickMoreComment() : leave")
               break
            ret = await self.pyteerEx.clickHoverElement(element,selector,self.clickDelay,self.hoverDelay)
            if ret != RetVal.Suc.value:
               self.printLogInfo("CrawlerWukongSub->clickMoreComment() : leave")
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

        replyInfo.parentContentId      = 1
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
        if len(curDateText) == 0:
            return "";
    
        strDatetime = "{}-{}:{}".format(self.strCurYear,curDateText,"00")
        result,dat= self.verifyDate(strDatetime)
        if result:
            now = datetime.datetime.now()
            if dat < now:                 
                return strDatetime
            else:
                newDate = datetime.datetime(dat.year-1,dat.month,dat.day,dat.hour,dat.minute,dat.second)
                return newDate.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "";
      
                   
    #------------------------------------------------------------------------------------------------
    #---验证传入的字符串是否是有效时间格式 并返回成功转化的时间数据
    def verifyDate(self,datetime_str):
        try:        
    	    ret = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')        
    	    return True,ret    
        except ValueError:        
    	    return False,None 

            
        
        


    