#def.py
import enum
#-----------------------------------------------------------
#use    : g = RetVal.Suc  g.name   g.value
#compare: if g == RetVal.Suc
#---返回值                       #-------ret返回值:
RetVal     = enum.Enum('RetVal',[ ('Suc',0),         #成功
                                  ('SucExit',60),    #成功退出
                                  #---失败
                                  ("Fail",1),        #失败
                                  ("FailRepeat",2),  #失败重试
                                  ("FailExit",3),    #失败退出
                                  ("FailExitNotFindKeyword",4),#失败退出,由于文本中没有找到关键字
                                  ("FailExitAsNovel",5),       #失败退出,由于找到连载的小说
                                  ("FailExitCountLimit",6),    #失败退出,由于达到数量上限
                                  #----异常
                                  ('ExceptElement',20),
                                  ('ExceptTimeout',21),
                                  ('ExceptPageError',22 ),
                                  ('ExceptNetError',23),
                                  ('ExceptBrowser',23),
                                  ('ExceptPyppeteer',24),
                                  #--------------------ifFinish的返回值
                                  ('GrapSucRepeat',0),  #本次抓取成功,继续下次的翻页或滚动抓取
                                  ('GrapSuc',1),        #抓取成功，退出
                                  ('GrapFailRepeat',2), #抓取失败,继续抓取
                                  ('GrapFailExit',3),   #抓取失败,退出
                                  ('GrapExitNotFindKeyword',4), #抓取退出，由于文本中没有找到关键字
                                  ('GrapExitAsNovel',5), #抓取退出，由于找到小说
                                  ('GrapExitCountLimit',6),#抓取数量达到上限
                                   
                                 ])
#--------------------------------------------
#---logging level
LogLevel   = enum.Enum('LogLevel',[('Debug',1),("Normal",2),("Fail",3),("Exception",4)])

#---抓取类型
GrapTypeEm = enum.Enum('GrapTypeEm',[('Compoundword',1),("Url",2),("User",3)])
#---
GrapCollectEm = enum.Enum('GrapCollectEm',[('GetPageNot',0),("GetPageHtml",1),("GetPageText",2),("GetPageFloor",3)])
#---网站类型
GrapSiteEm = enum.Enum('GrapSiteEm',[('Baidu_tieba',1),("Baidu_zhidao",2),("Weibo",3),
("Wukong",4),("Toutiao",5),("Weixin_sogou",6),("Zhihu",7),("Tianya",10),("Sogou_wenwen",11),("So_wenda",12),("Sina_iask",13),("Baidu",40)])
#---浏览网页的方式
GrapScrollEm = enum.Enum('GrapScrollEm',[('Page',0),("VScroll",1)])
#---抓取类型对应的调用函数
GrapTypeFuncEm = enum.Enum('GrapTypeFuncEm',[('KeyMain',0),("KeySub",1),("DefUrl",2),("DefUser",3)])


class ConfigParaInfoTest:
    def __init__(self):
        self.browserHeadless = False  #浏览器的headless模式
        self.subThreadNum    = 1  #子抓取时，线程个数
        mainBase = "fdfdfdf"
        mainSub  = "ioppp"
        self.picDict = {'name1':mainBase +"kk1",
                        'name2':mainSub  + "kk2",

                       }
    def test(self):
        kk1 = self.picDict["name1"]
        kk2 = self.picDict["name2"]
        print(kk1)
        print(kk2)
#---------------------------------------------
#class  参数配置
class ConfigParaInfo:
    def __init__(self):
        self.browserHeadless = False  #浏览器的headless模式
        self.subThreadNum    = 1  #子抓取时，线程个数

#---------------------------------------------
#class  CrawlerInfo:
class  SpiderTaskInfo:
    def __init__(self):
        self.serverTaskId = 0  #任务id
        self.origin       = 0
        self.keyword      = ""
        self.compoundword = ""
        self.maxPages     = 0
        self.targetUrl    = ""
        self.hotWord      = 0  
        self.snapshot     = 0
        self.collect      = 0  #=0:不获取内容;=1:获取整页 html;=2:获取整页 text;=3:获取按楼层的内容
        self.analogClick  = 0
        self.analogBrowse = 0

