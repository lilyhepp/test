#-------baidu_sub.py

import sys,os
import asyncio
from pyppeteer import launch

sys.path.append("..")

from struct_def                  import *
from crawlers.search_base_sites  import *
from pyteerex.pyppeteer_ex       import *
from common.tools                import *

class   BaiduSub(CrawlerSiteScrollSub):

    def __init__(self,crawlerType,queueDict,configParaInfo,index):

        super().__init__(crawlerType,queueDict,configParaInfo)
        
        #------------------------------------------------------
        #----配置参数
        
        #--滚动条滚动的步长
        self.autoScrollStep            = 80
        
        
        #---------------------------------------------------------
        #----other

        #--pid,sid,
        
        self.lauchKwargsAgent = ['--disable-infobars','--proxy-server=115.28.253.245:9020','--no-sandbox', f'--window-size={1500},{800}']
        self.lauchKwargs = ['--disable-infobars','--no-sandbox', f'--window-size={1500},{800}']
        self.cssPageBtnDict = {
                               'firstPageBtn':"div.pb_footer > div.p_thread.thread_theme_7 >div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager >a:nth-child(1)",
                               'prePageBtn':"",
                               #'curPageText':"div.wrap2 > div#head > div.l_container>div.content.clearfix >div.pb_footer>div.p_thread.thread_theme_7>div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager>span.tP",
                               'curPageText':"div.l_container>div.content.clearfix >div.pb_footer>div.p_thread.thread_theme_7>div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager>span.tP",
                               'curPageBtn':"div.wrap2 > div.s_container.clearfix > div.pager.pager-search > span.cur",
                               #'nextPageBtn':'''div.wrap2 > div.search_bright.clearfix >div.>div.content.clearfix >div.pb_footer > div.p_thread.thread_theme_7 >div.l_thread_info>div.l_posts_num>div.l_pager.pager_theme_5.pb_list_pager  ''',
                               'nextPageBtn':"div.pb_footer > div.p_thread.thread_theme_7 >div.l_thread_info>ul.l_posts_num>li.l_pager.pager_theme_5.pb_list_pager >a:nth-last-child(2)",
                               'bottomAllPageNum':"div.pb_footer > div.p_thread.thread_theme_7 > div.l_thread_info > ul.l_posts_num > li.l_reply_num > span:nth-last-child(1)"
                               #'bottomAllPageNum':"div.pb_footer > div.p_thread.thread_theme_7 > div.l_thread_info > ul.l_posts_num > li.l_reply_num >span.red "
                               }

        self.paraClickNextPage = {
                                  'timeoutMs':40000,
                                  'waitUntil':["load","domcontentloaded"] 
                                 }
        
        #sub
        self.cssContextDict    = {
                                  'mainTitle':"div.left_section > div#j_core_title_wrap > div.core_title.core_title_theme_bright>h1.core_title_txt ",
                                  'mainReply':"div.p_postlist > div.l_post.j_l_post.l_post_bright ",
                                  #'mainReply_pid':"div.d_post_content_main >div.p_content.p_content > cc > div.d_post_content.j_d_post_content.clearfix",
                                  'mainReply_pid':"div.d_post_content_main >div.p_content > cc > div.d_post_content.j_d_post_content",
                                  'mainReply_nickname':"div.d_author > ul.p_author > li.d_name > a.p_author_name.j_user_card",
                                  'mainReply_userHref':"div.d_author > ul.p_author > li.d_name > a.p_author_name.j_user_card",
                                  'mainReply_userName':"div.d_author > ul.p_author > li.d_name > a.p_author_name.j_user_card",
                                  'mainReply_time':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > ul.p_tail ",
                                  'mainReply_time1':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > div.post-tail-wrap >span:nth-last-child(1)",
                                  'mainReply_floor':"div.d_post_content_main > div.core_reply.j_lzl_wrapper > div.core_reply_tail > div.post-tail-wrap >span:nth-last-child(2)",
                                  
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
                                 'pageLoginExit':"body.skin_normal>div#passport-login-pop > div.tang-foreground > div.tang-title.tang-title-dragable>div.buttons>a.close-btn "
                                 }
        
        #log
        logpath = "baidu/sub/" + str(index) 
        self.log_inits(logpath,2,2,logging.INFO)

    #--------------------------------------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------
    
    async def dealMainScrollBefor(self,page,crawlerInfo):    
        newUrl      = page.target.url
        newUrl      = GrapReplyInfo.dealStr(newUrl)
        
        if newUrl:
            replyInfo = GrapReplyInfo()
            replyInfo.copyAsCrawlerInfo(crawlerInfo )
            replyInfo.href       = newUrl
            replyInfo.pageUrl    = newUrl
            replyInfo.text       = crawlerInfo.main_text
            
            replyInfo.contentId       = 1
            replyInfo.parentContentId = 0
            
            replyBuf = []
            replyBuf.append(replyInfo)
            self.app_commitBuf(replyBuf)
            
            self.printGrapInfo("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            self.printGrapInfo("main_href_new={}".format(newUrl))
        
        return RetVal.SucExit.value
    
    #--------------------------------------------------------------------------------------
    async def  waitforPageLoad(self,page):
        return RetVal.Suc.value

    #--------------------------------------------------------------------------------------
    #do crawler a web page
    async def  dealSubCrawlerAsFloor(self,page,crawlerInfo,index):
        ret = RetVal.Suc.value

        return ret,[]


     
    
    

    