#-------------  baidu_tieba_sub.py
#--百度贴吧

import sys,os
import asyncio
import random
import time
import logging
from   pyppeteer import launch

sys.path.append("..")

from  struct_def                 import *
from  crawlers.search_base_sites import *
from  pyteerex.pyppeteer_ex      import *
from  common.tools               import *

#---------------------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
class   CrawlerTiebaSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):
        
        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        
        #---------------------------------------------------------
        #----other

        #--pid,sid,
        self.mainPidSplit = "post_content_"

        
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
        
        #sub
        self.cssContextDict    = {
                                  'mainTitle':"div.left_section > div#j_core_title_wrap > div.core_title.core_title_theme_bright>h1.core_title_txt ",
                                  'mainTitle1':"div.left_section > div.core_title_wrap_bright>h3.core_title_txt",
                                  #--2019.9.30 修改mainReply
                                  #'mainReply':"div.p_postlist > div.l_post.j_l_post.l_post_bright ",
                                  'mainReply':"div.p_postlist > div.l_post",
                                  'mainReply_pid':"div.d_post_content_main >div.p_content > cc > div.d_post_content.j_d_post_content",
                                  #'mainReply_nickname':"div.d_author > ul.p_author > li.d_name > a.p_author_name.j_user_card",
                                  'mainReply_nickname':"div.d_author > ul.p_author > li.d_name > a.p_author_name ",
                                  'mainReply_pid':"div.d_post_content_main >div.p_content > cc > div.d_post_content",
                                  'mainReply_userHref':"div.d_author > ul.p_author > li.d_name > a.p_author_name.j_user_card",
                                  'mainReply_userName':"div.d_author > ul.p_author > li.d_name > a.p_author_name.j_user_card",
                                  
                                  #----主回复的子回复数量
                                  'mainReply_subReply_count':"div.d_post_content_main>div.core_reply>div.core_reply_wrapper>div.core_reply_content>ul.j_lzl_m_w>li.lzl_single_post",

                                  'mainReply_time':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > ul.p_tail >li:nth-last-child(1) ",
                                  'mainReply_floor':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > ul.p_tail>li:nth-last-child(2) ",
                                  'mainReply_time1':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > div.post-tail-wrap >span:nth-last-child(1)",
                                  'mainReply_floor1':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > div.post-tail-wrap >span:nth-last-child(2)",
                                  #ad广告
                                  'mainReply_ad':"div.d_post_content_main>div.p_content>div.d_post_content>div.middle_image_content>div.ad_bottom_view>span.label_text",
                                  'mainReply_ad1':"div.d_post_content_main>div.ad_bottom_view>span.label_text",
                                  'mainReply_text':"div.d_post_content_main >div.p_content > cc > div.d_post_content.j_d_post_content",
                                  'reply_image':"img.BDE_Image",

                                  'subReply'      :"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.j_lzl_container.core_reply_wrapper > div.j_lzl_c_b_a.core_reply_content >ul.j_lzl_m_w>li.lzl_single_post.j_lzl_s_p",
                                  'subReply_sid'  :"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.j_lzl_container.core_reply_wrapper > div.j_lzl_c_b_a.core_reply_content >ul.j_lzl_m_w>li.lzl_single_post.j_lzl_s_p",
                                  'subReply_userHref':"a.j_user_card.lzl_p_p",
                                  'subReply_nickname':"div.lzl_cnt > a.at.j_user_card ",
                                  'subReply_text':    "div.lzl_cnt > span.lzl_content_main",
                                  'subReply_time':    "div.lzl_cnt > div.lzl_content_reply > span.lzl_time"
                                  
                                 }
        
        self.cssLoginDict      ={
                                 'user_name':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-userName >input.pass-text-input.pass-text-input-userName",
                                 'password' :"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-password >input.pass-text-input.pass-text-input-password",
                                 'clk_button':"div.login_form.tang-pass-login > form.pass-form.pass-form-normal >p.pass-form-item.pass-form-item-submit >input.pass-button.pass-button-submit",
                                 'pageLoginExit':"div#passport-login-pop > div.tang-foreground > div.tang-title.tang-title-dragable>div.buttons>a.close-btn "
                                 }
        
        #log
        logpath = "tieba/sub/" + str(index) 
        self.log_inits(logpath,1,1,logging.INFO)

    #--------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------------
    #子抓取--按楼层抓取
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        
        self.printLogInfo("CrawlerTiebaSub->dealSubCrawlerAsFloor() : enter")

        ret,replyInfoBuf = await self.dealCompoundwordCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerTiebaSub->dealSubCrawlerAsFloor() : exit ret={}".format(ret))

        return ret,replyInfoBuf
    

    #--------------------------------------------------------------------------------------
    #子抓取--按楼层抓取    
    async def  dealSubCrawlerAsDefUrl(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerTiebaSub->dealSubCrawlerAsDefUrl() : enter")
        
        ret,replyInfoBuf = await self.dealDefUrlCrawlerPage(page,crawlerInfo,index)

        self.printLogInfo("CrawlerTiebaSub->dealSubCrawlerAsDefUrl() : exit ret={}".format(ret))

        return ret,replyInfoBuf

    #--------------------------------------------------------------------------------------
    # crawler a web page as compoundword
    async def  dealCompoundwordCrawlerPage(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerTiebaSub->dealCompoundwordCrawlerPage() : enter")

        replyBuf = []
        ret,replyBuf = await self.dealSubCrawlerPageBase(page,crawlerInfo,index)
        
        self.printLogInfo("CrawlerTiebaSub->dealCompoundwordCrawlerPage() : exit")
        
        return ret,replyBuf
    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def dealDefUrlCrawlerPage(self,page,crawlerInfo,index):
        self.printLogInfo("CrawlerTiebaSub->dealDefUrlCrawlerPage() : enter")
        
        replyBuf = []
        ret,replyBuf = await self.dealSubCrawlerPageBase(page,crawlerInfo,index)
        
        self.printLogInfo("CrawlerTiebaSub->dealDefUrlCrawlerPage() : exit")
        return ret,replyBuf
    
    #--------------------------------------------------------------------------------------    
    async def  login(self,page):
       """
       self.printLogInfo("CrawlerTiebaSub->login() : enter")
       selectName = self.cssLoginDict["user_name"]
       selectPass = self.cssLoginDict["password"]
       selectBtn  = self.cssLoginDict["clk_button"]
       user_name  = "lilyhepp"
       password   = "lily2019"
       
       #await page.type(selectName, user_name, {'delay': self.input_time_random() - 50})   # delay是限制输入的时间
       #await page.type(selectPass, password,  {'delay': self.input_time_random()})
       await asyncio.sleep(1)
       await self.pyteerEx.scroolTop(page)
       await asyncio.sleep(1)
     
       
       await page.click(selectName)
       await asyncio.sleep(1)
       await page.type(selectName, user_name, {'delay': 300})   # delay是限制输入的时间
       await asyncio.sleep(1)
       
       await page.click(selectPass)
       await page.type(selectPass, password,  {'delay': 400})
       await asyncio.sleep(1)

       #await page.click(selectBtn)
       await  self.pyteerEx.clickNavigate(page,selectBtn)
       #await asyncio.sleep(4)

       self.printLogInfo("CrawlerTiebaSub->login() : exit")
       """
       return RetVal.Suc.value

    
    #--------------------------------------------------------------------------------------
    # goto to next page
    # return:
    #   isFinish   = 0：继续抓取下一页
    #   isFinish   = 1: 完成抓取
    #   isFinish   = 2: 退出子循环，在新的browser中打开下一页
    #   isFinish   = 3: 抓取失败，退出      
    async def  dealSubGotoNextPage(self,page,pageNo,maxPageNum):
        
        self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : enter ".format(pageNo))
        
        isContinue = 0
        isFinish   = RetVal.GrapSucRepeat.value
        nAllPageNum = 0
        ret         = RetVal.Suc.value
        strRet      = ""
        url_next    = ""
        cssAllPageNum = self.cssPageBtnDict["bottomAllPageNum"]
        cssCurPage    = self.cssPageBtnDict["curPageText"]
        selectorBtn   = self.cssPageBtnDict["nextPageBtn"]
        
        #current page
        ret,strRet = await self.pyteerEx.getElementContext(page,cssCurPage )
        if ret != RetVal.Suc.value:
            nCurPage = 1
        else:
            nCurPage = CommonTool.strToInt(strRet.strip())
        
        self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : nCurPage={} ".format(pageNo,nCurPage))
        
        #all page
        ret,strRet = await self.pyteerEx.getElementContext(page,cssAllPageNum )

        if ret == RetVal.Suc.value:

                nAllPageNum = CommonTool.strToInt(strRet.strip())

                self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : allCurPage={} ".format(pageNo,nAllPageNum))
                #
                if nAllPageNum > nCurPage:
                    
                    ret ,element = await self.pyteerEx.getElement(page,selectorBtn)

                    if ret == RetVal.Fail.value:
                        isFinish   = RetVal.GrapSuc.value
                    elif ret > RetVal.Fail.value:
                        isFinish   = RetVal.GrapFailRepeat.value
                    else:

                        url_next = await self.pyteerEx.getElementHref(page,selectorBtn)

                        ret  = await self.pyteerEx.clickNavigate(page,selectorBtn,self.paraClickNextPage["timeoutMs"],self.paraClickNextPage["waitUntil"])
                        if ret == RetVal.Suc.value:
                        
                            self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : success to goto next page ".format(pageNo))
                            await self.pyteerEx.scroolBottom(page)

                            #close 
                            cssVal = self.cssLoginDict["pageLoginExit"]
                            ret1 = await self.pyteerEx.waitPage(page,cssVal,6)
                            if ret1 == RetVal.Suc.value:
                                ret1 = await self.pyteerEx.clickElement(page,cssVal )
                                if ret1 == RetVal.Suc.value:
                                    self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : success to close windows ".format(pageNo))
                                    isFinish = RetVal.GrapSucRepeat.value
                                else:
                                    isFinish = RetVal.GrapFailRepeat.value
                                """
                                ret1 = await self.pyteerEx.clickNavigate(page,cssVal,8000,["load"])
                                if ret1 == RetVal.Suc.value:
                                
                                    self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : success to close windows ".format(pageNo))
                                    isFinish = RetVal.GrapSucRepeat.value
                                else:
                                    isFinish = RetVal.GrapFailRepeat.value
                                """
                            else:
                                isFinish = RetVal.GrapSucRepeat.value

                        else:   #失败，打开next page的url
                            isFinish = RetVal.GrapFailRepeat.value
                else:  #抓取页面完成
                    isFinish   = RetVal.GrapSuc.value
        else: #exception
            isFinish   = RetVal.GrapFailExit.value

        self.getLogInfo().show("CrawlerTiebaSub->dealSubGotoNextPage()->page={} : exit ".format(pageNo))

        return isFinish,url_next    
    
    #--------------------------------------------------------------------------------------
    #
    async def  dealMainOther(self,page,crawlerInfo):
        """
        print("CrawlerTiebaSub->dealMainOther():enter")
        ret          = 1
        strMainTitle =""

        ret,strMainTitle = await self.grabSubPageMainTitle(page)
        print(strMainTitle)
        if ret != 0:
            return 1
        

        """
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #检查当前页是否是第一页，不是则获取第一页的url
    # ret = 0: 当前页是首页
    # ret = 1: 当前页不是首页,获取了首页的地址
    # ret = 2: 当前页不是首页,获取首页地址失败
    async def  checkFirstPage(self,page):

        self.printLogInfo("CrawlerTiebaSub->checkFirstPage() : enter")

        ret  = RetVal.Fail.value
        strTitle = ""
        url      = ""
        selector = self.cssPageBtnDict["firstPageBtn"]

        ret1,element = await self.pyteerEx.getElement(page,selector)

        if element is not None:
            ret1,strTitle  = await self.pyteerEx.getElementContext(element)
            
            ret1,url       = await self.pyteerEx.getElementHref(element)

            self.printLogInfo("CrawlerTiebaSub->checkFirstPage() : title={}".format(strTitle))
        else:  #current page is first page
            return RetVal.Suc.value, url
        
        if strTitle == "首页":
            ret = RetVal.FailRepeat.value

        
            
        self.printLogInfo("CrawlerTiebaSub->checkFirstPage() : exit")

        return ret,url


    #--------------------------------------------------------------------------------------
    async def  waitforPageLoad(self,page):
        
        self.printLogInfo("CrawlerTiebaSub->waitforPageLoad() : enter")
        
        ret = await self.pyteerEx.waitPage(page,self.cssPageBtnDict["bottomAllPageNum"],1)
        
        self.printLogInfo("CrawlerTiebaSub->waitforPageLoad() : exit")

        return ret

    #--------------------------------------------------------------------------------------
    #--获取标题
    async def  getMainTitleInfo(self,page,crawlerInfo,index):

        self.getLogInfo().show("CrawlerTiebaSub->getMainTitleInfo()->index={}: enter ".format(index))
        
        #title
        selector    =  self.cssContextDict["mainTitle"]
        ret,curText =  await self.pyteerEx.getElementContext(page,selector)
        curText     =  curText.strip()
        
        if ret != RetVal.Suc.value:
            self.getLogInfo().show("CrawlerTiebaSub->getMainTitleInfo()->index={}: get title fail,and get title1 ".format(index))
            selector    =  self.cssContextDict["mainTitle1"]
            ret,curText =  await self.pyteerEx.getElementContext(page,selector)
            curText     =  curText.strip()
            if ret != RetVal.Suc.value:
               self.getLogInfo().show("CrawlerTiebaSub->getMainTitleInfo()->index={}: get title1 fail ".format(index))

        
        #---   
        if len(curText) > 0:
            crawlerInfo.main_title = curText
            ret = RetVal.Suc.value
        else:
            ret = RetVal.Fail.value

        self.getLogInfo().show("CrawlerTiebaSub->getMainTitleInfo()->index={}: exit ,title={}".format(index,crawlerInfo.main_title))
        
        return ret


    #----------------------------------------------------------------------------------------
    #---抓取指定网页评论的更新
    async def dealSubCrawlerPageBase(self,page,crawlerInfo,index):

        self.printLogInfo("CrawlerTiebaSub->dealDefUrlCrawlerPage() : enter")
        self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: enter keyword={} ".format(index,crawlerInfo.keyword))
        self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: enter url={} ".format(index,crawlerInfo.url))
        
        
        strMainTitle = ""
        replyBuf = []
        replyBuf1= []
        replyBuf2= []

        strUrl         = crawlerInfo.url
        strCompoundword= crawlerInfo.compoundword

        ret          = RetVal.Suc.value
        ret1         = RetVal.Suc.value
        itemCount    = 0
        selector     = self.cssContextDict["mainReply"]
        
        #---
        curPageNo             = await self.getCurPageVal(page)
        crawlerInfo.curPageNo = curPageNo
        
        #----get title
        if curPageNo == 1:#首页
            self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: getMainTitleInfo begin ".format(index))
            
            crawlerInfo.p_curPageItemNo    = 0
            crawlerInfo.p_parentPageItemNo = 0
            
            ret1 = await self.getMainTitleInfo(page,crawlerInfo,index)
            if ret1 != RetVal.Suc.value:
                self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: getMainTitleInfo->page =1,get title fail,exit ".format(index))
                return RetVal.FailExit.value,replyBuf

            self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: getMainTitleInfo end ".format(index))
        elif curPageNo == 0: #异常
            self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: getMainTitleInfo->page =0,fail,exit ".format(index))
            return RetVal.FailExit.value,replyBuf

        else:                #标题为空
            if len(crawlerInfo.main_title ) < 1:
                self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: getMainTitleInfo->page ={},title is empty,exit ".format(index,curPageNo))
                return RetVal.FailExit.value,replyBuf


        #-----
        itemCount = 0
        ret1,elementList = await self.pyteerEx.getElementAll(page,selector)
        for item in elementList:
            itemCount += 1

            #---子页问题回复抓取上限 
            if self.terminateSubPageMaxCount == crawlerInfo.vscroll_grap_count:
                return RetVal.FailExitCountLimit.value,replyBuf

            crawlerInfo.vscroll_grap_count +=1
            ret1,replyInfo = await self.grabMainReplyInfo_new(page,item,strUrl,crawlerInfo.grap_data,crawlerInfo)
            if ret1 == RetVal.Fail.value:
                continue
            elif ret1 == RetVal.FailExit.value:
                return RetVal.FailExit.value,replyBuf
            #----问题描述和问题内容需要检查有无关键词
            if 1 == itemCount: 
                temp = []
                temp.append(replyInfo)
                result = self.checkIncludeKeyword(crawlerInfo,temp)
                if result != RetVal.Suc.value:
                    self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: title and text is empty,terminate grap ".format(index))
                    self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: keyword={} ".format(index,crawlerInfo.keyword))
                    self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: title={} ".format(index,crawlerInfo.main_title))
                    self.getLogInfo().show("CrawlerTiebaSub->dealSubCrawlerPageBase()->index={}: context={} ".format(index,replyInfo.text))
                    return RetVal.FailExitNotFindKeyword.value,replyBuf

            if ret1 == RetVal.Suc.value: #抓取到新数据或修改的数据
                replyBuf.append(replyInfo)
                #--判断小说
                ret = self.IsTerminateGrapAsNovel(crawlerInfo,replyInfo.text)
                if ret == RetVal.FailExitAsNovel.value:
                    break
                
                self.printReplyInfo(replyInfo,crawlerInfo)

            """
            #---crawler sub reply
            if ret <= RetVal.Fail.value:
                #sub
                crawlerInfo.p_parentPageItemNoSub = crawlerInfo.p_curPageItemNo
                ret1,replyBuf1 = await self.grabSubReplyInfo_new(page,item,strUrl,replyInfo.pid,crawlerInfo.grap_data,crawlerInfo)
                if ret1 == RetVal.Suc.value:
                    replyBuf.extend(replyBuf1)
                    self.printReplyInfo(replyInfo,crawlerInfo)
            else: #error
                continue
            """
        #---------------------------------------------end for
        
    
        if ret != RetVal.FailExitAsNovel.value:
            retcount = len(replyBuf)
            if retcount > 0:
                ret = RetVal.Suc.value
            else:
                ret = RetVal.Fail.value

        self.printLogInfo("CrawlerTiebaSub->dealSubCrawlerPageBase() : exit")

        return ret ,replyBuf
        
    #------------------------------------------------------------------------------
    #get main title
    async def  grabSubPageMainTitle(self,page):

        ret = RetVal.Fail.value
        strTitle = ""
        selector = self.cssContextDict["mainTitle"]
        element = await page.querySelector(selector)

        if element is not None:
            title_str = await (await element.getProperty('textContent')).jsonValue()
            ret = RetVal.Suc.value
        
        return ret,title_str

    #--------------------------------------------------------------------------------------
    #get main repaly                                                                                                     
    def  getImgStrings(self,imgBuf):
        imgStr = ""
        for item in imgBuf:
            imgStr += GrapReplyInfo.getPicWrapStr(item)

        return imgStr
    #--------------------------------------------------------------------------------------
    #获取主回复的楼层和时间字符串
    def  getMainTimeFloor(self,strTimeFloor):
          pass
    #--------------------------------------------------------------------------------------
    #get main repaly 
    # ret = 0: 抓取到新数据,或修改的数据
    # ret = 1: 数据已存在
    # ret = 2: 出错                                                                                                    
    async def  grabMainReplyInfo_new(self,page,elementHandle,strUrl,grap_data_dict,crawlerInfo):
        
        self.printLogInfo("CrawlerTiebaSub->grabMainReplyInfo_new() : enter")

        ret  = RetVal.Suc.value
        ret1 = 0
        ret2 = 0
        replyInfo_last = None
        replyInfo = GrapReplyInfo()
        
        selector               = self.cssContextDict["mainReply_ad"]
        ret2,element            = await self.pyteerEx.getElement(elementHandle,selector)
        if ret2 == RetVal.Suc.value:
            return  RetVal.Fail.value,replyInfo
        else:
            selector               = self.cssContextDict["mainReply_ad1"]
            ret2,element           = await self.pyteerEx.getElement(elementHandle,selector)
            if ret2 ==  RetVal.Suc.value:
                return  RetVal.Fail.value,replyInfo

        #datapid
        selector               = self.cssContextDict["mainReply_pid"]
        ret2,curText           = await self.pyteerEx.getElementId(elementHandle,selector)
        replyInfo.pid          = self.getMainPid(curText ,self.mainPidSplit)
        
        #time
        selector               = self.cssContextDict["mainReply_time"]
        ret2,curText           = await self.pyteerEx.getElementContext(elementHandle,selector)
        curText                = GrapReplyInfo.dealStr(curText )
        replyInfo.publishTime  = curText + ":00"
        if ret2 != RetVal.Suc.value:
            selector                = self.cssContextDict["mainReply_time1"]
            ret2,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
            curText                 = GrapReplyInfo.dealStr(curText )
            replyInfo.publishTime   = curText + ":00"
        
        #---check
        ret1,replyInfo_last = grap_data_dict.isExistKeyEx(strUrl,replyInfo.pid,"",replyInfo.publishTime )
        if ret1 == 2:   #same
            ret = RetVal.Fail.value 
        elif ret1 == 0: #不存在    
            #publisher
            selector               = self.cssContextDict["mainReply_nickname"]
            ret2,curText           = await self.pyteerEx.getElementContext(elementHandle,selector)
            curText                = curText.strip()
            if (ret2 == RetVal.Suc.value) and (len(curText) > 0):
                replyInfo.publisher     = curText
            else:
                if crawlerInfo.p_parentPageItemNo == 0:
                    ret3 = RetVal.FailExit.value
                else:
                    ret3 = RetVal.Fail.value
                return  ret3,replyInfo

            #user_href
            selector               = self.cssContextDict["mainReply_userHref"]
            ret2,curText            = await self.pyteerEx.getElementHref(elementHandle,selector)
            replyInfo.userHref     = GrapReplyInfo.dealStr(curText )
        
            #user_name
            ret2,curText            = await self.grabMainUserName(page,elementHandle)
            replyInfo.userName     = GrapReplyInfo.dealStr(curText )
        
            #floor
            selector               = self.cssContextDict["mainReply_floor"]
            ret2,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
            replyInfo.main_floor   = GrapReplyInfo.dealStr(curText )
            if ret2 != RetVal.Suc.value:
                selector               = self.cssContextDict["mainReply_floor1"]
                ret2,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
                replyInfo.main_floor   = GrapReplyInfo.dealStr(curText )

        elif ret1 == 1: #update
            replyInfo.copyfrom(1,replyInfo_last)

        #--------    
        if ret1 != 2: #get text    
            #text
            selector               = self.cssContextDict["mainReply_text"]
            ret2,curText           = await self.pyteerEx.getElementContext(elementHandle,selector)
            curText                = GrapReplyInfo.dealStr(curText )
            ret2, imgBuf           = await self.grabAllImage(page,elementHandle)
            if ret2  == RetVal.Suc.value:
                curText            += self.getImgStrings(imgBuf)
            replyInfo.text         = curText
        
        ret1,elementList = await self.pyteerEx.getElementAll(elementHandle,self.cssContextDict["mainReply_subReply_count"]) 
        if ret1 == RetVal.Suc.value:
            replyInfo.comments  = len(elementList)
        
        replyInfo.isMain    = 1
        replyInfo.href      = strUrl
        replyInfo.pageUrl   = self.getPageUrl(strUrl)
        
        replyInfo.parentContentId = crawlerInfo.p_parentPageItemNo
        crawlerInfo.p_curPageItemNo += 1
        replyInfo.contentId       = crawlerInfo.p_curPageItemNo
        replyInfo.copyAsCrawlerInfo(crawlerInfo)
        #--第一条记录当作标题的回复
        if crawlerInfo.p_parentPageItemNo == 0:
            crawlerInfo.p_parentPageItemNo = 1
            replyInfo.main_title = crawlerInfo.main_title
            
        self.printLogInfo("CrawlerTiebaSub->grabMainReplyInfo_new() : exit")
        
        ret = RetVal.Suc.value
        return ret,replyInfo
    #--------------------------------------------------------------------------------------
    #get main repaly                                                                                                     
    async def  grabMainReplyInfo(self,page,elementHandle,strUrl):
        
        self.printLogInfo("CrawlerTiebaSub->grabMainReplyInfo() : enter")

        ret  = RetVal.Fail.value
        replyInfo = GrapReplyInfo()

        #nick_name
        selector               = self.cssContextDict["mainReply_nickname"]
        ret,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
        replyInfo.publisher     = GrapReplyInfo.dealStr(curText )

        #user_href
        selector               = self.cssContextDict["mainReply_userHref"]
        ret,curText            = await self.pyteerEx.getElementHref(elementHandle,selector)
        replyInfo.userHref     = GrapReplyInfo.dealStr(curText )
        
        #user_name
        ret,curText            = await self.grabMainUserName(page,elementHandle)
        replyInfo.userName     = GrapReplyInfo.dealStr(curText )
        
        #time
        selector               = self.cssContextDict["mainReply_time"]
        ret,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
        curText                = GrapReplyInfo.dealStr(curText )
        replyInfo.publishTime   = curText + ":00"
        if ret != RetVal.Suc.value:
            selector               = self.cssContextDict["mainReply_time1"]
            ret,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
            curText                = GrapReplyInfo.dealStr(curText )
            replyInfo.publishTime   = curText + ":00"
        
        #floor
        selector               = self.cssContextDict["mainReply_floor"]
        ret,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
        replyInfo.main_floor   = GrapReplyInfo.dealStr(curText )
        
        
        #text
        selector               =  self.cssContextDict["mainReply_text"]
        ret,curText            = await self.pyteerEx.getElementContext(elementHandle,selector)
        curText                = GrapReplyInfo.dealStr(curText )
        ret, imgBuf            = await self.grabAllImage(page,elementHandle)
        if ret  == RetVal.Suc.value:
            curText            += self.getImgStrings(imgBuf)
        replyInfo.text         = curText
        
        #datapid
        selector               = self.cssContextDict["mainReply_pid"]
        ret,curText            = await self.pyteerEx.getElementId(elementHandle,selector)
        replyInfo.pid          = self.getMainPid(curText ,self.mainPidSplit)

        
        replyInfo.isMain    = 1
        replyInfo.href      = strUrl
        replyInfo.pageUrl   = self.getPageUrl(strUrl)
        ret = RetVal.Suc.value

        self.printLogInfo("CrawlerTiebaSub->grabMainReplyInfo() : exit")

        return ret,replyInfo

    #--------------------------------------------------------------------------------------
    #
    async def  grabAllImage(self,page,objElement):
        
        #self.printLogInfo("CrawlerTiebaSub->grabAllImage() : enter")

        ret     =  RetVal.Fail.value
        imgBuf  = []
        selector = self.cssContextDict["reply_image"]

        ret ,imgBuf=   await  self.pyteerEx.getElementAllProDef(page,objElement,"src",selector)

        #self.printLogInfo("CrawlerTiebaSub->grabAllImage() : exit")

        return ret,imgBuf


    #get sid from data-field
    async def  grabMainUserName(self,page,element):  

        #self.printLogInfo("CrawlerTiebaSub->grabMainUserName() : enter")

        ret     = RetVal.Fail.value
        strUserName = ""
        key     = "un"
        proName = "data-field"
        selector = self.cssContextDict["mainReply_userName"]
              
        ret1,dataJson = await self.pyteerEx.getElementProDef(page,element,proName,selector)
        if ret1 == RetVal.Suc.value:
            dataDict = JsonEx.loads(dataJson)

            if dataDict is not None:
                if key in dataDict.keys():
                    strUserName = dataDict[key]
                
                ret = RetVal.Suc.value
        
        #self.printLogInfo("CrawlerTiebaSub->grabMainUserName() : exit")

        return ret,strUserName

    #--------------------------------------------------------------------------------------
    #get sid from data-field
    async def  grabSubSpid(self,page,element):  

        #self.printLogInfo("CrawlerTiebaSub->grabSubSpid() : enter")

        ret     = RetVal.Fail.value
        strSpid = ""
        strUserName = ""
        key     = "spid"
        key1    = "user_name"
        proName = "data-field"
              
        ret1,dataJson = await self.pyteerEx.getElementProDef(page,element,proName)
        if ret1 == RetVal.Suc.value:
            dataDict = JsonEx.loads(dataJson)

            if dataDict is not None:
                if key in dataDict.keys():
                    strSpid = dataDict[key]
                if key1 in dataDict.keys():
                    strUserName = dataDict[key1]
                ret = RetVal.Suc.value
        
        #self.printLogInfo("CrawlerTiebaSub->grabSubSpid() : exit")

        return ret,[strSpid,strUserName]
    #--------------------------------------------------------------------------------------
    #get sub repaly                                                                                                     
    async def  grabSubReplyInfo(self,page,element,strUrl,strPid):
        
        self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfo() : enter")

        ret      = RetVal.Fail.value
        ret1     = 1
        replyBuf = [  ]
        selector     = self.cssContextDict["subReply"]
        selectorHref = self.cssContextDict["subReply_userHref"]

        ret1,elementList = await self.pyteerEx.getElementAll(element,selector)
        for item in  elementList:

            ret1,strSpidBuf   = await self.grabSubSpid(page,item)
            strSpid           = GrapReplyInfo.dealStr(strSpidBuf[0] )
            strUsername       = GrapReplyInfo.dealStr(strSpidBuf[1] )
            
            ret1,strUserHref  = await self.pyteerEx.getElementHref(item,selectorHref)
            
            ret,replyInfo = await self.grabSubReplyInfoItem(page,item)
            
            if ret == RetVal.Suc.value:
              replyInfo.href     = strUrl  
              replyInfo.pageUrl  = self.getPageUrl(strUrl)
              replyInfo.sid      = strSpid
              replyInfo.pid      = strPid
              replyInfo.userName = strUsername
              replyInfo.userHref = GrapReplyInfo.dealStr(strUserHref )
              replyBuf.append(replyInfo ) 
            
        if len(replyBuf) > 0:
            ret = RetVal.Suc.value
        
        self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfo() : exit")

        return  ret,replyBuf
    
    #--------------------------------------------------------------------------------------
    #get sub repaly                                                                                                     
    async def  grabSubReplyInfo_new(self,page,element,strUrl,strPid,grap_data_dict,crawlerInfo):
        
        self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfo() : enter")

        ret      = RetVal.Fail.value
        ret1     = 1
        
        replyBuf = [  ]
        selector     = self.cssContextDict["subReply"]
        selectorTime = self.cssContextDict["subReply_time"]

        ret1,elementList = await self.pyteerEx.getElementAll(element,selector)
        itemCount = 0
        for item in  elementList:
            itemCount += 0
            replyInfo = GrapReplyInfo()

            ret1,strSpidBuf   = await self.grabSubSpid(page,item)
            strSpid             = GrapReplyInfo.dealStr(strSpidBuf[0] )
            replyInfo.userName  = GrapReplyInfo.dealStr(strSpidBuf[1] )
            
            #--get time
            ret,curText       = await self.pyteerEx.getElementContext(item,selectorTime)
            strTime           = GrapReplyInfo.dealStr(curText )
            strTime           = strTime + ":00"
            replyInfo.publishTime = strTime

            # spid is empty
            if not strSpid:
                self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfo_new() : spid is empty,url={},pid={},spid={}".format(strUrl,strPid,strSpid))
                continue

            ret1,replyInfo_last = grap_data_dict.isExistKeyEx(strUrl,strPid,strSpid,strTime )
            if ret1 == 2: #same
                continue
            
            if ret1 == 0: #not exist
                #url
                selector      = self.cssContextDict["subReply_userHref"]
                ret1,curText  = await self.pyteerEx.getElementHref(item,selector)
                replyInfo.userHref = GrapReplyInfo.dealStr(curText )

                #nick_name
                selector               = self.cssContextDict["subReply_nickname"]
                ret,curText            = await self.pyteerEx.getElementContext(item,selector)
                replyInfo.publisher     = GrapReplyInfo.dealStr(curText )
            else:   #存在,则复制
                replyInfo.userHref     = replyInfo_last.userHref
                replyInfo.publisher     = replyInfo_last.publisher

            #context
            selector               = self.cssContextDict["subReply_text"]
            ret1,curText           = await self.pyteerEx.getElementContext(item,selector)
            replyInfo.text         = GrapReplyInfo.dealStr(curText )

            #save
            replyInfo.href     = strUrl  
            replyInfo.pageUrl  = self.getPageUrl(strUrl)
            replyInfo.sid      = strSpid
            replyInfo.pid      = strPid

            crawlerInfo.p_curPageItemNo +=1
            replyInfo.contentId       = crawlerInfo.p_curPageItemNo
            replyInfo.parentContentId = crawlerInfo.p_parentPageItemNoSub
            replyInfo.copyAsCrawlerInfo(crawlerInfo )  

            replyBuf.append(replyInfo )
            
            #replyBuf3= []
            #replyInfo1 = replyInfo
            #replyInfo1.copyAsCrawlerInfo(crawlerInfo )
            #replyBuf3.append( replyInfo1)
            #ret3,strJson = JsonEx.makeSpiderJson(replyBuf3 )
            #if ret3 == 0:
            #    print("CrawlerTiebaSub: begin to call app")
            #    CommonTool.sendSocket(0,crawlerInfo.serverTaskId,strJson) 

        retCount = len(replyBuf)    
        if retCount > 0:
            ret = RetVal.Suc.value
        
        self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfo() : exit")

        return  ret,replyBuf
    
    


    #--------------------------------------------------------------------------------------
    #get sub repaly                                                                                                     
    async def  grabSubReplyInfoItem(self,page,element):
        
        self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfoItem() : enter")

        ret  = RetVal.Fail.value
        replyInfo = GrapReplyInfo()

        #nick_name
        selector               = self.cssContextDict["subReply_nickname"]
        ret,curText            = await self.pyteerEx.getElementContext(element,selector)
        replyInfo.publisher     = GrapReplyInfo.dealStr(curText )

        #time
        selector               = self.cssContextDict["subReply_time"]
        ret,curText            = await self.pyteerEx.getElementContext(element,selector)
        curText                = GrapReplyInfo.dealStr(curText )
        replyInfo.publishTime   = curText + ":00"

        #text
        selector               = self.cssContextDict["subReply_text"]
        ret,curText            = await self.pyteerEx.getElementContext(element,selector)
        replyInfo.text         = GrapReplyInfo.dealStr(curText )
        
        ret = RetVal.Suc.value
        
        self.printLogInfo("CrawlerTiebaSub->grabSubReplyInfoItem() : exit")
        return ret,replyInfo
    
    