import asyncio
import random
import time
import logging
import json
from pyppeteer import launch
import sys,os

sys.path.append("..")

from  struct_def import *
from crawlers.search_base_sites import *
from pyteerex.pyppeteer_ex  import *
from common.tools           import *

class   CrawlerSinaIaskSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        
        
        #---------------------------------------------------
        
        self.cssPageBtnDict = {
                               'firstPageBtn':" ",
                               'prePageBtn'      :"div.wgt-answers.has-other>div.bd-wrap>div.wgt-pager.pager >a.pager-pre",
                               'prePageBtnNext'  :"div.wgt-answers.has-other>div.bd-wrap>div.wgt-pager.pager >a.pager-pre+a",
                               
                               'curPageText':"div.wgt-answers.has-other>div.bd-wrap>div.wgt-pager.pager >b",
                               'curPageBtn' :"div.wgt-answers.has-other>div.bd-wrap>div.wgt-pager.pager  >b",
                               
                               'nextPageBtn':"div.wgt-answers.has-other>div.bd-wrap>div.wgt-pager.pager >a.pager-next",
                               
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':20000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        
        #sub
        self.cssContextDict    = {
                                  #--标题
                                  'mainTitle':".problem-title-text",
                                  'mainTitle_replay':".problem-text",
                                  #'mainTitle_count':"div.layout-wrap > section.line.qb-section > article.grid.qb-content>div.wgt-ask.accuse-response>div.line.f-aid.ask-info >div.line.wgt-replyer-line>span#v-times",
                                  #-------------------------------------------------------------------------
                                  #首评论-----只有一个首评论--分页后没有首评论
                                  'mainReply_best':"div.wgt-best ", 
                                  #首评论-【展开全部】-click
                                  'mainReply_best_span_all_click':"div.wgt-best>div.bd.answer>div.line.content>div.best-text.mb-10 >div.wgt-best-mask > div.wgt-best-showbtn",


                                  #首评论-pid
                                  'mainReply_best_pid':"div.wgt-best>div.wgt-replyer-all ", 
                                  #首评论-昵称 
                                  'mainReply_best_nickname':"div.wgt-best>div.wgt-replyer-all>span.wgt-replyer-all-uname",
                                  #首评论-时间
                                  'mainReply_best_time':    "div.wgt-best>div.wgt-replyer-all>span.wgt-replyer-all-box>span.wgt-replyer-all-time",
                                  #首评论-文本入口
                                  'mainReply_best_text_entry':"div.wgt-best>div.bd.answer>div.line.content>div.best-text.mb-10",
                                  #首评论-支持数
                                  'mainReply_best_support':"div.wgt-best>div.bd.answer>div.line.content>div.newbest-content-meta>div.wgt-best-operator>div.wgt-eva >span.evaluate >b.evaluate-num ",
                                  #首评论-不支持数
                                  'mainReply_best_unsupport':"div.wgt-best>div.bd.answer>div.line.content>div.newbest-content-meta>div.wgt-best-operator>div.wgt-eva >span.evaluate-bad >b.evaluate-num ",
                                  #首评论-下面的子评论的个数
                                  'mainReply_best_reply_num':"div.wgt-best>div.bd.answer>div.line.content>div.newbest-content-meta>div.wgt-best-operator>span.comment >em ",
                                  #首评论-点击评论个数
                                  'mainReply_best_reply_click':"div.wgt-best>div.bd.answer>div.line.content>div.newbest-content-meta>div.wgt-best-operator>span.comment  ",
                                  #--------------------------------------------------------------------------
                                  #首评论下的-子回复 parent--div.bd.answer,先打开subReply_best
                                  #进入子评论的相对路径
                                  'subReply_best_entry':"div.wgt-best>div.bd.answer>div.comment-area>div.comment-area-inner>div.comment-body.line",
                                  #枚举所有子评论
                                  'subReply_best_item':"div.comment-entry.f-12 ",
            
                                  'subReply_best_scroll_cur':"p.comment-pager.pager>b.pager-now",
                                  'subReply_best_scroll_next':"p.comment-pager.pager>",

                                  #---------------------------------------------------------------------------------
                                  #-------所有的评论文本
                                  #-评论文本匹配
                                  'all_reply_text_first_p'   : "p",
                                  'all_reply_text_other_p'   : "p",
                                  #-------评论中的图片
                                  'all_reply_text_pic'       : "a.ikqb_img_alink",


                                  #--------------------------------------------------------------------------
                                  #其它评论----
                                  # 【 折叠回答】
                                  'mainReply_fold_click':".detail-text-more[style='']",
                                  #【更多回答】--点击
                                  'mainReply_more_click':"div.show a.detail-curt-view .view-text",

                                  #其它评论----入口
                                  'mainReply':"div.wgt-answers > div.bd-wrap>div.bd.answer ",
                                  #【展开全部】-click
                                  'mainReply_span_all_click':"div.line.content-wrapper>div.line.content>div.answer-text.mb-10 >div.wgt-answers-mask>div.wgt-answers-showbtn",

                                  #pid
                                  'mainReply_pid'     :"div.wgt-replyer-all",
                                  'mainReply_nickname':"div.wgt-replyer-all>span.wgt-replyer-all-uname",
                                  'mainReply_time'    :"div.wgt-replyer-all>span.wgt-replyer-all-box>span.wgt-replyer-all-time ",
                                  
                                  'mainReply_text_entry':"div.line.content-wrapper>div.line.content>div.answer-text.mb-10",
                                  'mainReply_support'   :"div.line.content-wrapper>div.line.content >div.line.info.f-light-gray>div.wgt-answers-operator>div.wgt-eva>span.evaluate >b.evaluate-num ",
                                  'mainReply_unsupport' :"div.line.content-wrapper>div.line.content >div.line.info.f-light-gray>div.wgt-answers-operator>div.wgt-eva>span.evaluate-bad >b.evaluate-num ",
                                  #子评论数量
                                  'mainReply_reply_num' :"div.line.content-wrapper>div.line.content >div.line.info>div.wgt-answers-operator>span.comment > em  ",
                                  #点击评论个数
                                  'mainReply_reply_click':"div.line.content-wrapper>div.line.content >div.line.info>div.wgt-answers-operator>span.comment  " ,
                                  
                                  #其它评论----子评论--
                                  #子评论--入口
                                  'subReply_entry'   :"div.line.content-wrapper>div.comment-area>div.comment-area-inner>div.comment-body.line",
                                  #从id获取sid
                                  'subReply_sid'     :"div.comment-item>div.operation-con>span.evaluate",
                                  'subReply_nickname':"div.comment-item>div.details.f-aid>a.f-light.comment-entry-username ",
                                  'subReply_time'    :"div.comment-item>div.details.f-aid>span.comment-entry-time ",
                                  #子评论文本
                                  'subReply_text'    :"div.comment-item>div.comment-content ",
                                  #子评论支持数
                                  'subReply_support' :"div.comment-item>div.operation-con>span.evaluate>em.evaluate-num ",
                                  
                                 }
        #login
        
        self.cssLoginDict      ={
                                 'user_name':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-userName >input.pass-text-input.pass-text-input-userName",
                                 'password' :"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-password >input.pass-text-input.pass-text-input-password",
                                 'clk_button':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-submit >input.pass-button.pass-button-submit",
                                 'pageLoginExit':"body.skin_normal>div#passport-login-pop > div.tang-foreground > div.tang-title.tang-title-dragable>div.buttons>a.close-btn "
                                 }
        #more
        

        
        #log
        logpath = "sina_iask/sub/" + str(index) 
        self.log_inits(logpath,2,2,logging.INFO)

    #--------------------------------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------
    #---function
    #-------------------------------------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------------
    #----获取pageUrl
    """
    def getPageUrl(self,strUrl):
        pageUrl   = ""
        strUrl = strUrl.strip()

        if len(strUrl) > 0:
            strList   = CommonTool.strSplit(strUrl,"html")
            if len(strList) > 1:
                pageUrl = strList[0]
                pageUrl = pageUrl + "html"
            else:
                pageUrl = strUrl
        else:
            pageUrl   = ""
        
        return pageUrl
    """
    #--------------------------------------------------------------------------------------
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerSinaIaskSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.dealCompoundwordCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerSinaIaskSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    #--------------------------------------------------------------------------------------
    #子抓取--按楼层抓取    
    async def  dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerSinaIaskSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.dealDefUrlCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerSinaIaskSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    
    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealDefUrlCrawlerPage(self,page,crawlerInfo,index):
        
        replyBuf = []

        ret,replyBuf = await self.dealSubCrawlerPageBase(page,crawlerInfo,index )
         
        return ret,replyBuf
        

    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealCompoundwordCrawlerPage(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerSinaIaskSub->dealCompoundwordCrawlerPage() : enter")

        replyBuf = []
        ret,replyBuf = await self.dealSubCrawlerPageBase(page,crawlerInfo,index )
        
        self.printLogInfo("CrawlerSinaIaskSub->dealCompoundwordCrawlerPage() : exit")
        return ret,replyBuf
    
    #--------------------------------------------------------------------------------------
    #
    async def  getMainTitleInfo(self,page,crawlerInfo,index):

        self.getLogInfo().show("CrawlerSinaIaskSub->getMainTitleInfo()->index={}: enter ".format(index))
        
        strUrl    = crawlerInfo.url
        ret       = 0   
        replyInfo =  GrapReplyInfo() 
        
        replyInfo.copyAsCrawlerInfo(crawlerInfo )
        
        #title
        selector    =  self.cssContextDict["mainTitle"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        if ret == RetVal.Suc.value:
            replyInfo.main_title = curText.strip()
        else:
            replyInfo.main_title = ""
        crawlerInfo.main_title   = replyInfo.main_title

        #--标题为空,则返回失败
        if len(replyInfo.main_title ) < 1:
            return RetVal.FailExit.value,replyInfo
            
        #publisher
        selector = "div.user-bar-info > a .user-name"
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        if ret == RetVal.Suc.value:
            replyInfo.publisher = curText.strip()
        #text
        selector    =  self.cssContextDict["mainTitle_replay"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        if ret == RetVal.Suc.value:
            replyInfo.text = curText.strip()
        
        #-----判断标题和内容是否包含keyword
        replyBuf = []
        replyBuf.append(replyInfo)
        #ret1 = self.checkIncludeKeyword(crawlerInfo,replyBuf)
        ret1 = self.checkStrIncludeKeyword(replyInfo.main_title,replyInfo.text,crawlerInfo.keyword)
        if ret1 == RetVal.Fail.value:
            ret =  RetVal.FailExitNotFindKeyword.value
            return ret,replyInfo
        
        #browser count 
        # selector    =  self.cssContextDict["mainTitle_count"]
        # ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        # if ret == RetVal.Suc.value:
        #     replyInfo.reads = self.getMainTitleCount(curText.strip())
                           
        #
        crawlerInfo.p_curPageItemNo +=1
        replyInfo.contentId  = crawlerInfo.p_curPageItemNo
        replyInfo.parentContentId = 0
        replyInfo.href      = strUrl
        replyInfo.pageUrl   = self.getPageUrl(strUrl)

        self.getLogInfo().show("CrawlerSinaIaskSub->getMainTitleInfo()->index={}: exit title={}".format(index,crawlerInfo.main_title))

        ret = RetVal.Suc.value
        return ret, replyInfo
    
    #--------------------------------------------------------------------------------------
    #
    def getMainTitleCount(self,strMainTitleCount):
        return CommonTool.getDigitFromString(strMainTitleCount)

    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerPageBase(self,page,crawlerInfo,index):
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}:%%%%%%%%%%%%%%%%%%%%%%%%%%".format(index))
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: enter keyword={} ".format(index,crawlerInfo.keyword))
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: enter url={} ".format(index,crawlerInfo.url))
        
        retCount      = 0
        curPageItemNo = 0
        strUrl        = crawlerInfo.url
        strCompoundword = crawlerInfo.compoundword

        replyBuf  = []
        ret       = RetVal.Suc.value
        ret1      = RetVal.Suc.value
        replyInfo  = None
        #--抓取问题
        crawlerInfo.p_curPageItemNo    = 0
        crawlerInfo.p_parentPageItemNo = 0
        
        ret1,replyInfo = await self.getMainTitleInfo(page,crawlerInfo,index)
        if ret1 == RetVal.Suc.value:
            replyBuf.append(replyInfo)
            self.printReplyInfo(replyInfo,crawlerInfo)

        elif ret1 == RetVal.FailExitNotFindKeyword.value:  #退出抓取
            self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: title and text is empty,terminate grap ".format(index))
            self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: keyword={} ".format(index,crawlerInfo.keyword))
            self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: title={} ".format(index,crawlerInfo.main_title))
            self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: context={} ".format(index,replyInfo.text))
            return ret1,replyBuf

        elif ret1 == RetVal.FailExit.value: 
            self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: title is empty,terminate grap ".format(index))
            return ret1,replyBuf

            
        crawlerInfo.p_parentPageItemNo += 1   
            

        #获取评论
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: dealMainOtherinfo begin ".format(index))
        
        cssMainOther     = ".other_item,.good_item"
        ret,elementList  =     await self.pyteerEx.getElementAll(page,cssMainOther)
        #当前出现的连续类小说评论数
        currNovelTerminateCount = 0
        for element in elementList:
            
            ret1,replyInfo = await self.dealMainOtherinfo(element,strUrl,strCompoundword,crawlerInfo.grap_data,index,crawlerInfo)

            if ret1 == RetVal.Suc.value:
                replyBuf.append(replyInfo)
                self.printReplyInfo(replyInfo,crawlerInfo)
                crawlerInfo.vscroll_grap_count +=1
                #判断已抓取的数量是否超过最大抓取数
                if crawlerInfo.vscroll_grap_count >= self.terminateSubPageMaxCount:
                    ret = RetVal.FailExitCountLimit.value
                    return ret, replyBuf
                #判断小说
                if len(replyInfo.text) > self.novelMaxWordCount:
                    currNovelTerminateCount = currNovelTerminateCount+1
                else:
                    currNovelTerminateCount = 0
                if currNovelTerminateCount == self.novelTerminateCount:
                    return RetVal.FailExitAsNovel.value,replyBuf
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: dealMainOtherinfo end ".format(index))
        #---------------------------end for

        #-------------------
        if len(replyBuf) > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubCrawlerPageBase()->index={}: dealMainOtherinfo end1 ".format(index))
        
        return ret,replyBuf

    #--------------------------------------------------------------------------------------
    # 
    async def  dealMainScrollBefor(self,page,crawlerInfo):
        
        selector  = self.cssContextDict["mainReply_more_click"]
        ret = await self.pyteerEx.clickHoverElement(page,selector,1,1)
        
        selector  = self.cssContextDict["mainReply_fold_click"]
        ret = await self.pyteerEx.clickHoverElement(page,selector,1,1)

        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    # goto to next page
    # return:
    #   isFinish   = 0：继续抓取下一页
    #   isFinish   = 1: 完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开下一页
    #   isFinish   = 3: 抓取失败，退出       
    async def  dealSubGotoNextPage(self,page,curPageIndex,maxPageNum):
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubGotoNextPage()->index={}: enter ".format(curPageIndex))
        
        isFinish    = RetVal.GrapSucRepeat.value
        nAllPageNum = 0
        ret         = RetVal.Suc.value
        strRet      = ""
        url_next    = ""

        cssCurPage        = self.cssPageBtnDict["curPageText"]
        selectorNextBtn   = self.cssPageBtnDict["nextPageBtn"]
        
        
        #all page
        ret1,element = await self.pyteerEx.getElement(page,selectorNextBtn)
        if ret1 == RetVal.Suc.value:
            self.getLogInfo().show("CrawlerSinaIaskSub->dealSubGotoNextPage()->index={}: has next page ".format(curPageIndex))
            
            url_next = await self.pyteerEx.getElementHref(page,selectorNextBtn)

            ret = await self.pyteerEx.hovers(element)
            if ret != RetVal.Suc.value:
                return  RetVal.GrapSuc.value

            ret  = await self.pyteerEx.clickNavigate(page,selectorNextBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
            if ret == RetVal.Suc.value:
                isFinish   = RetVal.GrapSucRepeat.value
            else:
                isFinish   = RetVal.GrapFailRepeat.value
        elif ret1 == RetVal.Fail.value:   #only one page
            isFinish   = RetVal.GrapSuc.value
        elif ret1 >RetVal.Fail.value:
            isFinish   = RetVal.GrapSucRepeat.value

        self.getLogInfo().show("CrawlerSinaIaskSub->dealSubGotoNextPage()->index={}: exit ".format(curPageIndex))  

        return isFinish,url_next  
    

    #-------------------------------------------------------------------------------------------
    #获取评论内容
    async def getReplyAllSubText(self,ObjElement,cssStr,index):
        
        print("getReplyAllSubText:enter ")

        ret    = RetVal.Suc.value
        strText = ""
        curText = ""
        cssPic  = self.cssContextDict["all_reply_text_pic"]

        ret,elementList = await self.pyteerEx.getElementAll(ObjElement,cssStr)
        print("getReplyAllSubText:enter 1=",len(elementList))
        
        count = 0
        for item in elementList:
            
            ret,curText = await self.pyteerEx.getElementHref(item,cssPic)
            if ret == RetVal.Suc.value:
                strText = strText + GrapReplyInfo.getPicWrapStr(curText)
            

            ret,curText = await self.pyteerEx.getElementContext(item)
            if ret == RetVal.Suc.value:
                strText = strText + GrapReplyInfo.getTextWrapStr(curText)
            

        if len(strText) > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        
        return ret,strText


    #-------------------------------------------------------------------------------------------
    #获取评论内容--
    #分为有p标签和没有p标签
    async def  getReplyAllText(self,ObjElement,index):
        
        print("getReplyAllText:enter ")

        strText    = ""
        strTextAll = ""
        ret  = 0
        ret1 = 0
        
        cssSub          = self.cssContextDict["all_reply_text_first_p"]
        #直接获取div中文本
        ret,strText   = await self.pyteerEx.getElementContext(ObjElement)
        if ret == RetVal.Suc.value:
            strTextAll += strText

        #获取p标签中的文本
        ret,strText = await self.getReplyAllSubText(ObjElement,cssSub,index)
        if ret == RetVal.Suc.value:
            strTextAll += strText
        
        strTextAll = strTextAll.replace("\n展开全部","")
        strTextAll = strTextAll.strip()
        return strTextAll

    #-------------------------------------------------------------------------------------------
    #获取第一个评论相关的信息
    #ret = 0:抓取到新的，或更新的
    #ret = 1:数据没有变化
    #ret = 2:出错
    async def  dealMainFirstinfo(self,page,strUrl,strCompoundword,grap_data_map,index,crawlerInfo):
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealMainFirstinfo()->index={}: enter ".format(index))

        replyBuf   = []
        replyBuf1  = []
        replyInfo =  GrapReplyInfo() 
        reply_num_str = ""
        strPid     = "" 
        ret  = 0
        ret1 = 0
        ret2 = 0
        checkRet = 0
        val  = ""
        selector  = self.cssContextDict["mainReply_best_pid"]
        
        #pid--找不到，直接返回
        ret2,val  = await self.pyteerEx.getElementId(page,selector)
        if ret2 != RetVal.Suc.value:
            ret = RetVal.Fail.value
            return  ret, replyBuf
            #return ret
        
        val            = self.getMainPid(val)
        replyInfo.pid  = val
        strPid         = val
    
        

        #---click 【展开全部】
        self.getLogInfo().show("CrawlerSinaIaskSub->dealMainFirstinfo()->index={}: click [span all ]  begin ".format(index))
        
        selector  = self.cssContextDict["mainReply_best_span_all_click"]
        
        await self.clickSpanAllBtn(page,selector)
        self.getLogInfo().show("CrawlerSinaIaskSub->dealMainFirstinfo()->index={}: click [span all ]  end ".format(index))
        
        #------hover 
        selector  = self.cssContextDict["mainReply_best_reply_num"]
        ret1 = await self.pyteerEx.hoverElement(page,selector,2)
        
        #time
        selector  = self.cssContextDict["mainReply_best_time"]
        ret1,curText = await self.pyteerEx.getElementContext(page,selector)
        curText = GrapReplyInfo.dealStr(curText )
        replyInfo.publishTime     = curText + " 00:00:00"
        
        #-------check
        checkRet,replyInfo_last = grap_data_map.isExistKeyEx(strUrl,replyInfo.pid,"",replyInfo.publishTime )
        
        if checkRet == 2:   #same
            ret = RetVal.Fail.value    
        elif checkRet == 0: #不存在 
            #publisher
            selector    = self.cssContextDict["mainReply_best_nickname"]
            ret2,curText = await self.pyteerEx.getElementContext(page,selector)
            replyInfo.publisher     = GrapReplyInfo.dealStr(curText )
            
            #stars
            selector  = self.cssContextDict["mainReply_best_support"]
            ret2,curText = await self.pyteerEx.getElementContext(page,selector)
            replyInfo.stars     = CommonTool.strToInt(curText )
            
            #unsupport
            selector  = self.cssContextDict["mainReply_best_unsupport"]
            ret2,curText = await self.pyteerEx.getElementContext(page,selector)
            replyInfo.unsupport     = GrapReplyInfo.dealStr(curText )

        elif checkRet == 1: #update
            replyInfo.publisher = replyInfo_last.publisher
            replyInfo.stars  = replyInfo_last.stars
            replyInfo.unsupport = replyInfo_last.unsupport
        
        #----
        #reply_num
        selector  = self.cssContextDict["mainReply_best_reply_num"]
        ret2,reply_num_str = await self.pyteerEx.getElementContext(page,selector)
        
        
        replyInfo.isMain = 1
        replyInfo.href      = strUrl
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(replyInfo.pid,"")
        replyInfo.pageUrl   = self.getPageUrl(strUrl)

        replyInfo.parentContentId = crawlerInfo.p_parentPageItemNo
        crawlerInfo.p_curPageItemNo += 1
        replyInfo.contentId       = crawlerInfo.p_curPageItemNo
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        
        replyInfo.comments = CommonTool.strToInt(reply_num_str.strip())

        #-----
        if checkRet != 2: #get text
            # text
            selector  = self.cssContextDict["mainReply_best_text_entry"]
            ret2,elementText = await self.pyteerEx.getElement(page,selector)
            if ret2 == RetVal.Suc.value:
                replyInfo.text = await self.getReplyAllText(elementText,index)
            #self.log_grap.show(replyInfo.text )
            
            #----add
            replyBuf.append(replyInfo )

        
        #------------
        retCount = len(replyBuf)
        if retCount >0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        
        return ret,replyBuf
    
    #--------------------------------------------------------------------------------------
    #--点击【展开全部】按钮--考虑多次点击这个按钮
    async def clickSpanAllBtn(self,ObElement,selector):
        
        #ret = await self.pyteerEx.clickElementDelay(ObElement,selector,1)
        ret = await self.pyteerEx.clickHoverElement(ObElement,selector,1,1 )  
    
    #--------------------------------------------------------------------------------------
    #获取其它评论相关的信息
    #ret = 0：成功抓取数据或更新
    #ret = 2: 数据相同
    #ret = 3: 通讯出错
    async def  dealMainOtherinfo(self,element,strUrl,strCompoundword,grap_data_map,index,crawlerInfo):
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealMainOtherinfo()->index={}: enter ".format(index))

        ret  = RetVal.Fail.value       
        
        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = self.getPageUrl(crawlerInfo.url)

        replyInfo.parentContentId      = crawlerInfo.p_parentPageItemNo

        #-----------------------------------------------
        #--publisher
        replyPublisherTagCss = ".user-name a"
        ret,curText = await self.pyteerEx.getElementContext(element,replyPublisherTagCss)
        replyInfo.publisher = CommonTool.strStripRet(curText)

        # #--pid property = comment_id ; comment_id="4413581661404210"
        # propertyName = replyPidName
        # ret1,curText = await self.pyteerEx.getElementProDef(page,element,propertyName,cssReplyPid)
        # curText      = curText.strip()
        # replyInfo.pid = curText
        # replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(curText,"")

        #---text
        replyContTagCss = " .list-text"
        ret,curText   = await self.pyteerEx.getElementContext(element,replyContTagCss)
        replyInfo.text =curText.strip()

        #---time 格式: 9月4日 16:30
        replyTimeTagCss = ".time"
        ret,curText   = await self.pyteerEx.getElementContext(element,replyTimeTagCss)
        replyInfo.publishTime = curText
            
        #--support
        replyZanTagCss = ".praise span"
        ret,curText   = await self.pyteerEx.getElementContext(element,replyZanTagCss)
        replyInfo.stars = CommonTool.strToInt(curText)
            
        #---------------------------------------------------
        if len(replyInfo.publisher)>0:
            crawlerInfo.p_curPageItemNo    += 1
            replyInfo.contentId            = crawlerInfo.p_curPageItemNo
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        return ret,replyInfo
 

    #--------------------------------------------------------------------------------------
    #获取单个回复下-所有的子回复-
    #   --要判断分页的情况
    async def  dealGetSubReplyAsScroll(self,objElement,strPid,strUrl,strCompoundword,grap_data_map,index,crawlerInfo):
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: enter ".format(index))

        ret = 1
        ret1 = 1
        replyBuf = []
        replyInfo = None
        #scroll
        cssScroll =  self.cssContextDict["subReply_best_scroll_cur"]
        cssNext   =  self.cssContextDict["subReply_best_scroll_next"] 
        cssReply  =  self.cssContextDict["subReply_best_item"] 


        loop = 100
        curNo = 0
        
        itemCount = 0

        while loop > 0:
            loop -= 1
            curNo +=1
            
            self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: get sub reply loop={} ".format(index,curNo))

            #--all reply
            ret1,elementList = await self.pyteerEx.getElementAll(objElement,cssReply )
            itemNum = 0
            for elementItem in elementList:
                itemNum +=1
                #itemCount += 1
                
                self.getLogInfo().show("-----------------------")
                self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: get all sub reply loop={} ,crawler item begin={} ".format(index,curNo,itemNum))
                    
                ret,replyInfo =  await self.dealGetAllSubReply(elementItem,strPid,strUrl,strCompoundword,grap_data_map,index,crawlerInfo)
                if ret == RetVal.Suc.value:
                    #crawlerInfo.p_curPageSubItemNo += 1
                    replyBuf.append(replyInfo)

                self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: get all sub reply loop={},crawler item end={} ".format(index,curNo,itemNum))

            #----next page
            strNum = "a:nth-child({})".format(curNo+1)
            cssNextAll = cssNext + strNum

            self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: get all sub reply loop={},cssNextAll={} ".format(index,curNo,cssNextAll))
            ret1 = await self.pyteerEx.clickHoverElement(objElement,cssNextAll,1,1)
     
            if ret1 == RetVal.Suc.value:
                self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: goto to next page1 ".format(index))
                continue
            else:
                break
        
        retCount = len(replyBuf)
        if retCount > 0:
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value
        
        self.getLogInfo().show("CrawlerSinaIaskSub->dealGetSubReplyAsScroll()->index={}: exit ".format(index))

        return ret,replyBuf

    #--------------------------------------------------------------------------------------
    # ret = 0:成功抓取新的，或更新过的数据  
    # ret = 2:数据相同
    # ret = 3:失败   
    async def  dealGetAllSubReply(self,element,strPid,strUrl,strCompoundword,grap_data_map,index,crawlerInfo):

        self.getLogInfo().show("CrawlerSinaIaskSub->dealGetAllSubReply()->index={}: enter ".format(index))
        
        ret   = 0

        replyInfo =  GrapReplyInfo()
        replyInfo.parentContentId = crawlerInfo.p_parentPageItemNoSub
        crawlerInfo.p_curPageItemNo +=1
        replyInfo.contentId       = crawlerInfo.p_curPageItemNo
        replyInfo.copyAsCrawlerInfo(crawlerInfo)  
        reply_num = ""
        ret1 = 0
        val = ""
        
        #pid--
        selector       = self.cssContextDict["subReply_sid"]
        ret1,curText    = await self.pyteerEx.getElementId(element,selector)
        replyInfo.sid  = self.getSubSid(curText)

        #time
        selector  = self.cssContextDict["subReply_time"]
        ret1,curText = await self.pyteerEx.getElementContext(element,selector)
        curText      = GrapReplyInfo.dealStr(curText )
        replyInfo.publishTime = curText + ":00"
        
        
        # spid is empty
        if not replyInfo.sid:
            self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfo_new() : spid is empty,url={},pid={}".format(strUrl,strPid))
            ret = RetVal.Fail.value
            return ret,replyInfo

        #------check
        checkRet,replyInfo_last = grap_data_map.isExistKeyEx(strUrl,strPid,replyInfo.sid,replyInfo.publishTime )
        if checkRet == 2:   #same
            ret = RetVal.Fail.value  
        elif checkRet == 0: #不存在  
            #publisher
            selector    = self.cssContextDict["subReply_nickname"]
            ret1,curText = await self.pyteerEx.getElementContext(element,selector)
            replyInfo.publisher = GrapReplyInfo.dealStr(curText )
            self.getLogInfo().show("CrawlerSinaIaskSub->dealGetAllSubReply()->index={}: publisher= ".format(index,replyInfo.publisher))
            
        else:
            replyInfo.publisher = replyInfo_last.publisher

        #-----
        if checkRet != 2:
            # text
            selector    = self.cssContextDict["subReply_text"]
            ret1,curText = await self.pyteerEx.getElementContext(element,selector )
            if ret1 == RetVal.Suc.value:
                replyInfo.text = GrapReplyInfo.dealStr(curText )
            #self.log_grap.show(replyInfo.text )
            
            #support
            selector  = self.cssContextDict["subReply_support"]
            ret1,curText = await self.pyteerEx.getElementContext(element,selector)
            replyInfo.stars = CommonTool.strToInt(curText )
        
            self.getLogInfo().show("CrawlerSinaIaskSub->dealGetAllSubReply()->index={}: exit ".format(index))
            #other
            replyInfo.href    = strUrl
            replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(strPid,replyInfo.sid)
            replyInfo.pageUrl = self.getPageUrl(strUrl)

            replyInfo.pid  = strPid
            
            ret = RetVal.Suc.value

        return ret, replyInfo

    
    #------------------------------------------------------------------------------
    #get main title
    async def  grabSubPageMainTitle(self,page):

        ret = RetVal.Suc.value
        strTitle = ""
        
        return ret,strTitle

    #-------------------------------------------------------------------------------------------
    #获取主回复的pid
    def getMainPid(self,strMainPid):
        
        strPid     = ""
        strMainPid = strMainPid.strip()

        strlist = strMainPid.split('wgt-replyer-all-')
        if len(strlist) > 1:
            strPid = strlist[1]
            strPid.strip()
            
        return strPid
    
    #-------------------------------------------------------------------------------------------
    #获取主回复中子回复的sid
    def getSubSid(self,strSubSid):
        
        strSid     = ""
        strSubSid = strSubSid.strip()

        strlist = strSubSid.split('evaluate-')
        if len(strlist) > 1:
            strSid = strlist[1]
            strSid.strip()
            
        return strSid

    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  checkFirstPage(self,page):
        
        self.printLogInfo("CrawlerSinaIaskSub->checkFirstPage() : enter")
        
        url            = ""
        cssPrepage     = self.cssPageBtnDict["prePageBtn"]
        cssPrepageNext = self.cssPageBtnDict["prePageBtnNext"]
        ret  = RetVal.Fail.value
        countLoop  = 1000
        curPageNo  = await self.getCurPageVal(page)
        
        #------------------------
        if curPageNo > 1:
            while countLoop > 0:
                countLoop -= 1

                ret1,element = await self.pyteerEx.getElement(page,cssPrepage)
                if ret1 == RetVal.Suc.value:
                    ret1  = await self.pyteerEx.clickNavigate(page,cssPrepageNext,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
                    if ret1 == RetVal.Suc.value: #成功
                        continue
                    else:
                        ret = RetVal.FailExit.value
                        self.printLogInfo("CrawlerSinaIaskSub->checkFirstPage() : call clickNavigate fail")
                        break

                elif ret1 == RetVal.Fail.value:  #
                    ret =  RetVal.FailRepeat.value
                    break
                else:                            #异常
                    ret = RetVal.FailExit.value
                    self.printLogInfo("CrawlerSinaIaskSub->checkFirstPage() : exception")
                    break
            #-----------end while
        #---------------------
        elif curPageNo == 1:
            ret = RetVal.Suc.value
        else:  # page=0,出错
            ret = RetVal.FailExit.value
            self.printLogInfo("CrawlerSinaIaskSub->checkFirstPage() : curPageNo={},clickNavigate after,curPage !=1,exit".format(curPageNo))

        #--
        if ret ==  RetVal.FailRepeat.value:
            curPageNo  = await self.getCurPageVal(page)
            if curPageNo == 1:
                url = page.target.url
                ret = RetVal.FailRepeat.value
            else:
                ret = RetVal.FailExit.value

        self.printLogInfo("CrawlerSinaIaskSub->checkFirstPage() : exit")    
        return ret,url
        

    #--------------------------------------------------------------------------------------
    async def  waitforPageLoad(self,page):
        """
        print("CrawlerTiebaSub->waitforPageLoad():enter ")
        
        print( self.cssPageBtnDict["bottomAllPageNum"])
        ret = await self.pyteerEx.waitPage(page,self.cssPageBtnDict["bottomAllPageNum"],1)

        print("CrawlerTiebaSub->waitforPageLoad():leave ")
        return ret
        """
        return RetVal.Suc.value


    