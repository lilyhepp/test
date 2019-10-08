#----------  weibo_sub.py
#-- 微博--子抓取
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
class   CrawlerWeiboSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        #--调用clickHoverElement()函数时,click的延迟 
        self.clkh_click_delay    = 0.6
        #--调用clickHoverElement()函数时,hover的延迟
        self.clkh_hover_delay    = 0.6
        #----
        self.onceClickBtnMoreCount = 5
        #--main pid
        self.mainPidSplit = "id="
        #---------------------------------------------------------
        #----other
        self.cssPageBtnDict = {
                               'tailPageText':"div.wrap1>div.wrap2>div.footer>span",
                               'firstPageBtn':"div.pb_footer > div.p_thread.thread_theme_7 >div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager >a:nth-child(1)",
                               'prePageBtn':"",
                               
                               'curPageText':"div.l_container>div.content.clearfix >div.pb_footer>div.p_thread.thread_theme_7>div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager>span.tP",
                               'curPageBtn':"div.wrap2 > div.s_container.clearfix > div.pager.pager-search > span.cur",
                               
                               'nextPageBtn':"div.pb_footer > div.p_thread.thread_theme_7 >div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager >a:nth-last-child(2)",
                               'bottomAllPageNum':"div.pb_footer > div.p_thread.thread_theme_7 > div.l_thread_info > ul.l_posts_num > li.l_reply_num > span:nth-last-child(1)"
                               
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        #search button css
        self.cssSearchDict     = {
                                  'inputBox1': "div.WB_miniblog_fb >div#weibo_top_public>div.WB_global_nav.WB_global_nav_v2>div.gn_header.clearfix>div.gn_search_v2 > input.W_input",
                                  'inputBox':  "div.WB_miniblog_fb >div#pl_common_top>div.WB_global_nav >div.gn_header.clearfix>div.gn_search_v2 > input.W_input",
                                  'clkButton1': "div.WB_miniblog_fb >div#weibo_top_public>div.WB_global_nav.WB_global_nav_v2>div.gn_header.clearfix>div.gn_search_v2 > a.W_ficon",
                                  'clkButton':  "div.WB_miniblog_fb>div#plc_top>div.WB_global_nav >div.gn_header.clearfix>div.gn_search_v2 > a.W_ficon ",
                                  'editDelayMin':self.searchEditDelayMin,
                                  'editDelayMax':self.searchEditDelayMax,
                                  'waitTimeoutMs':self.clickTimeoutMs,
                                  'waitUntill':["load","domcontentloaded" ]
                                 }

        #------------------------------------------------------
        #
        mainInfo_entry = "div.WB_feed>div>div.WB_cardwrap>"
        main_reply_entry  = mainInfo_entry + "div.WB_feed_repeat>div.WB_repeat>div.repeat_list>div>div.list_box>div.list_ul>"
        #sub
        self.cssContextDict    = {
                                  
                                  #'mainInfo_nickname':mainInfo_entry + "div.WB_feed_detail>div.WB_detail>div.WB_info>a.W_f14",
                                  'mainInfo_nickname':mainInfo_entry + "div.WB_feed_detail>div.WB_detail>div.WB_info>a",
                                  'mainInfo_time'    :mainInfo_entry + "div.WB_feed_detail>div.WB_detail>div.WB_from.S_txt2>a.S_txt2",
                                  'mainInfo_title'   :mainInfo_entry + "div.WB_feed_detail>div.WB_detail>div.WB_text.W_f14",
                                  #图片
                                  'mainInfo_pic_show':mainInfo_entry + "div.WB_feed_detail>div.WB_detail>div.WB_expand_media_box>div.WB_expand_media>div.WB_media_view>div.media_show_box>ui.clearfix>li.smallcursor>div.artwork_box>div>img",
                                  #图片列表
                                  'mainInfo_pic_list':mainInfo_entry + "div.WB_feed_detail>div.WB_detail>div.WB_expand_media_box>div.WB_expand_media>div.WB_media_view>div.pic_choose_box>div.stage_box>ul.choose_box>li>a>img  ",
                                  
                                  #转发数
                                  'mainInfo_forward'   :mainInfo_entry + "div.WB_feed_handle>div.WB_handle>ul.WB_row_line >li:nth-last-child(3)>a.S_txt2>span.pos>span.line>span>em:nth-last-child(1)",
                                  #点赞数
                                  'mainInfo_stars'     :mainInfo_entry + "div.WB_feed_handle>div.WB_handle>ul.WB_row_line >li:nth-last-child(1)>a.S_txt2>span.pos>span.line.S_line1>span>em:nth-last-child(1)",
                                  #评论数
                                  'mainInfo_reply_num' :mainInfo_entry + "div.WB_feed_handle>div.WB_handle>ul.WB_row_line >li.curr>a.S_txt2>span.pos>span.line.S_line1>span>em:nth-last-child(1)",
                                  
                                  #---查看更多按钮
                                  'main_reply_btn_more':main_reply_entry + "a.WB_cardmore >span.more_txt",

                                  #--------------------------------------------------------------------------------------
                                  #---主评论
                                  
                                  #---主评论根目录
                                  'main_reply_entry'   : main_reply_entry +"div.list_li",
                                  #---nickname
                                  'main_reply_nickname' :"div.list_con>div.WB_text>a",
                                  #---id值---property = comment_id ;comment_id="4413580097488787"
                                  'main_reply_pid'      :"",
                                  #---主评论pid的属性名
                                  'main_reply_pid_pro_name': "comment_id",
                                  #---text
                                  'main_reply_text'     :"div.list_con>div.WB_text",
                                  #---time
                                  'main_reply_time'     :"div.list_con>div.WB_func>div.WB_from",
                                  #---点赞
                                  'main_reply_support'  :"div.list_con>div.WB_func>div.WB_handle>ul.clearfix>li:nth-last-child(1)>span.line>a>span>em:nth-last-child(1)",
                                  
                                  
        
                                  #------
                                  #------------------------------------------------------------------------------------
                                  #---共n条子回复按钮
                                  'sub_reply_btn_more':"div.list_con>div.list_box_in>div.list_ul>div.list_li_v2>div.WB_text>a",
                                  #----子评论根目录
                                  'sub_reply_entry': "div.list_con>div.list_box_in>div.list_ul>div.list_li",
                                  #-----subreply id  property = comment_id ;comment_id="4413581661404210"
                                  #----子评论的pid
                                  'sub_reply_pid':  "",
                                  #----子评论pid的属性名
                                  'sub_reply_pid_pro_name':"comment_id",
                                  #----nickname
                                  'sub_reply_nickname': "div.list_con>div.WB_text>a",
                                  #----text,获取的是nickname和text,:分隔，需要取出text
                                  'sub_reply_text':"div.list_con>div.WB_text ",
                                  #----time 格式:9月3日 19:33 ,没有年
                                  'sub_reply_time':"div.list_con>div.WB_func>div.WB_from",
                                  #-------点赞
                                  'sub_reply_support':"div.list_con>div.WB_func>div.WB_handle>ul.clearfix>li:nth-last-child(1)>span.line>a.S_txt1>span>em:nth-last-child(1)",
                                
                                  
                                 }
        
        self.cssLoginDict      ={
                                 'user_name':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-userName >input.pass-text-input.pass-text-input-userName",
                                 'password' :"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-password >input.pass-text-input.pass-text-input-password",
                                 'clk_button':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-submit >input.pass-button.pass-button-submit",
                                 'pageLoginExit':"body.skin_normal>div#passport-login-pop > div.tang-foreground > div.tang-title.tang-title-dragable>div.buttons>a.close-btn "
                                 }
        
        #log
        logpath = "weibo/sub/" + str(index) 
        self.log_inits(logpath,2,2,logging.INFO)

    
    #--------------------------------------------------------------------------------------  
    #  
    async def  login(self,page):
      
       return RetVal.Suc.value
    #--------------------------------------------------------------------------------------  
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeiboSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.dealCompoundwordCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerWeiboSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    #--------------------------------------------------------------------------------------
    #子抓取--按网址抓取    
    async def  dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerWeiboSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.dealDefUrlCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerWeiboSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf

    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def dealDefUrlCrawlerPage(self,page,crawlerInfo,index):
        self.printLogInfo("CrawlerWeiboSub->dealDefUrlCrawlerPage() : enter")
        
        replyBuf = []
        ret,replyBuf = await self.grapAllPageData(page,crawlerInfo,index)
        
        self.printLogInfo("CrawlerWeiboSub->dealDefUrlCrawlerPage() : exit")
        return ret,replyBuf

    #--------------------------------------------------------------------------------------
    #----按关键字抓取
    async def  dealCompoundwordCrawlerPage(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerWeiboSub->dealCompoundwordCrawlerPage() : enter")

        replyBuf = []
        ret,replyBuf = await self.grapAllPageData(page,crawlerInfo,index)
        
        self.printLogInfo("CrawlerWeiboSub->dealCompoundwordCrawlerPage() : exit")
        
        ret = RetVal.Suc.value
        return ret,replyBuf
    
    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def grapAllPageData(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerWeiboSub->grapAllPageData() : enter")
    
        replyBuf = []
        replyBuf1= []
        replyBuf2= []
        
        isFinish     = 0
        strCurYear   = "2019"
        ret          = 0
        curCount     = 0
        maxCount     = 8000
    
        #---------------------------main info
        ret,replyInfo = await self.grapMainInfo(page,crawlerInfo)
        if ret == RetVal.Suc.value:
            replyBuf.append(replyInfo)
            strCurYear = CommonTool.strSplitIndex(replyInfo.publishTime,"-",0)
        self.printReplyInfo(replyInfo,crawlerInfo)
        
        
        #--grap sub info
        while curCount < maxCount:
            curCount += 1
            
            ret,isFinish,replyBuf1 = await self.grapAllReplyInfo(page,crawlerInfo,strCurYear)
            if ret == RetVal.Suc.value:
                replyBuf.extend(replyBuf1)
            elif ret == RetVal.FailExitAsNovel.value:
                replyBuf.extend(replyBuf1)
                break
                       
            if isFinish == 1:
                break
        #----------------------------------------------
        if ret != RetVal.FailExitAsNovel.value:
            if len(replyBuf) > 0:
                ret = RetVal.Suc.value
            else:
                ret = RetVal.Fail.value
        
        self.printLogInfo("CrawlerWeiboSub->grapAllPageData() : exit")

        return ret,replyBuf

     #----------------------------------------------------------------------------------------
     #--返回值:
     #        isFinish: =1,抓取完成;=0,需要继续抓取 
    async def grapAllReplyInfo(self,page,crawlerInfo,strTimeYear):

        self.printLogInfo("CrawlerWeiboSub->grapAllReplyInfo() : enter")

        isFinish  = 0
        ret       = RetVal.Fail.value
        replyBuf  = []
        replyBuf1 = []
        #---------------------------main reply info
        #--click more
        ret1,isFinish = await self.clickButtonMore(page)

        #-----main info
        selector          = self.cssContextDict["main_reply_entry"]
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

               #检查小说
               ret = self.IsTerminateGrapAsNovel(crawlerInfo,replyInfo.text)
               if ret == RetVal.FailExitAsNovel.value:
                   break

               #----sub reply
               crawlerInfo.p_parentPageItemNoSub = crawlerInfo.p_curPageItemNo
               ret1,replyBuf1 = await self.grapSubReplyInfo(page,item,crawlerInfo,strTimeYear)
               if ret1 == RetVal.Suc.value:
                   replyBuf.extend(replyBuf1)
                   self.printReplyInfoBuf(replyBuf1,crawlerInfo)
        
        #--------------------------------------------
        if ret != RetVal.FailExitAsNovel.value:
            retcount = len(replyBuf)
            if retcount > 0:
                ret = RetVal.Suc.value
            else:
                ret = RetVal.Fail.value

        self.printLogInfo("CrawlerWeiboSub->grapAllReplyInfo() : exit")

        return ret,isFinish,replyBuf
        
    #----------------------------------------------------------------------------------------
    #---抓取主回复的子回复
    async def grapSubReplyInfo(self,page,element,crawlerInfo,strTimeYear):

        self.printLogInfo("CrawlerWeiboSub->grapSubReplyInfo() : enter")  

        ret  = RetVal.Fail.value
        replyBuf  = []
        
        #---click
        selector  = self.cssContextDict["sub_reply_btn_more"]
        #await self.pyteerEx.clickHoverElement(element,selector,self.clkh_click_delay,self.clkh_hover_delay)
        
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
        
        self.printLogInfo("CrawlerWeiboSub->grapSubReplyInfo() : exit")    
        
        return ret,replyBuf
    #----------------------------------------------------------------------------------------
    #---抓取主回复的子回复
    async def grapItemSubReplyInfo(self,page,element,crawlerInfo,strTimeYear):
        self.printLogInfo("CrawlerWeiboSub->grapItemSubReplyInfo() : enter")
        
        ret  = RetVal.Suc.value
        ret1 = RetVal.Suc.value
        
        cssNickName       = self.cssContextDict["sub_reply_nickname"]
        cssReplyPid       = self.cssContextDict["sub_reply_pid"]
        replyPidProName   = self.cssContextDict["sub_reply_pid_pro_name"]
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

        #--pid property = usercard ;val = id=6068935618
        propertyName = replyPidProName
        ret1,curText = await self.pyteerEx.getElementProDef(page,element,propertyName,cssReplyPid)
        curText      = curText.strip()
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(crawlerInfo.pid,curText)

        #---text
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyText)
        replyInfo.text = self.getReplyTextAsSplit(curText)

        #---time 格式: 9月4日 16:30
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        replyInfo.publishTime = self.getReplyTime(curText,strTimeYear)
            
        #--start
        ret1,curText    = await self.pyteerEx.getElementContext(element,cssReplySupport)
        replyInfo.stars = CommonTool.strToInt(curText)
            
        #---------------------------------------------------

        self.printLogInfo("CrawlerWeiboSub->grapItemSubReplyInfo() : exit")
        
        
        return ret,replyInfo    


    #----------------------------------------------------------------------------------------
    #---抓取主回复
    async def grapItemMainReplyInfo(self,page,element,crawlerInfo,strTimeYear):

        self.printLogInfo("CrawlerWeiboSub->grapMainReplyInfo() : enter")
        
        ret  = RetVal.Suc.value
        ret1 = RetVal.Suc.value
        
        cssNickName       = self.cssContextDict["main_reply_nickname"]
        cssReplyPid       = self.cssContextDict["main_reply_pid"]
        replyPidName      = self.cssContextDict["main_reply_pid_pro_name"]
        cssReplyText      = self.cssContextDict["main_reply_text"]
        cssReplyTime      = self.cssContextDict["main_reply_time"]
        cssReplySupport   = self.cssContextDict["main_reply_support"]
        
        
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

        #--pid property = comment_id ; comment_id="4413581661404210"
        propertyName = replyPidName
        ret1,curText = await self.pyteerEx.getElementProDef(page,element,propertyName,cssReplyPid)
        curText      = curText.strip()
        replyInfo.pid = curText
        replyInfo.locateSymbol  = GrapReplyInfo.getLocateSymbolStr(curText,"")

        #---text
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyText)
        replyInfo.text = self.getReplyTextAsSplit(curText)

        #---time 格式: 9月4日 16:30
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplyTime)
        replyInfo.publishTime = self.getReplyTime(curText,strTimeYear)
            
        #--support
        ret1,curText   = await self.pyteerEx.getElementContext(element,cssReplySupport)
        replyInfo.stars = CommonTool.strToInt(curText)
            
        #---------------------------------------------------
        
        self.printLogInfo("CrawlerWeiboSub->grapMainReplyInfo() : exit")

        self.printReplyInfo(replyInfo,crawlerInfo)

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
    #---获取时间: 源格式:9月3日 19:30  ;目标格式:2019-09-03 19:30:00 
    def getReplyTime(self,timeText,strTimeYear):
        
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

    #----------------------------------------------------------------------------------------
    #---点查看更多按钮
    async def clickButtonMore(self,page):

        self.printLogInfo("CrawlerWeiboSub->clickButtonMore() : enter")

        ret        = RetVal.Suc.value
        isFinish   = 0
        selector   = self.cssContextDict["main_reply_btn_more"]

        count    = 8000
        curCount = 0
        while count > 0:

            count -= 1
            curCount += 1
            
            ret = await self.pyteerEx.clickHoverElement(page,selector,self.clkh_click_delay,self.clkh_hover_delay)
            if ret == RetVal.Suc.value:
                pass    
            else:
                self.printLogInfo("CrawlerWeiboSub->clickButtonMore() :success and exit, not find more button")
                isFinish = 1
                break
            
            #-------------
            #if curCount >self.onceClickBtnMoreCount:
            #    isFinish = 0
            #    break
            #-------------
            continue
        #------------------------------------------
        #--while end
        
        ret = RetVal.Suc.value
        
        self.printLogInfo("CrawlerWeiboSub->clickButtonMore() : exit")

        return ret,isFinish

    
    #----------------------------------------------------------------------------------------
    #---抓取主信息
    #---时间-是title属性,格式：2019-09-03 19:30,需要手动加00
    #---文本为图片->先抓有多个图片的，没有则抓单个图片的
    async def grapMainInfo(self,page,crawlerInfo):
        
        self.printLogInfo("CrawlerWeiboSub->grapMainInfo() : enter")

        ret = RetVal.Suc.value

        replyInfo      = GrapReplyInfo()
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        replyInfo.href = crawlerInfo.url
        replyInfo.pageUrl = crawlerInfo.url

        crawlerInfo.p_parentPageItemNo = 0
        replyInfo.parentContentId = crawlerInfo.p_parentPageItemNo
        crawlerInfo.p_curPageItemNo = 1
        replyInfo.contentId       = crawlerInfo.p_curPageItemNo
        
        #---publisher
        selector    = self.cssContextDict["mainInfo_nickname"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        replyInfo.publisher = CommonTool.strStripRet(curText)
        
        #---time
        propertyName = "title"
        selector    =  self.cssContextDict["mainInfo_time"]
        ret,curText =  await self.pyteerEx.getElementProDef(page,page,propertyName,selector)
        curText     =   CommonTool.strStripRet(curText);
        replyInfo.publishTime =  curText + ":00"
        
        #---title
        selector    = self.cssContextDict["mainInfo_title"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        curText     =  CommonTool.strStripRet(curText)
        replyInfo.main_title   = curText
        crawlerInfo.main_title = curText

        #----context
        
        propertyName = "src"
        selector     =  self.cssContextDict["mainInfo_pic_list"]
        ret,picBuf   =  await self.pyteerEx.getElementAllProDef(page,page,propertyName,selector)
        
        if len(picBuf) > 0:
            for subPic in picBuf:
               replyInfo.text +=    GrapReplyInfo.getPicWrapStr(subPic)  
        else:  #抓单个图片
            selector    =  self.cssContextDict["mainInfo_pic_show"]
            ret,curText =  await self.pyteerEx.getElementProDef(page,page,propertyName,selector)
            if ret == RetVal.Suc.value:
                replyInfo.text  =  GrapReplyInfo.getPicWrapStr(curText)
        
        #----转发数
        selector           = self.cssContextDict["mainInfo_forward"]
        ret,curText        = await self.pyteerEx.getElementContext(page,selector)
        replyInfo.forwards = CommonTool.strToInt(curText)
        
        #----点赞数
        selector           = self.cssContextDict["mainInfo_stars"]
        ret,curText        = await self.pyteerEx.getElementContext(page,selector)
        replyInfo.stars    = CommonTool.strToInt(curText)
        
        #-----评论数
        selector           = self.cssContextDict["mainInfo_reply_num"]
        ret,curText        = await self.pyteerEx.getElementContext(page,selector)
        replyInfo.comments = CommonTool.strToInt(curText)

        self.printLogInfo("CrawlerWeiboSub->grapMainInfo() : exit")
        
        
        return ret,replyInfo


    
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
    
    #--------------------------------------------------------------------------------------
    #
    async def  dealMainOther(self,page,crawlerInfo):
        
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
        
        ret = await self.pyteerEx.waitPageAll(page,cssList,10)

        self.printLogInfo("CrawlerTiebaMain->dealMainScrollBefor() : exit ret={}".format(ret))
        
        return ret
    #--------------------------------------------------------------------------------------
    async def  waitforPageLoad(self,page):
        return RetVal.Suc.value
    
    
    
    
    
    


    