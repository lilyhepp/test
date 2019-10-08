#deal_crawler.py
import sys,os
import threading
import time

import threading
import asyncio
from   pyppeteer import launch

sys.path.append("..")
sys.path.append(".")

from   g_def                      import *
from   struct_def                 import *
from   crawlers.baidu_tieba_main  import *
from   crawlers.baidu_zhidao_main import *
from   crawlers.baidu_main        import *
from   crawlers.weibo_main        import *
from   crawlers.toutiao_main      import * 
from   crawlers.wukong_main       import * 
from   crawlers.zhihu_main        import * 
from   crawlers.tianya_main       import *
from   crawlers.weixin_sogou_main import *  
from   crawlers.sina_iask_main    import * 
from   crawlers.so_wenda_main     import *
from   crawlers.sogou_wenwen_main import * 

#-------------------------------------------------------------------------------------------
#处理抓取任务,新增网站要在这添加处理函数
def  deal_Crawler_sites(spiderTaskInfo):
   
   #spiderTaskInfo.origin = 1
   """
   if (spiderTaskInfo.origin > 2)  :
       CommonTool.app_commitTask(spiderTaskInfo.serverTaskId)
       return    
   """
   crawlerTaskInfo = get_crawler_task(spiderTaskInfo)
   
   #---判断keyword和com是否相同,加"""
   if crawlerTaskInfo.compoundword == crawlerTaskInfo.keyword  and crawlerTaskInfo.site_type != GrapSiteEm.Sina_iask:
       crawlerTaskInfo.compoundword = '"{}"'.format(crawlerTaskInfo.keyword)
   

   configParaInfo  = ConfigParaInfo()    
   #--贴吧
   if crawlerTaskInfo.site_type ==  GrapSiteEm.Baidu_tieba:
        deal_Crawler_sub_site_tieba(crawlerTaskInfo,configParaInfo)
      
   #--知道
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Baidu_zhidao:
        deal_Crawler_sub_sites_zhidao(crawlerTaskInfo,configParaInfo)
   #--baidu
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Baidu:
        deal_Crawler_sub_sites_baidu(crawlerTaskInfo,configParaInfo) 
   #--weibo
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Weibo:
        deal_Crawler_sub_sites_weibo(crawlerTaskInfo,configParaInfo)
   #--wukong
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Wukong:
        deal_Crawler_sub_sites_wukong(crawlerTaskInfo,configParaInfo)  
   #--toutiao
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Toutiao:
        deal_Crawler_sub_sites_toutiao(crawlerTaskInfo,configParaInfo)
   #--zhihu
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Zhihu:
        deal_Crawler_sub_sites_zhihu(crawlerTaskInfo,configParaInfo)
   #--Tianya
   elif crawlerTaskInfo.site_type ==  GrapSiteEm.Tianya:
        deal_Crawler_sub_sites_tianya(crawlerTaskInfo,configParaInfo)
   #--weixinsogou
   elif crawlerTaskInfo.site_type == GrapSiteEm.Weixin_sogou:
        deal_Crawler_sub_sites_WeixinSogou(crawlerTaskInfo,configParaInfo)
   #--360问答
   elif crawlerTaskInfo.site_type == GrapSiteEm.So_wenda:
        deal_Crawler_sub_sites_SoWenda(crawlerTaskInfo,configParaInfo)
   #--新浪爱问
   elif crawlerTaskInfo.site_type == GrapSiteEm.Sina_iask:
        deal_Crawler_sub_sites_SinaIask(crawlerTaskInfo,configParaInfo)
    #--搜狗问问
   elif crawlerTaskInfo.site_type == GrapSiteEm.Sogou_wenwen:
        deal_Crawler_sub_sites_Sogouwenwen(crawlerTaskInfo,configParaInfo)
#-------------------------------------------------------------------------------------------
#
def  get_crawler_task(spiderTaskInfo):
       
   spiderInfo = spiderTaskInfo
   grap_data_list   = None 

   grap_type   = GrapTypeEm.Compoundword
   #grap_type   = GrapTypeEm.Url
   site_type,site_url   = get_site_type(spiderInfo.origin )
   #site_url    = "https://weibo.com/5697427068/I5fHupFoW?refer_flag=1001030103_&type=comment#_rnd1567595429770"
   #site_url = "https://tieba.baidu.com/p/5129227030?pid=107393090579&cid=0&red_tag=2763781756#107393090579"
   crawlerTaskInfo = CrawlerTaskInfo(grap_type,site_type,site_url,spiderInfo.keyword,spiderInfo.compoundword,grap_data_list)
   crawlerTaskInfo.copyAsSpider(spiderTaskInfo )
   
   return crawlerTaskInfo