class  CrawlerTaskInfo:
    def __init__(self,grapType,siteType,url,keyword,compoundword,grapData=None):
        #抓取类型
        self.grap_type = grapType
        #网站类型
        self.site_type = siteType

        #网址
        self.url       = url
        #关键字
        self.keyword   = keyword
        #
        self.compoundword = compoundword
        #附加数据
        self.grap_data = grapData
        #附加数据map
        self.grap_mapData = None
        #
        self.serverTaskId  = 0
        self.maxPages      = 0
        self.targetUrl     = ""
        self.hotWord       = 0
        self.snapshot      = 0
        self.collect       = 0
        self.analogClick   = 0
        self.analogBrowse  = 0
    
    def copyAsSpider(self,spiderTaskInfo):
        self.serverTaskId  = spiderTaskInfo.serverTaskId
        self.keyword       = spiderTaskInfo.keyword
        self.maxPages      = spiderTaskInfo.maxPages
        self.targetUrl     = spiderTaskInfo.targetUrl
        self.hotWord       = spiderTaskInfo.hotWord
        self.snapshot      = spiderTaskInfo.snapshot
        self.collect       = spiderTaskInfo.collect
        self.analogClick   = spiderTaskInfo.analogClick
        self.analogBrowse  = spiderTaskInfo.analogBrowse
        

class  CrawlerInfo:
    def __init__(self,url,keyword,compoundword,is_main,grap_data=[],is_finish=False):
        self.is_main   = 0         #=0:主抓取 =1:子抓取
        self.is_finish = is_finish
        self.url       = url
        self.keyword   = keyword
        self.compoundword = compoundword
        self.grap_data = grap_data

        self.serverTaskId  = 0
        self.maxPages      = 0
        self.targetUrl     = ""
        self.hotWord       = 0
        self.snapshot      = 0
        self.collect       = 0
        self.analogClick   = 0
        self.analogBrowse  = 0
                    
        #
        self.pageNo        = 0   #
        self.itemNo        = 0
        self.main_title    = ""
        self.main_text     = ""
        self.main_url      = ""
        self.hotWords      = ""

        #para
        self.pid           = ""
        #------------------------------------
        self.p_curPageItemNo = 0
        self.p_parentPageItemNo = 0

        self.p_prePageItemNo = 0
        self.p_parentPageItemNoSub = 0
        

        self.p_curPageSubItemNo = 0
        self.curPageNo          = 0  #子抓取中，当前页
        self.finish_status      = 0
        self.vscroll_grap_count = 0  #滚动方式中，已抓取的项的数量
        #---
        self.grap_buf           = None #保存抓取的数据
        self.keywordInGrapBufCount = 0 #在抓取的数据中找到关键字的次数
        #---判断抓取数据为小说的结构
        self.novelInfo          = None


    def copyAsSpider(self,crawlerTaskInfo):
        self.serverTaskId  = crawlerTaskInfo.serverTaskId
        self.keyword      = crawlerTaskInfo.keyword
        self.maxPages      = crawlerTaskInfo.maxPages
        self.targetUrl     = crawlerTaskInfo.targetUrl
        self.hotWord       = crawlerTaskInfo.hotWord
        self.snapshot      = crawlerTaskInfo.snapshot
        self.collect       = crawlerTaskInfo.collect
        self.analogClick   = crawlerTaskInfo.analogClick
        self.analogBrowse  = crawlerTaskInfo.analogBrowse

    def copyAsTopItemInfo(self,grapTopItemInfo):
        self.serverTaskId = grapTopItemInfo.serverTaskId
        self.pageNo       = grapTopItemInfo.pageNo
        self.itemNo       = grapTopItemInfo.itemNo
        #self.main_title   = grapTopItemInfo.main_title
        self.main_text    = grapTopItemInfo.main_text
        self.main_url     = grapTopItemInfo.main_url
        self.hotWords     = grapTopItemInfo.hotWords

class compoundwordInfo:
    def __init__(self):
       self.site_search      = ''
       self.site_sub_search  = ''
       self.main_compoundword     = ''
       self.sub_compoundword      = ''


class GrapTopItemInfo:
    def __init__(self,url,keyword,compoundword,is_finish=False):
       self.is_finish        = is_finish
       self.url              = url
       self.keyword          = keyword
       self.compoundword     = compoundword
       self.main_url         = ""
       self.main_title       = ""
       self.main_text        = ""
       #
       self.serverTaskId     = 0
       self.pageNo           = 0
       self.itemNo           = 0
       self.snapshots        = ""
       self.hotWords         = ""  