#-------------------------------------------------------------------------------------------
#
def  get_site_type(siteTypeVal ):
   
   siteType = GrapSiteEm.Baidu_tieba.value
   siteUrl  = ""
   
   print("siteTypeVal=",siteTypeVal)

   if siteTypeVal == 1:
       siteType = GrapSiteEm.Baidu_tieba
       siteUrl  = "https://tieba.baidu.com/index.html"
   elif siteTypeVal == 2:
       siteType = GrapSiteEm.Baidu_zhidao
       siteUrl  = "https://zhidao.baidu.com"
   elif siteTypeVal == 3:
       siteType = GrapSiteEm.Weibo
       siteUrl  = "https://www.weibo.com"
   #悟空
   elif siteTypeVal == 4:
       siteType = GrapSiteEm.Wukong
       siteUrl  = "https://www.wukong.com"
   #头条
   elif siteTypeVal == 5:
       siteType = GrapSiteEm.Toutiao
       siteUrl  = "https://www.toutiao.com/"
   #知乎
   elif siteTypeVal == 7:
       siteType = GrapSiteEm.Zhihu
       siteUrl  = "https://www.zhihu.com/search?type=content&q="
   #搜狗微信
   elif siteTypeVal == 6:
       siteType = GrapSiteEm.Weixin_sogou
       siteUrl  = "https://weixin.sogou.com/"   
   #天涯
   elif siteTypeVal == 10:
       siteType = GrapSiteEm.Tianya
       siteUrl  = "http://search.tianya.cn" 
    #搜狗问问
   elif siteTypeVal == 11:
       siteType = GrapSiteEm.Sogou_wenwen
       siteUrl  = "https://wenwen.sogou.com/"   
   #360问答
   elif siteTypeVal == 12:
       siteType = GrapSiteEm.So_wenda
       siteUrl  = "https://wenda.so.com" 
   #新浪爱问
   elif siteTypeVal == 13:
       siteType = GrapSiteEm.Sina_iask
       siteUrl  = "https://iask.sina.com.cn"   
   elif siteTypeVal == 40:
       siteType = GrapSiteEm.Baidu
       siteUrl  = "https://www.baidu.com"
   

   return siteType,siteUrl

#-------------------------------------------------------------------------------------------
#--百度贴吧
def deal_Crawler_sub_site_tieba(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_site_tieba():enter")

   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerTieba = CrawlerTieba(coNum)
   crawlerTieba.crawlerScroll(loop,crawlerInfo,configParaInfo)
    
#-------------------------------------------------------------------------------------------   
#  百度知道
def deal_Crawler_sub_sites_zhidao(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_zhidao():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerZhidao = CrawlerZhidao(coNum)
   crawlerZhidao.crawlerScroll(loop,crawlerInfo,configParaInfo)

#-------------------------------------------------------------------------------------------
# 百度
def deal_Crawler_sub_sites_baidu(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_baidu():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerBaidu = CrawlerBaidu(coNum)
   crawlerBaidu.crawlerScroll(loop,crawlerInfo,configParaInfo)

#-------------------------------------------------------------------------------------------
# 微博
def deal_Crawler_sub_sites_weibo(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_weibo():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerWeibo = CrawlerWeibo(coNum)
   crawlerWeibo.crawlerScroll(loop,crawlerInfo,configParaInfo)    

#-------------------------------------------------------------------------------------------
# 悟空
def deal_Crawler_sub_sites_wukong(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_wukong():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()

   crawlerWukong = CrawlerWukong(coNum)

   crawlerWukong.crawlerScroll(loop,crawlerInfo,configParaInfo) 

#-------------------------------------------------------------------------------------------
# 头条
def deal_Crawler_sub_sites_toutiao(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_toutiao():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   
   crawlerToutiao = CrawlerToutiao(coNum)
   
   crawlerToutiao.crawlerScroll(loop,crawlerInfo,configParaInfo)     

#-------------------------------------------------------------------------------------------
# 知乎
def deal_Crawler_sub_sites_zhihu(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_zhihu():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerZhihu = CrawlerZhihu(coNum)
   crawlerZhihu.crawlerScroll(loop,crawlerInfo,configParaInfo)

#-------------------------------------------------------------------------------------------
# 微信搜狗
def deal_Crawler_sub_sites_WeixinSogou(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_WeixinSogou():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   
   crawlerWeixinSogou = CrawlerWeixinSogou(coNum)
   
   crawlerWeixinSogou.crawlerScroll(loop,crawlerInfo,configParaInfo) 
     
#-------------------------------------------------------------------------------------------
# 天涯
def deal_Crawler_sub_sites_tianya(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_tianya():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerTianya = CrawlerTianya(coNum)
   crawlerTianya.crawlerScroll(loop,crawlerInfo,configParaInfo)  

#-------------------------------------------------------------------------------------------
# 新浪爱问
def deal_Crawler_sub_sites_SinaIask(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_SinaIask():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerSinaIask = CrawlerSinaIask(coNum)
   crawlerSinaIask.crawlerScroll(loop,crawlerInfo,configParaInfo)

#-------------------------------------------------------------------------------------------
# 360问答
def deal_Crawler_sub_sites_SoWenda(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_SoWenda():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerSoWenda = CrawlerSoWenda(coNum)
   crawlerSoWenda.crawlerScroll(loop,crawlerInfo,configParaInfo)


   
#-------------------------------------------------------------------------------------------
# 搜狗问问
def deal_Crawler_sub_sites_Sogouwenwen(crawlerInfo,configParaInfo): 

   print(" deal_Crawler_sub_sites_SinaIask():enter")
   
   coNum = configParaInfo.subThreadNum
   loop  = asyncio.get_event_loop()
   crawlerSogouWenWen = CrawlerSogouWenWen(coNum)
   crawlerSogouWenWen.crawlerScroll(loop,crawlerInfo,configParaInfo)