#------------------------------------------------------------------------
#----检查小说
class NovelInfo:
    def __init__(self,terminateCount,maxWordCount,keyword):
        self.matchCount     = 0                #连续匹配次数,连续匹配则递增，否则为0
        self.terminateCount = terminateCount   #终止抓取的次数
        self.maxWordCount   = maxWordCount     #最大字数
        self.keyword        = keyword.upper()          #关键词
    #--检查是否需要终止抓取
    def checkIsTerminate(self,strData):
        
        ret        = RetVal.Suc.value
        wordCount  = len(strData)
        strData    = strData.upper()
        
        if wordCount > self.maxWordCount:
            if strData.find(self.keyword) == -1: #找不到
                self.matchCount += 1
            else:
                self.matchCount =0
        else:
            self.matchCount =0
        #---

        if self.matchCount >= self.terminateCount:
            ret = RetVal.FailExitAsNovel.value
        
        return ret

#-------------------------------------------------------------------------
#----
class GrapReplyInfo:
    def __init__(self):
        self.serverTaskId   = 0
        self.pageNo         = 0
        self.ranking        = 0
        
        self.contentId       = 0
        self.parentContentId = 0  

        self.snapshots       = ""   #快照
        self.href            = ""   #
        self.pageUrl         = ""   #页地址
        self.main_title      = ""   
        self.text            = ""   #回帖内容

        self.publisher       = ""
        self.publishTime     = "1970-01-01 00:00:00"
        

        self.reads           = 0   #阅读数
        self.forwards        = 0   #转发数
        self.stars           = 0   #点赞数
        self.comments        = 0   #评论数
        self.hotWords        = ""  #热搜词
        self.locateSymbol    = ""  #标识

        #-------------------------------------------------------------------------
        self.pid            = ""   #主回复id
        self.sid            = ""   #子回复id


        self.isMain         = 0    #是否是主回复
        self.userName       = ""   #用户名
        self.userHref       = ""   #用户主页
        
        self.main_floor     = ""   #百度贴吧，主回复楼层
        
        self.support        = 0   #支持的评论数
        self.unsupport      = 0  #不支持的评论数

        self.main_href      = ""
        self.main_text      = ""

        #
        
    #----------------------------------------------------
    def  copyfrom(self,isMain,replyInfo):
        self.isMain         = isMain    #是否是主回复
        self.userName       = replyInfo.userName   #用户名
        self.userHref       = replyInfo.userHref   #用户主页
        self.publisher       = replyInfo.publisher   #昵称
        self.publishTime     = replyInfo.publishTime   #
        self.main_floor     = replyInfo.main_floor   #百度贴吧，主回复楼层
        self.href           = replyInfo.href   #
        self.text           = replyInfo.text   #回帖内容
        self.pid            = replyInfo.pid   #主回复id
        self.sid            = replyInfo.sid   #子回复id
        self.support        = replyInfo.support   #支持的评论数
        self.unsupport      = replyInfo.unsupport   #不支持的评论数
    #------------------------------------------------------------------
    def  copyAsCrawlerInfo(self,crawlerInfo):
        self.serverTaskId  = crawlerInfo.serverTaskId
        self.pageNo        = crawlerInfo.pageNo
        self.ranking       = crawlerInfo.itemNo
        self.main_href     = crawlerInfo.main_url
        #self.href          = crawlerInfo.url
        #self.main_title    = crawlerInfo.main_title
        self.hotWords      = crawlerInfo.hotWords
    #------------------------------------------------------------------
    def copyAsGrapTopItemInfo(self,grapTopItemInfo):
        self.serverTaskId  = grapTopItemInfo.serverTaskId
        self.pageNo        = grapTopItemInfo.pageNo
        self.ranking       = grapTopItemInfo.itemNo
        self.snapshots     = grapTopItemInfo.snapshots
        self.hotWords      = grapTopItemInfo.hotWords

        self.href          = grapTopItemInfo.url
        self.text          = grapTopItemInfo.main_text
        self.main_title    = grapTopItemInfo.main_title 
        
    #-----------------------------------------------------------------
    @staticmethod
    def getLocateSymbolStr(pid,sid):
        return "{}:{}".format(pid,sid)

    #-----------------------------------------------
    #--字符串处理
    @staticmethod
    def dealStr(picHref):

        curStr = ""
        if len(picHref) > 0:
            curStr = picHref.strip()


        return curStr   
    #--------------------------------------------
    #--获取评论中图片的封装格式字符串
    @staticmethod
    def getPicWrapStr(picHref):

        strHref ="[eims_pic_href:{}]\r".format(picHref.strip())
        return strHref

    @staticmethod
    def getTextWrapStr(curText):
       
       strText = "{}\r".format(curText.strip())
       return strText

        
    #def __iter__(self):
    #    return self